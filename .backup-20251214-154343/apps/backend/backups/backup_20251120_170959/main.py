#!/usr/bin/env python3
"""
APEX Backend API - FIXED VERSION
Working imports only - no intelligence.outreach module
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import json
import os
from typing import Optional, List, Dict
from dotenv import load_dotenv
from contextlib import contextmanager

# ✅ WORKING IMPORTS ONLY
from intelligence.engines.scoring.scoring_orchestrator import ScoringOrchestrator
from intelligence.hubspot_sync import HubSpotSync

# Load environment variables
load_dotenv()

# Database setup
DATABASE = "apex.db"

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize FastAPI
app = FastAPI(
    title="APEX Intelligence Platform",
    version="2.0",
    description="AI-Powered Sales Intelligence with MDCP/RSS Scoring"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    hubspot_id: Optional[str] = None

class EnrichmentRequest(BaseModel):
    depth: str = "quick"

# ==================== ROOT & HEALTH ====================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "APEX Intelligence Platform",
        "version": "2.0",
        "status": "operational",
        "features": ["MDCP/RSS Scoring", "Persona Classification", "HubSpot Integration"],
        "docs": "/docs",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()[0]
            return {
                "status": "healthy",
                "database": "connected",
                "contacts": count,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ==================== SCORING ENDPOINTS ====================

@app.post("/api/contacts/{contact_id}/score")
async def score_contact(contact_id: int, trigger: str = "manual"):
    """Score a contact using MDCP/RSS scoring + persona classification"""
    try:
        with get_db() as conn:
            orchestrator = ScoringOrchestrator(conn)
            result = orchestrator.score_contact(contact_id, trigger=trigger)
            
            if 'error' in result:
                raise HTTPException(status_code=404, detail=result['error'])
            
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/score/bulk")
async def score_contacts_bulk(contact_ids: List[int]):
    """Score multiple contacts at once"""
    try:
        with get_db() as conn:
            orchestrator = ScoringOrchestrator(conn)
            results = orchestrator.bulk_score(contact_ids)
            return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== CONTACT CRUD ====================

@app.get("/api/contacts")
async def list_contacts(
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "priority_score",
    order: str = "desc"
):
    """List all contacts with optional sorting"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            valid_sorts = ["priority_score", "mdcp_score", "rss_score", "created_at", "name"]
            if sort_by not in valid_sorts:
                sort_by = "priority_score"
            
            query = f"""
                SELECT * FROM contacts 
                ORDER BY {sort_by} {order.upper()}
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (limit, offset))
            contacts = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT COUNT(*) FROM contacts")
            total = cursor.fetchone()[0]
            
            return {
                "contacts": contacts,
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: int):
    """Get detailed contact information"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts")
async def create_contact(contact: ContactCreate):
    """Create a new contact and automatically score it"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO contacts (
                    name, email, phone, company, title, industry, 
                    hubspot_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact.name,
                contact.email,
                contact.phone,
                contact.company,
                contact.title,
                contact.industry,
                contact.hubspot_id,
                datetime.now().isoformat()
            ))
            conn.commit()
            contact_id = cursor.lastrowid
            
            # Automatically score the new contact
            orchestrator = ScoringOrchestrator(conn)
            scoring_result = orchestrator.score_contact(contact_id, trigger='import')
            
            return {
                "id": contact_id,
                "contact": contact.dict(),
                "scoring": scoring_result
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/contacts/{contact_id}")
async def update_contact(contact_id: int, contact: ContactCreate):
    """Update an existing contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE contacts SET
                    name = ?, email = ?, phone = ?, 
                    company = ?, title = ?, industry = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                contact.name,
                contact.email,
                contact.phone,
                contact.company,
                contact.title,
                contact.industry,
                datetime.now().isoformat(),
                contact_id
            ))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            # Re-score after update
            orchestrator = ScoringOrchestrator(conn)
            scoring_result = orchestrator.score_contact(contact_id, trigger='manual')
            
            return {
                "id": contact_id,
                "updated": True,
                "scoring": scoring_result
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ====================

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Total contacts
            cursor.execute("SELECT COUNT(*) FROM contacts")
            total_contacts = cursor.fetchone()[0]
            
            # Scored contacts
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE priority_score IS NOT NULL")
            scored_contacts = cursor.fetchone()[0]
            
            # Average scores
            cursor.execute("""
                SELECT 
                    AVG(priority_score) as avg_priority,
                    AVG(mdcp_score) as avg_mdcp,
                    AVG(rss_score) as avg_rss
                FROM contacts
                WHERE priority_score IS NOT NULL
            """)
            scores = dict(cursor.fetchone())
            
            # Persona distribution
            cursor.execute("""
                SELECT 
                    persona_tier,
                    persona_type,
                    COUNT(*) as count
                FROM contacts
                WHERE persona_tier IS NOT NULL
                GROUP BY persona_tier, persona_type
                ORDER BY count DESC
            """)
            personas = [dict(row) for row in cursor.fetchall()]
            
            return {
                "total_contacts": total_contacts,
                "scored_contacts": scored_contacts,
                "average_scores": {
                    "priority": round(scores.get('avg_priority') or 0, 2),
                    "mdcp": round(scores.get('avg_mdcp', 0), 2),
                    "rss": round(scores.get('avg_rss', 0), 2)
                },
                "personas": personas,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/personas")
async def get_persona_distribution():
    """Get detailed persona distribution"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    persona_tier,
                    persona_type,
                    COUNT(*) as count,
                    AVG(priority_score) as avg_priority,
                    AVG(mdcp_score) as avg_mdcp,
                    AVG(rss_score) as avg_rss
                FROM contacts
                WHERE persona_tier IS NOT NULL
                GROUP BY persona_tier, persona_type
                ORDER BY persona_tier, count DESC
            """)
            distribution = [dict(row) for row in cursor.fetchall()]
            return {"distribution": distribution}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== HUBSPOT INTEGRATION ====================

@app.post("/api/hubspot/import")
async def import_from_hubspot():
    """Import contacts from HubSpot and score them"""
    try:
        if not os.getenv('HUBSPOT_API_KEY'):
            raise HTTPException(status_code=400, detail="HubSpot API key not configured")
        
        hubspot = HubSpotSync()
        contacts = hubspot.import_contacts()
        
        with get_db() as conn:
            contact_ids = []
            cursor = conn.cursor()
            
            for contact_data in contacts:
                cursor.execute("""
                    INSERT INTO contacts (
                        name, email, phone, company, title, 
                        hubspot_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    contact_data.get('name'),
                    contact_data.get('email'),
                    contact_data.get('phone'),
                    contact_data.get('company'),
                    contact_data.get('title'),
                    contact_data.get('hubspot_id'),
                    datetime.now().isoformat()
                ))
                contact_ids.append(cursor.lastrowid)
            
            conn.commit()
            
            # Score all imported contacts
            orchestrator = ScoringOrchestrator(conn)
            results = orchestrator.score_after_import(contact_ids)
            
            return {
                "imported": len(contact_ids),
                "scored": len(results),
                "results": results
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("🚀 APEX Intelligence Platform")
    print("=" * 70)
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 70)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    
    