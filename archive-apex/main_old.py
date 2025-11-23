#!/usr/bin/env python3
"""
APEX Backend API - Complete Main Application
Unified Sales Intelligence Platform with all engines integrated
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import json
import asyncio
from typing import Optional, List, Dict
from dotenv import load_dotenv
import os
from contextlib import contextmanager

# Load environment variables
load_dotenv()

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Apex Sales Intelligence API",
    version="2.0.0",
    description="AI-Powered Sales Automation & Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# IMPORT AND REGISTER ROUTERS
# ============================================================================

# Import the outreach router
from api.routes.outreach import router as outreach_router
app.include_router(outreach_router)

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE = os.getenv('DATABASE_URL', './apex.db')

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize all database tables"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hubspot_id INTEGER UNIQUE,
                name TEXT NOT NULL,
                title TEXT,
                company TEXT,
                industry TEXT,
                email TEXT,
                phone TEXT,
                linkedin_url TEXT,
                
                -- Enrichment fields
                enriched BOOLEAN DEFAULT 0,
                enriched_at TIMESTAMP,
                enrichment_data JSON,
                
                -- Scoring fields
                tier INTEGER,
                persona_name TEXT,
                opportunity_score REAL,
                urgency_level TEXT,
                
                -- Intelligence fields
                relationship_data JSON,
                vertical_intelligence JSON,
                
                -- Outreach fields
                last_contacted TIMESTAMP,
                outreach_stage TEXT,
                conversion_probability REAL,
                
                -- Metadata
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Outreach history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                type TEXT NOT NULL, -- email, call, linkedin
                content JSON,
                sent_at TIMESTAMP,
                response TEXT,
                success BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
        """)
        
        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                metric_type TEXT,
                metric_value REAL,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
        """)
        
        # Companies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                industry TEXT,
                size TEXT,
                revenue TEXT,
                profile_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Database tables initialized")

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ContactCreate(BaseModel):
    """Model for creating a contact"""
    hubspot_id: Optional[int] = None
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None

class ContactResponse(BaseModel):
    """Model for contact response"""
    id: int
    name: str
    title: Optional[str]
    company: Optional[str]
    email: Optional[str]
    tier: Optional[int]
    persona_name: Optional[str]
    opportunity_score: Optional[float]
    enriched: bool

class EnrichmentRequest(BaseModel):
    """Model for enrichment request"""
    include_vertical: bool = True
    include_relationship: bool = True
    quick_mode: bool = False

# ============================================================================
# CORE API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Apex Sales Intelligence API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "contacts": "/api/contacts",
            "outreach": "/api/v1/outreach",
            "analytics": "/api/analytics"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            contact_count = cursor.fetchone()[0]
        
        return {
            "status": "healthy",
            "database": "connected",
            "contacts": contact_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# CONTACTS ENDPOINTS
# ============================================================================

@app.post("/api/contacts", response_model=ContactResponse)
async def create_contact(contact: ContactCreate):
    """Create a new contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (
                    hubspot_id, name, title, company, 
                    industry, email, phone, linkedin_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                contact.hubspot_id,
                contact.name,
                contact.title,
                contact.company,
                contact.industry,
                contact.email,
                contact.phone,
                contact.linkedin_url
            ))
            conn.commit()
            contact_id = cursor.lastrowid
            
            # Fetch and return the created contact
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            return ContactResponse(
                id=row['id'],
                name=row['name'],
                title=row['title'],
                company=row['company'],
                email=row['email'],
                tier=row['tier'],
                persona_name=row['persona_name'],
                opportunity_score=row['opportunity_score'],
                enriched=bool(row['enriched'])
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts")
async def list_contacts(limit: int = 20, offset: int = 0):
    """List all contacts with pagination"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM contacts 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            contacts = []
            for row in cursor.fetchall():
                contacts.append({
                    "id": row['id'],
                    "name": row['name'],
                    "title": row['title'],
                    "company": row['company'],
                    "email": row['email'],
                    "tier": row['tier'],
                    "persona_name": row['persona_name'],
                    "opportunity_score": row['opportunity_score'],
                    "enriched": bool(row['enriched']),
                    "created_at": row['created_at']
                })
            
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
    """Get a specific contact by ID"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            return dict(row)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/enrich")
async def enrich_contact(contact_id: int, request: EnrichmentRequest):
    """Enrich a contact with additional data"""
    try:
        # Import enrichment engine
        from intelligence.engines.profile_enrichment_engine import ProfileEnrichmentEngine
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            contact = cursor.fetchone()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            # Perform enrichment
            engine = ProfileEnrichmentEngine()
            enrichment_data = engine.enrich_person(
                name=contact['name'],
                company=contact['company'],
                additional_context=f"Title: {contact['title']}"
            )
            
            # Update database
            cursor.execute("""
                UPDATE contacts 
                SET enriched = 1, 
                    enriched_at = ?, 
                    enrichment_data = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                datetime.now().isoformat(),
                json.dumps(enrichment_data),
                datetime.now().isoformat(),
                contact_id
            ))
            conn.commit()
            
            return {
                "status": "success",
                "contact_id": contact_id,
                "enrichment_data": enrichment_data
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get dashboard analytics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get various stats
            cursor.execute("SELECT COUNT(*) FROM contacts")
            total_contacts = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enriched = 1")
            enriched_contacts = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(opportunity_score) FROM contacts WHERE opportunity_score IS NOT NULL")
            avg_score = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM outreach_history WHERE success = 1")
            successful_outreach = cursor.fetchone()[0]
            
            return {
                "total_contacts": total_contacts,
                "enriched_contacts": enriched_contacts,
                "enrichment_rate": f"{(enriched_contacts/total_contacts*100):.1f}%" if total_contacts > 0 else "0%",
                "average_opportunity_score": round(avg_score, 2),
                "successful_outreach": successful_outreach,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/performance")
async def get_performance_metrics():
    """Get performance metrics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get conversion metrics
            cursor.execute("""
                SELECT 
                    COUNT(CASE WHEN conversion_probability > 0.7 THEN 1 END) as high_probability,
                    COUNT(CASE WHEN conversion_probability BETWEEN 0.4 AND 0.7 THEN 1 END) as medium_probability,
                    COUNT(CASE WHEN conversion_probability < 0.4 THEN 1 END) as low_probability
                FROM contacts
            """)
            
            result = cursor.fetchone()
            
            return {
                "high_conversion_probability": result[0] or 0,
                "medium_conversion_probability": result[1] or 0,
                "low_conversion_probability": result[2] or 0,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# STARTUP & SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("\n" + "="*70)
    print("🚀 APEX SALES INTELLIGENCE API")
    print("="*70)
    
    # Initialize database
    init_db()
    
    # Check for required environment variables
    required_env = ['OPENAI_API_KEY', 'PERPLEXITY_API_KEY']
    missing_env = [env for env in required_env if not os.getenv(env)]
    
    if missing_env:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_env)}")
        print("   Some features may not work properly")
    else:
        print("✅ All environment variables configured")
    
    print("✅ All systems initialized")
    print(f"📚 API Documentation: http://localhost:{os.getenv('PORT', 3000)}/docs")
    print(f"🔍 ReDoc Documentation: http://localhost:{os.getenv('PORT', 3000)}/redoc")
    print("="*70 + "\n")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    print("\n" + "="*70)
    print("👋 Shutting down Apex API...")
    print("="*70 + "\n")

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": str(exc) if os.getenv('DEBUG') else None
        }
    )

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('PORT', 3000))
    host = os.getenv('HOST', '0.0.0.0')
    reload = os.getenv('DEBUG', 'false').lower() == 'true'
    
    uvicorn.run(
        "main:app" if reload else app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
