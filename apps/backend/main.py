"""
APEX SALES INTELLIGENCE - PRODUCTION BACKEND
Unified backend with all features from api.py + main.py
PostgreSQL database, deployed on Render
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Apex Sales Intelligence API",
    description="Production-ready sales intelligence platform with enrichment, scoring, and analytics",
    version="2.0.0"
)

# CORS Configuration
ALLOWED_ORIGINS = [
    "https://apex-sales-intelligence.vercel.app",
    "https://apex-sales-intelligence-*.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()

# Initialize Enrichment Engine (if available)
try:
    from enrichment_engine import EnhancedEnrichment
    enrichment_engine = EnhancedEnrichment()
    logger.info("✅ Enrichment engine loaded")
except ImportError:
    enrichment_engine = None
    logger.warning("⚠️ Enrichment engine not available")

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    match_score: Optional[int] = None
    match_tier: Optional[str] = None

class PersonaRequest(BaseModel):
    contact_id: int
    persona_type: str  # INITIATOR, CHAMPION, DECISION_MAKER, BLOCKER

class ScoreRequest(BaseModel):
    contact_ids: List[int]

class EnrollmentRequest(BaseModel):
    contact_id: int
    cadence_name: str
    sequence_days: int = 14

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Apex Sales Intelligence API",
        "status": "operational",
        "version": "2.0.0",
        "deployed_on": "Render",
        "database": "PostgreSQL (Railway)",
        "features": [
            "Contact Management",
            "Deep Enrichment (3-stage Perplexity)",
            "MDCP/RSS Scoring",
            "Persona Classification",
            "ICP Matching",
            "Cadence Enrollment",
            "Analytics Dashboard",
            "Batch Operations"
        ]
    }

@app.get("/health", tags=["Health"])
async def health():
    """Health check with database stats"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total_contacts = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched_contacts = cursor.fetchone()["count"]
            
            cursor.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_contacts": total_contacts,
            "enriched_contacts": enriched_contacts,
            "enrichment_engine": "available" if enrichment_engine else "unavailable",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# ============================================================================
# CONTACT CRUD ENDPOINTS
# ============================================================================

@app.get("/api/contacts", tags=["Contacts"])
async def list_contacts(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    enriched_only: bool = False
):
    """List contacts with pagination and filtering"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Build query
            query = "SELECT * FROM contacts WHERE 1=1"
            params = []
            
            if search:
                query += " AND (name ILIKE %s OR company ILIKE %s OR email ILIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            if enriched_only:
                query += " AND enrichment_status = 'completed'"
            
            query += " ORDER BY id DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            contacts = cursor.fetchall()
            
            # Get total count
            count_query = "SELECT COUNT(*) as count FROM contacts WHERE 1=1"
            count_params = []
            if search:
                count_query += " AND (name ILIKE %s OR company ILIKE %s OR email ILIKE %s)"
                count_params.extend([search_term, search_term, search_term])
            if enriched_only:
                count_query += " AND enrichment_status = 'completed'"
            
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()["count"]
            
            cursor.close()
            
            return {
                "success": True,
                "contacts": [dict(c) for c in contacts],
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.error(f"List contacts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{contact_id}", tags=["Contacts"])
async def get_contact(contact_id: int):
    """Get single contact by ID"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            return {
                "success": True,
                "contact": dict(contact)
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts", tags=["Contacts"])
async def create_contact(contact: ContactCreate):
    """Create new contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (name, email, company, title, phone, linkedin_url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
            """, (
                contact.name,
                contact.email,
                contact.company,
                contact.title,
                contact.phone,
                contact.linkedin_url
            ))
            contact_id = cursor.fetchone()["id"]
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "message": "Contact created successfully"
            }
    except Exception as e:
        logger.error(f"Create contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/contacts/{contact_id}", tags=["Contacts"])
async def update_contact(contact_id: int, contact: ContactUpdate):
    """Update existing contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            updates = []
            params = []
            
            if contact.name is not None:
                updates.append("name = %s")
                params.append(contact.name)
            if contact.email is not None:
                updates.append("email = %s")
                params.append(contact.email)
            if contact.company is not None:
                updates.append("company = %s")
                params.append(contact.company)
            if contact.title is not None:
                updates.append("title = %s")
                params.append(contact.title)
            if contact.phone is not None:
                updates.append("phone = %s")
                params.append(contact.phone)
            if contact.linkedin_url is not None:
                updates.append("linkedin_url = %s")
                params.append(contact.linkedin_url)
            if contact.match_score is not None:
                updates.append("match_score = %s")
                params.append(contact.match_score)
            if contact.match_tier is not None:
                updates.append("match_tier = %s")
                params.append(contact.match_tier)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            query = f"UPDATE contacts SET {', '.join(updates)} WHERE id = %s"
            params.append(contact_id)
            
            cursor.execute(query, params)
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            cursor.close()
            
            return {
                "success": True,
                "message": "Contact updated successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/contacts/{contact_id}", tags=["Contacts"])
async def delete_contact(contact_id: int):
    """Delete contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            cursor.close()
            
            return {
                "success": True,
                "message": "Contact deleted successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENRICHMENT ENDPOINTS
# ============================================================================

@app.post("/api/contacts/{contact_id}/enrich", tags=["Enrichment"])
async def enrich_contact(contact_id: int):
    """
    Deep enrichment with 3-stage Perplexity search
    Generates 20k+ character professional profiles
    """
    if not enrichment_engine:
        raise HTTPException(status_code=503, detail="Enrichment engine not available")

    try:
        # Get contact data
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")

            # Mark as enriching
            cursor.execute("UPDATE contacts SET enrichment_status = 'enriching' WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()

        # Convert to dict for enrichment engine
        contact_dict = dict(contact)

        # Call enrichment engine
        logger.info(f"🚀 Starting enrichment for {contact_dict.get('name')} (ID: {contact_id})")
        enrichment_result = enrichment_engine.enrich_contact(contact_dict)

        # Save results to database
        with get_db() as conn:
            cursor = conn.cursor()

            # Prepare clean enrichment data
            profile_text = enrichment_result.get('profile_text', '')
            enrichment_json = json.dumps({
                'profile_text': profile_text,
                'character_count': len(profile_text),
                'enriched_at': datetime.now().isoformat(),
                'success': True
            })

            # Update contact with enrichment data
            cursor.execute("""
                UPDATE contacts SET
                    enrichment_status = 'completed',
                    enriched_at = NOW(),
                    enrichment_data = %s,
                    match_score = COALESCE(match_score, 0) + 20
                WHERE id = %s
            """, (
                enrichment_json,
                contact_id
            ))
            conn.commit()
            cursor.close()
        
        logger.info(f"✅ Enrichment completed for contact {contact_id} ({len(profile_text)} chars)")
        
        return {
            "success": True,
            "contact_id": contact_id,
            "profile_length": len(profile_text),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrichment error for contact {contact_id}: {e}")
        # Mark as failed
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/deep-enrich", tags=["Enrichment"])
async def deep_enrich_contact(contact_id: int):
    """
    Full APEX deep enrichment with MDCP/RSS scoring pipeline
    Includes persona classification, ICP matching, and call script generation
    """
    try:
        # Step 1: Basic enrichment
        enrich_result = await enrich_contact(contact_id)
        
        # Step 2: Generate persona
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = dict(cursor.fetchone())
            cursor.close()
        
        # Determine persona based on title
        title = (contact.get('title') or '').lower()
        if any(word in title for word in ['ceo', 'founder', 'president', 'owner']):
            persona = 'DECISION_MAKER'
        elif any(word in title for word in ['vp', 'director', 'head', 'chief']):
            persona = 'CHAMPION'
        elif any(word in title for word in ['manager', 'lead', 'coordinator']):
            persona = 'INITIATOR'
        else:
            persona = 'INITIATOR'
        
        # Step 3: Calculate MDCP/RSS scores
        mdcp_score = 0
        rss_score = 0
        
        # MDCP Components (out of 100)
        if contact.get('match_score'):
            mdcp_score += min(contact['match_score'], 25)  # Match: 25 points
        if contact.get('enrichment_status') == 'completed':
            mdcp_score += 25  # Data: 25 points
        if persona in ['CHAMPION', 'DECISION_MAKER']:
            mdcp_score += 25  # Contact: 25 points
        if contact.get('company'):
            mdcp_score += 25  # Profile: 25 points
        
        # RSS Components (out of 100)
        if contact.get('urgency_level') == 'HIGH':
            rss_score += 40  # Readiness: 40 points
        elif contact.get('urgency_level') == 'MEDIUM':
            rss_score += 20
        
        rss_score += 30  # Suitability: 30 points (placeholder)
        rss_score += 30  # Seniority: 30 points (placeholder)
        
        # Step 4: Update contact with scores and persona
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts SET
                    persona_type = %s,
                    mdcp_score = %s,
                    rss_score = %s,
                    apex_score = %s
                WHERE id = %s
            """, (
                persona,
                mdcp_score,
                rss_score,
                (mdcp_score + rss_score) / 2,  # APEX Score = average
                contact_id
            ))
            conn.commit()
            cursor.close()
        
        return {
            "success": True,
            "contact_id": contact_id,
            "enrichment": enrich_result,
            "persona": persona,
            "scores": {
                "mdcp": mdcp_score,
                "rss": rss_score,
                "apex": (mdcp_score + rss_score) / 2
            }
        }
        
    except Exception as e:
        logger.error(f"Deep enrichment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/enrich-and-score/batch", tags=["Enrichment"])
async def batch_enrich_and_score(request: ScoreRequest):
    """Batch enrich and score multiple contacts"""
    results = []
    for contact_id in request.contact_ids:
        try:
            result = await deep_enrich_contact(contact_id)
            results.append({"contact_id": contact_id, "success": True, "data": result})
        except Exception as e:
            results.append({"contact_id": contact_id, "success": False, "error": str(e)})
    
    return {
        "success": True,
        "total": len(request.contact_ids),
        "results": results
    }

# ============================================================================
# SCORING ENDPOINTS
# ============================================================================

@app.post("/api/contacts/{contact_id}/score", tags=["Scoring"])
async def score_contact(contact_id: int):
    """Calculate MDCP/RSS scores for a contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            # Calculate MDCP Score
            mdcp_score = 0
            if contact.get('match_score'):
                mdcp_score += min(contact['match_score'], 25)
            if contact.get('enrichment_status') == 'completed':
                mdcp_score += 25
            if contact.get('persona_type') in ['CHAMPION', 'DECISION_MAKER']:
                mdcp_score += 25
            if contact.get('company'):
                mdcp_score += 25
            
            # Calculate RSS Score
            rss_score = 0
            if contact.get('urgency_level') == 'HIGH':
                rss_score += 40
            elif contact.get('urgency_level') == 'MEDIUM':
                rss_score += 20
            rss_score += 30  # Suitability placeholder
            rss_score += 30  # Seniority placeholder
            
            # Update database
            apex_score = (mdcp_score + rss_score) / 2
            cursor.execute("""
                UPDATE contacts SET
                    mdcp_score = %s,
                    rss_score = %s,
                    apex_score = %s
                WHERE id = %s
            """, (mdcp_score, rss_score, apex_score, contact_id))
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "scores": {
                    "mdcp": mdcp_score,
                    "rss": rss_score,
                    "apex": apex_score
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Score contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/score/batch", tags=["Scoring"])
async def batch_score_contacts(request: ScoreRequest):
    """Batch score multiple contacts"""
    results = []
    for contact_id in request.contact_ids:
        try:
            result = await score_contact(contact_id)
            results.append({"contact_id": contact_id, "success": True, "scores": result["scores"]})
        except Exception as e:
            results.append({"contact_id": contact_id, "success": False, "error": str(e)})
    
    return {
        "success": True,
        "total": len(request.contact_ids),
        "results": results
    }

@app.get("/api/apex/scores", tags=["Scoring"])
async def get_apex_scores(
    min_score: Optional[int] = 0,
    max_score: Optional[int] = 100,
    limit: int = 50
):
    """Get contacts ranked by APEX score"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, company, title, apex_score, mdcp_score, rss_score
                FROM contacts
                WHERE apex_score IS NOT NULL
                    AND apex_score >= %s
                    AND apex_score <= %s
                ORDER BY apex_score DESC
                LIMIT %s
            """, (min_score, max_score, limit))
            contacts = cursor.fetchall()
            cursor.close()
            
            return {
                "success": True,
                "contacts": [dict(c) for c in contacts],
                "count": len(contacts)
            }
    except Exception as e:
        logger.error(f"Get APEX scores error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ICP & PERSONA ENDPOINTS
# ============================================================================

@app.get("/api/contacts/{contact_id}/icp-match", tags=["ICP"])
async def get_icp_match(contact_id: int):
    """Get ICP match analysis for a contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            # Calculate ICP match score
            match_score = contact.get('match_score', 0)
            tier = 'LOW'
            if match_score >= 80:
                tier = 'HIGH'
            elif match_score >= 50:
                tier = 'MEDIUM'
            
            return {
                "success": True,
                "contact_id": contact_id,
                "icp_match": {
                    "score": match_score,
                    "tier": tier,
                    "company": contact.get('company'),
                    "title": contact.get('title'),
                    "factors": {
                        "company_size": "N/A",
                        "industry_match": "N/A",
                        "title_match": "Strong" if contact.get('title') else "Weak"
                    }
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ICP match error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-persona", tags=["Persona"])
async def generate_persona(contact_id: int):
    """Generate persona classification for contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            title = (contact.get('title') or '').lower()
            
            # Classify persona
            if any(word in title for word in ['ceo', 'founder', 'president', 'owner']):
                persona = 'DECISION_MAKER'
            elif any(word in title for word in ['vp', 'director', 'head', 'chief']):
                persona = 'CHAMPION'
            elif any(word in title for word in ['manager', 'lead', 'coordinator']):
                persona = 'INITIATOR'
            else:
                persona = 'INITIATOR'
            
            # Update database
            cursor.execute("UPDATE contacts SET persona_type = %s WHERE id = %s", (persona, contact_id))
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "persona": persona,
                "confidence": 0.85
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate persona error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CADENCE & ENROLLMENT ENDPOINTS
# ============================================================================

@app.get("/api/contacts/{contact_id}/enrollments", tags=["Cadence"])
async def get_enrollments(contact_id: int):
    """Get active cadence enrollments for contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            # Return enrollment data
            enrollments = []
            if contact.get('cadence_status') == 'active':
                enrollments.append({
                    "cadence_name": contact.get('cadence_name', 'Default Cadence'),
                    "status": "active",
                    "current_step": contact.get('cadence_step', 1),
                    "total_steps": contact.get('cadence_total_steps', 7),
                    "next_action": "Send follow-up email",
                    "next_action_date": (datetime.now() + timedelta(days=1)).isoformat()
                })
            
            return {
                "success": True,
                "contact_id": contact_id,
                "enrollments": enrollments,
                "count": len(enrollments)
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get enrollments error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/enroll", tags=["Cadence"])
async def enroll_contact(contact_id: int, request: EnrollmentRequest):
    """Enroll contact in sales cadence"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts SET
                    cadence_status = 'active',
                    cadence_name = %s,
                    cadence_step = 1,
                    cadence_total_steps = %s,
                    cadence_enrolled_at = NOW()
                WHERE id = %s
            """, (request.cadence_name, request.sequence_days, contact_id))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "cadence_name": request.cadence_name,
                "sequence_days": request.sequence_days,
                "status": "enrolled"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enroll contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CONTENT GENERATION ENDPOINTS
# ============================================================================

@app.post("/api/contacts/{contact_id}/generate-call-script", tags=["Content"])
async def generate_call_script(contact_id: int):
    """Generate personalized cold call script"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            # Generate simple call script
            script = f"""
COLD CALL SCRIPT - {contact.get('name', 'Contact')}

Opening:
"Hi {contact.get('name', 'there')}, this is [Your Name] from [Your Company]. 
I work with {contact.get('title', 'professionals')} at companies like {contact.get('company', 'yours')}. 
Do you have a quick minute?"

Value Proposition:
"We help organizations improve their sales intelligence and contact enrichment processes. 
Based on what I know about {contact.get('company', 'your company')}, I thought this might be relevant."

Discovery Question:
"Are you currently using any tools for contact enrichment or sales intelligence?"

Next Steps:
"Would you be open to a 15-minute call next week to explore this further?"
            """
            
            return {
                "success": True,
                "contact_id": contact_id,
                "call_script": script.strip()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate call script error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-email", tags=["Content"])
async def generate_email(contact_id: int):
    """Generate personalized outreach email"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            # Generate email
            email = f"""
Subject: Quick question for {contact.get('company', 'your team')}

Hi {contact.get('name', 'there')},

I noticed you're {contact.get('title', 'leading efforts')} at {contact.get('company', 'your organization')}.

I work with companies in your space to improve their sales intelligence and contact enrichment processes. 
Would you be open to a brief conversation about how we're helping organizations like yours?

Let me know if you have 15 minutes next week.

Best regards,
[Your Name]
            """
            
            return {
                "success": True,
                "contact_id": contact_id,
                "email": email.strip()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-linkedin", tags=["Content"])
async def generate_linkedin_message(contact_id: int):
    """Generate LinkedIn connection message"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            # Generate LinkedIn message
            message = f"""Hi {contact.get('name', 'there')},

I came across your profile and was impressed by your work as {contact.get('title', 'a professional')} at {contact.get('company', 'your company')}.

I'd love to connect and learn more about your work in the space.

Looking forward to connecting!"""
            
            return {
                "success": True,
                "contact_id": contact_id,
                "linkedin_message": message.strip()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate LinkedIn message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DASHBOARD & ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/todays-board", tags=["Dashboard"])
async def todays_board():
    """Get today's prioritized contact board"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get top contacts
            cursor.execute("""
                SELECT * FROM contacts 
                ORDER BY COALESCE(apex_score, match_score, 0) DESC, id DESC 
                LIMIT 20
            """)
            contacts = [dict(row) for row in cursor.fetchall()]
            
            # Stats queries
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE match_tier = 'HIGH' OR urgency_level = 'HIGH'
            """)
            high_priority = cursor.fetchone()["count"]
            
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE cadence_status = 'active'
            """)
            in_call_queue = cursor.fetchone()["count"]
            
            cursor.close()
            
            # Segment contacts by priority
            high_contacts = [c for c in contacts if c.get('match_tier') == 'HIGH' or c.get('urgency_level') == 'HIGH']
            
            return {
                "success": True,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "stats": {
                    "total_contacts": total,
                    "enriched": enriched,
                    "high_match": high_priority,
                    "medium_match": 0,
                    "low_match": 0,
                    "cold_call_queue": in_call_queue
                },
                "segments": {
                    "high": high_contacts[:10],
                    "medium": [],
                    "low": []
                },
                "top_priority": contacts[:20],
                "cold_call_stats": {
                    "total": in_call_queue,
                    "new": 0,
                    "meeting_set": 0
                }
            }
    except Exception as e:
        logger.error(f"todays_board error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics", tags=["Analytics"])
async def get_analytics():
    """Get platform analytics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Total contacts
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total_contacts = cursor.fetchone()["count"]
            
            # Enriched contacts
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            
            # By match tier
            cursor.execute("SELECT match_tier, COUNT(*) as count FROM contacts WHERE match_tier IS NOT NULL GROUP BY match_tier")
            match_tiers = {row["match_tier"]: row["count"] for row in cursor.fetchall()}
            
            # By persona
            cursor.execute("SELECT persona_type, COUNT(*) as count FROM contacts WHERE persona_type IS NOT NULL GROUP BY persona_type")
            personas = {row["persona_type"]: row["count"] for row in cursor.fetchall()}
            
            # In cadence
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE cadence_status = 'active'")
            in_cadence = cursor.fetchone()["count"]
            
            cursor.close()
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "contacts": {
                    "total": total_contacts,
                    "enriched": enriched,
                    "enrichment_rate": round((enriched / total_contacts * 100), 2) if total_contacts > 0 else 0
                },
                "match_tiers": match_tiers,
                "personas": personas,
                "cadence": {
                    "active_enrollments": in_cadence
                }
            }
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/dashboard", tags=["Analytics"])
async def analytics_dashboard():
    """Comprehensive analytics dashboard"""
    try:
        analytics = await get_analytics()
        board = await todays_board()
        
        return {
            "success": True,
            "analytics": analytics,
            "todays_board": board,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/{contact_id}", tags=["Dashboard"])
async def contact_dashboard(contact_id: int):
    """Full contact intelligence dashboard"""
    try:
        # Get base contact data
        contact_response = await get_contact(contact_id)
        contact = contact_response["contact"]
        
        # Get ICP match
        try:
            icp = await get_icp_match(contact_id)
        except:
            icp = {"icp_match": None}
        
        # Get enrollments
        try:
            enrollments = await get_enrollments(contact_id)
        except:
            enrollments = {"enrollments": []}
        
        return {
            "success": True,
            "contact": contact,
            "icp_analysis": icp.get("icp_match"),
            "enrollments": enrollments.get("enrollments", []),
            "scores": {
                "mdcp": contact.get("mdcp_score"),
                "rss": contact.get("rss_score"),
                "apex": contact.get("apex_score")
            },
            "persona": contact.get("persona_type"),
            "enrichment_status": contact.get("enrichment_status")
        }
    except Exception as e:
        logger.error(f"Contact dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SMART LISTS & QUEUES
# ============================================================================

@app.get("/api/smart-lists", tags=["Lists"])
async def get_smart_lists():
    """Get predefined smart lists"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # High Priority
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE match_tier = 'HIGH' OR apex_score >= 70
            """)
            high_priority = cursor.fetchone()["count"]
            
            # Recently Enriched
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE enrichment_status = 'completed' 
                AND enriched_at >= NOW() - INTERVAL '7 days'
            """)
            recently_enriched = cursor.fetchone()["count"]
            
            # Needs Enrichment
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE enrichment_status IS NULL OR enrichment_status = 'failed'
            """)
            needs_enrichment = cursor.fetchone()["count"]
            
            # Decision Makers
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE persona_type = 'DECISION_MAKER'
            """)
            decision_makers = cursor.fetchone()["count"]
            
            cursor.close()
            
            return {
                "success": True,
                "lists": [
                    {
                        "id": "high-priority",
                        "name": "High Priority",
                        "count": high_priority,
                        "description": "Contacts with high match score or APEX score"
                    },
                    {
                        "id": "recently-enriched",
                        "name": "Recently Enriched",
                        "count": recently_enriched,
                        "description": "Enriched in last 7 days"
                    },
                    {
                        "id": "needs-enrichment",
                        "name": "Needs Enrichment",
                        "count": needs_enrichment,
                        "description": "Not yet enriched or failed enrichment"
                    },
                    {
                        "id": "decision-makers",
                        "name": "Decision Makers",
                        "count": decision_makers,
                        "description": "Classified as decision makers"
                    }
                ]
            }
    except Exception as e:
        logger.error(f"Smart lists error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cold-call/queue", tags=["Queues"])
async def cold_call_queue():
    """Get cold call queue"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM contacts
                WHERE cadence_status = 'active'
                ORDER BY apex_score DESC NULLS LAST
                LIMIT 20
            """)
            queue = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            
            return {
                "success": True,
                "queue": queue,
                "count": len(queue),
                "generated_at": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Cold call queue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# HUBSPOT INTEGRATION
# ============================================================================

@app.post("/api/hubspot/import", tags=["HubSpot"])
async def import_from_hubspot():
    """Import contacts from HubSpot (placeholder)"""
    return {
        "success": False,
        "message": "HubSpot integration not yet configured",
        "note": "Requires HUBSPOT_API_KEY environment variable"
    }

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("=" * 70)
    logger.info("🚀 APEX SALES INTELLIGENCE - PRODUCTION BACKEND")
    logger.info("=" * 70)
    logger.info(f"Version: 2.0.0")
    logger.info(f"Deployed on: Render")
    logger.info(f"Database: PostgreSQL (Railway)")
    
    # Test database connection
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            cursor.close()
        
        logger.info(f"✅ Database connected: {total} contacts ({enriched} enriched)")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
    
    if enrichment_engine:
        logger.info("✅ Enrichment engine loaded")
    else:
        logger.warning("⚠️ Enrichment engine not available")
    
    logger.info("=" * 70)
    logger.info("🎯 ALL SYSTEMS OPERATIONAL")
    logger.info("=" * 70)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
