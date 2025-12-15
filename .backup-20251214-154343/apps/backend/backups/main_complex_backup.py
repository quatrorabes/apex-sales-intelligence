#!/usr/bin/env python3
"""
APEX Intelligence Platform - Production API
AI-Powered Sales Intelligence with MDCP/RSS Scoring
"""

import os
import json
import sqlite3
import logging
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List, Dict
import asyncio

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import intelligence modules
from intelligence.engines.scoring.scoring_orchestrator import ScoringOrchestrator
from intelligence.hubspot_sync import HubSpotSync
from intelligence.engines.enrichment.perplexity_enrichment import enrich_contact as ai_enrich
from intelligence.engines.enrichment.apex_intelligence_engine import score_contact as ai_score



# Database setup
DATABASE = os.getenv("DATABASE_PATH", "apex.db")

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
    version="3.0-PROD",
    description="Production-ready AI-Powered Sales Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Import Filters API
from api.import_filters import router as import_filters_router
app.include_router(import_filters_router)

print("✅ Import Filters API registered at /api/import/*")

# CORS middleware - configure for production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC MODELS ====================

class ContactCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None
    hubspot_id: Optional[str] = None

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None

class BulkScoreRequest(BaseModel):
    contact_ids: List[int]

class BatchEnrichRequest(BaseModel):
    contact_ids: List[int]
    
# ==================== EXCEPTION HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

# ==================== ROOT & HEALTH ====================

@app.get("/", tags=["System"])
async def root():
    """API root endpoint with system information"""
    return {
        "name": "APEX Intelligence Platform",
        "version": "3.0-PROD",
        "status": "operational",
        "features": [
            "MDCP/RSS Scoring",
            "Persona Classification",
            "HubSpot Integration",
            "Perplexity AI Enrichment"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["System"])
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }
    
    # Database check
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()[0]
            health_status["checks"]["database"] = {
                "status": "healthy",
                "contacts": count
            }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    # API Keys check
    health_status["checks"]["api_keys"] = {
        "hubspot": bool(os.getenv("HUBSPOT_API_KEY")),
        "perplexity": bool(os.getenv("PERPLEXITY_API_KEY")),
        "openai": bool(os.getenv("OPENAI_API_KEY"))
    }
    
    # Overall status
    health_status["status"] = "healthy" if all(
        check.get("status") != "unhealthy" 
        for check in health_status["checks"].values() 
        if isinstance(check, dict)
    ) else "degraded"
    
    return health_status

# ==================== CONTACT MANAGEMENT ====================

@app.get("/api/contacts", tags=["Contacts"])
async def list_contacts(
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "id",
    order: str = "desc",
    enriched_only: bool = False
):
    """List contacts with pagination and filtering"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Validate sort column
            valid_sorts = ["id", "priority_score", "mdcp_score", "rss_score", "created_at", "name", "company"]
            if sort_by not in valid_sorts:
                sort_by = "id"
            
            # Build query
            where_clause = "WHERE enriched = 1" if enriched_only else ""
            
            query = f"""
                SELECT * FROM contacts 
                {where_clause}
                ORDER BY {sort_by} {order.upper()}
                LIMIT ? OFFSET ?
            """
            
            cursor.execute(query, (limit, offset))
            contacts = [dict(row) for row in cursor.fetchall()]
            
            # Get total count
            count_query = f"SELECT COUNT(*) FROM contacts {where_clause}"
            cursor.execute(count_query)
            total = cursor.fetchone()[0]
            
            logger.info(f"Listed {len(contacts)} contacts (total: {total})")
            
            return {
                "contacts": contacts,
                "total": total,
                "limit": limit,
                "offset": offset,
                "page": (offset // limit) + 1
            }
    except Exception as e:
        logger.error(f"Error listing contacts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{contact_id}", tags=["Contacts"])
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
        logger.error(f"Error fetching contact {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts", tags=["Contacts"], status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate, background_tasks: BackgroundTasks):
    """Create a new contact and queue for scoring"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check for duplicates
            if contact.email:
                cursor.execute("SELECT id FROM contacts WHERE email = ?", (contact.email,))
                if cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Contact with this email already exists")
            
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
            
            logger.info(f"Created contact {contact_id}: {contact.name}")
            
            # Queue scoring in background
            background_tasks.add_task(score_contact_background, contact_id)
            
            return {
                "id": contact_id,
                "message": "Contact created and queued for scoring",
                "contact": contact.dict()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating contact: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/contacts/{contact_id}", tags=["Contacts"])
async def update_contact(contact_id: int, contact: ContactUpdate):
    """Update contact information"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            updates = []
            values = []
            
            for field, value in contact.dict(exclude_unset=True).items():
                updates.append(f"{field} = ?")
                values.append(value)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(contact_id)
            
            query = f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            logger.info(f"Updated contact {contact_id}")
            
            return {"id": contact_id, "message": "Contact updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/contacts/{contact_id}", tags=["Contacts"])
async def delete_contact(contact_id: int):
    """Delete a contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            logger.info(f"Deleted contact {contact_id}")
            return {"message": "Contact deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ENRICHMENT ====================
        
@app.post("/api/contacts/{contact_id}/deep-enrich", tags=["Enrichment"])
async def deep_enrich_contact(contact_id: int):
    """Deep enrich a contact with AI, then score them"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get contact
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            contact = cursor.fetchone()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
                
            contact_dict = dict(contact)
            
            print(f"\n{'='*60}")
            print(f"🚀 STARTING ENRICHMENT + SCORING PIPELINE")
            print(f"{'='*60}")
            
            # STEP 1: ENRICHMENT
            print(f"\n📡 Step 1: AI Enrichment for {contact_dict.get('name')}...")
            try:
                enrichment_result = ai_enrich(contact_id, contact_dict)
                print(f"✅ Enrichment complete!")
            except Exception as e:
                print(f"❌ Enrichment failed: {e}")
                enrichment_result = {"status": "error", "message": str(e)}
                
            # STEP 2: SCORING
            print(f"\n📊 Step 2: MDCP/RSS Scoring...")
            try:
                scoring_result = ai_score(contact_id)
                print(f"✅ Scoring complete! Priority: {scoring_result.get('priority_score')}")
            except Exception as e:
                print(f"❌ Scoring failed: {e}")
                scoring_result = {"error": str(e)}
                
            # Get columns
            cursor.execute("PRAGMA table_info(contacts)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Update database with both results
            updates = []
            values = []
            
            # Enrichment updates
            if 'enrichment_status' in columns:
                updates.append("enrichment_status = ?")
                values.append('complete' if enrichment_result.get('status') == 'success' else 'error')
                
            if 'enriched' in columns:
                updates.append("enriched = ?")
                values.append(1 if enrichment_result.get('status') == 'success' else 0)
                
            if 'enrichment_data' in columns:
                updates.append("enrichment_data = ?")
                values.append(json.dumps(enrichment_result))
                
            if 'enrichment_date' in columns:
                updates.append("enrichment_date = ?")
                values.append(datetime.now().isoformat())
                
            # Scoring updates (these are handled by ai_score but we can update status)
            if 'last_scored' in columns:
                updates.append("last_scored = ?")
                values.append(datetime.now().isoformat())
                
            # Execute update
            if updates:
                values.append(contact_id)
                query = f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, values)
                conn.commit()
                
            print(f"\n{'='*60}")
            print(f"✅ PIPELINE COMPLETE")
            print(f"   Priority Score: {scoring_result.get('priority_score', 'N/A')}")
            print(f"   Urgency: {scoring_result.get('urgency_level', 'N/A')}")
            print(f"   Action: {scoring_result.get('recommended_action', 'N/A')}")
            print(f"{'='*60}\n")
            
            return {
                "success": True,
                "contact_id": contact_id,
                "message": "Enrichment and scoring complete",
                "enrichment": {
                    "status": enrichment_result.get('status'),
                    "company": enrichment_result.get('company_name'),
                    "overview": enrichment_result.get('overview')
                },
                "scoring": {
                    "priority_score": scoring_result.get('priority_score'),
                    "mdcp_score": scoring_result.get('mdcp_score'),
                    "rss_score": scoring_result.get('rss_score'),
                    "urgency": scoring_result.get('urgency_level'),
                    "action": scoring_result.get('recommended_action')
                }
            }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ PIPELINE FAILED: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== BATCH OPERATIONS ====================

@app.post("/api/contacts/enrich-and-score/batch", tags=["Batch Operations"])
async def batch_enrich_and_score(request: BatchEnrichRequest):
    """Batch enrich and score multiple contacts"""
    results = []
    total = len(request.contact_ids)
    max_batch = min(total, 10)  # Process max 10 at a time
    
    logger.info(f"Starting batch enrichment for {max_batch} contacts")
    
    for i, contact_id in enumerate(request.contact_ids[:max_batch], 1):
        try:
            print(f"\n[{i}/{max_batch}] Processing contact {contact_id}...")
            
            # Get contact data
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
                contact = cursor.fetchone()
                
                if not contact:
                    results.append({
                        "contact_id": contact_id,
                        "status": "error",
                        "error": "Contact not found"
                    })
                    continue
                
                contact_dict = dict(contact)
            
            # Enrich
            try:
                enrichment_result = ai_enrich(contact_id, contact_dict)
                enrichment_status = "success"
            except Exception as e:
                enrichment_result = {"status": "error", "message": str(e)}
                enrichment_status = "error"
            
            # Score
            try:
                scoring_result = ai_score(contact_id)
                scoring_status = "success"
            except Exception as e:
                scoring_result = {"error": str(e)}
                scoring_status = "error"
            
            results.append({
                "contact_id": contact_id,
                "status": "success" if enrichment_status == "success" and scoring_status == "success" else "partial",
                "enrichment_status": enrichment_status,
                "scoring_status": scoring_status,
                "priority_score": scoring_result.get('priority_score'),
                "urgency": scoring_result.get('urgency_level')
            })
            
            # Small delay to avoid rate limits
            await asyncio.sleep(2)
            
        except Exception as e:
            logger.error(f"Error processing contact {contact_id}: {str(e)}")
            results.append({
                "contact_id": contact_id,
                "status": "error",
                "error": str(e)
            })
    
    # Summary
    successful = len([r for r in results if r['status'] == 'success'])
    partial = len([r for r in results if r['status'] == 'partial'])
    failed = len([r for r in results if r['status'] == 'error'])
    
    return {
        "processed": len(results),
        "successful": successful,
        "partial": partial,
        "failed": failed,
        "results": results,
        "message": f"Batch processing complete: {successful} successful, {partial} partial, {failed} failed"
    }

@app.post("/api/contacts/score/batch", tags=["Batch Operations"])
async def batch_score_only(request: BulkScoreRequest):
    """Batch score multiple contacts (no enrichment)"""
    results = []
    
    for contact_id in request.contact_ids[:20]:  # Limit to 20
        try:
            scoring_result = ai_score(contact_id)
            results.append({
                "contact_id": contact_id,
                "status": "success",
                "priority_score": scoring_result.get('priority_score'),
                "mdcp_score": scoring_result.get('mdcp_score'),
                "rss_score": scoring_result.get('rss_score'),
                "urgency": scoring_result.get('urgency_level')
            })
        except Exception as e:
            results.append({
                "contact_id": contact_id,
                "status": "error",
                "error": str(e)
            })
    
    return {
        "processed": len(results),
        "successful": len([r for r in results if r['status'] == 'success']),
        "failed": len([r for r in results if r['status'] == 'error']),
        "results": results
    }

# ==================== DASHBOARD ====================

@app.get("/api/dashboard/{contact_id}", tags=["Dashboard"])
async def get_dashboard_data(contact_id: int):
    """Get comprehensive dashboard data for a contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            contact = cursor.fetchone()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact_dict = dict(contact)
            
            # Parse enrichment data
            enrichment_data = {}
            if contact_dict.get('enrichment_data'):
                try:
                    enrichment_data = json.loads(contact_dict['enrichment_data'])
                except:
                    enrichment_data = {}
            
            # Build response
            response = {
                "contact_info": {
                    "id": contact_dict['id'],
                    "name": contact_dict.get('name'),
                    "email": contact_dict.get('email'),
                    "company": contact_dict.get('company'),
                    "title": contact_dict.get('title'),
                    "phone": contact_dict.get('phone')
                },
                "enrichment_status": contact_dict.get('enrichment_status', 'pending'),
                "scores": {
                    "priority_score": contact_dict.get('priority_score'),
                    "mdcp_score": contact_dict.get('mdcp_score'),
                    "rss_score": contact_dict.get('rss_score'),
                    "persona_tier": contact_dict.get('persona_tier')
                }
            }
            
            # Add enrichment data if available
            if enrichment_data:
                response["intelligence"] = enrichment_data.get('data', enrichment_data)
                response["generated_scripts"] = enrichment_data.get('generated_scripts', {})
            
            return response
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching dashboard data for {contact_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SCORING ====================

@app.post("/api/contacts/{contact_id}/score", tags=["Scoring"])
async def score_contact_endpoint(contact_id: int):
    """Score a contact using MDCP/RSS (no enrichment)"""
    try:
        print(f"\n📊 Scoring contact {contact_id}...")
        scoring_result = ai_score(contact_id)
        
        return {
            "success": True,
            "contact_id": contact_id,
            **scoring_result
        }
    except Exception as e:
        print(f"❌ Scoring failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def score_contact_background(contact_id: int):
    """Background task for contact scoring"""
    try:
        logger.info(f"Background scoring contact {contact_id}")
        result = ai_score(contact_id)
        logger.info(f"✅ Background scoring complete for contact {contact_id}")
    except Exception as e:
        logger.error(f"❌ Background scoring failed for contact {contact_id}: {str(e)}")

@app.get("/api/apex/scores", tags=["Scoring"])
async def get_apex_scores(
    limit: int = 100,
    min_score: float = 0
):
    """Get all scored contacts with filtering"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, name, company, title, email,
                    priority_score, mdcp_score, rss_score, 
                    persona_tier, persona_type,
                    enrichment_status, last_scored
                FROM contacts
                WHERE priority_score IS NOT NULL
                AND priority_score >= ?
                ORDER BY priority_score DESC
                LIMIT ?
            """, (min_score, limit))
            
            scores = [dict(row) for row in cursor.fetchall()]
            
            return {
                "scores": scores,
                "count": len(scores)
            }
    except Exception as e:
        logger.error(f"Error fetching scores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== ANALYTICS ====================

@app.get("/api/analytics/dashboard", tags=["Analytics"])
async def get_dashboard_analytics():
    """Get comprehensive analytics for dashboard"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            analytics = {}
            
            # Contact counts
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN enriched = 1 THEN 1 ELSE 0 END) as enriched,
                    SUM(CASE WHEN priority_score IS NOT NULL THEN 1 ELSE 0 END) as scored
                FROM contacts
            """)
            counts = dict(cursor.fetchone())
            analytics["contacts"] = counts
            
            # Score averages
            cursor.execute("""
                SELECT 
                    AVG(priority_score) as avg_priority,
                    AVG(mdcp_score) as avg_mdcp,
                    AVG(rss_score) as avg_rss,
                    MAX(priority_score) as max_priority,
                    MIN(priority_score) as min_priority
                FROM contacts
                WHERE priority_score IS NOT NULL
            """)
            scores = dict(cursor.fetchone())
            analytics["scores"] = {
                k: round(v, 2) if v else 0 
                for k, v in scores.items()
            }
            
            # Persona distribution
            cursor.execute("""
                SELECT 
                    persona_tier,
                    COUNT(*) as count
                FROM contacts
                WHERE persona_tier IS NOT NULL
                GROUP BY persona_tier
            """)
            personas = {row['persona_tier']: row['count'] for row in cursor.fetchall()}
            analytics["personas"] = personas
            
            # High priority contacts
            cursor.execute("""
                SELECT COUNT(*) as high_priority
                FROM contacts
                WHERE priority_score >= 70
            """)
            analytics["high_priority"] = cursor.fetchone()['high_priority']
            
            analytics["timestamp"] = datetime.now().isoformat()
            
            return analytics
            
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== HUBSPOT INTEGRATION ====================

@app.post("/api/hubspot/import", tags=["HubSpot"])
async def import_from_hubspot(
    background_tasks: BackgroundTasks,  # First (no default)
    limit: int = 100  # Second (has default)
):


    """Import contacts from HubSpot"""
    try:
        if not os.getenv('HUBSPOT_API_KEY'):
            raise HTTPException(
                status_code=400, 
                detail="HubSpot API key not configured"
            )
        
        hubspot = HubSpotSync()
        contacts = hubspot.import_contacts_from_hubspot(limit=limit)
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            new_imports = 0
            existing = 0
            imported_ids = []
            
            for contact_data in contacts:
                # Check if already exists
                cursor.execute(
                    "SELECT id FROM contacts WHERE hubspot_id = ?", 
                    (contact_data.get('hubspot_id'),)
                )
                existing_contact = cursor.fetchone()
                
                if existing_contact:
                    existing += 1
                    continue
                
                # Build name
                name = contact_data.get('name')
                if not name:
                    first = contact_data.get('firstname', '')
                    last = contact_data.get('lastname', '')
                    name = f"{first} {last}".strip() or "Unknown"
                
                # Insert new contact
                cursor.execute("""
                    INSERT INTO contacts (
                        name, email, phone, company, title, 
                        hubspot_id, created_at, enrichment_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    contact_data.get('email'),
                    contact_data.get('phone'),
                    contact_data.get('company'),
                    contact_data.get('title'),
                    contact_data.get('hubspot_id'),
                    datetime.now().isoformat(),
                    'pending'
                ))
                
                imported_ids.append(cursor.lastrowid)
                new_imports += 1
            
            conn.commit()
            
            # Queue scoring for new imports
            for contact_id in imported_ids:
                background_tasks.add_task(score_contact_background, contact_id)
            
            logger.info(f"Imported {new_imports} contacts from HubSpot (skipped {existing} existing)")
            
            return {
                "imported": new_imports,
                "existing": existing,
                "total_in_hubspot": len(contacts),
                "message": f"Import complete. {new_imports} new contacts queued for scoring."
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"HubSpot import error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STARTUP & SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 APEX Intelligence Platform starting...")
    
    # Verify database
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()[0]
            logger.info(f"✅ Database connected: {count} contacts")
    except Exception as e:
        logger.error(f"❌ Database error: {str(e)}")
    
    # Check API keys
    api_keys = {
        "HubSpot": bool(os.getenv("HUBSPOT_API_KEY")),
        "Perplexity": bool(os.getenv("PERPLEXITY_API_KEY")),
        "OpenAI": bool(os.getenv("OPENAI_API_KEY"))
    }
    
    for service, configured in api_keys.items():
        if configured:
            logger.info(f"✅ {service} API configured")
        else:
            logger.warning(f"⚠️ {service} API not configured")
    
    logger.info("🎯 APEX Platform ready for production!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 APEX Platform shutting down...")

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    # Production configuration
    config = {
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", 8000)),
        "reload": os.getenv("ENVIRONMENT", "development") == "development",
        "log_level": os.getenv("LOG_LEVEL", "info").lower(),
        "access_log": True
    }
    
    print("=" * 70)
    print("🚀 APEX Intelligence Platform - PRODUCTION")
    print("=" * 70)
    print(f"Server: http://{config['host']}:{config['port']}")
    print(f"Docs: http://{config['host']}:{config['port']}/docs")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print("=" * 70)
    
    uvicorn.run("main:app", **config)
    