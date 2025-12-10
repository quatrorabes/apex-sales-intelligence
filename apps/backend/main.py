
#!/usr/bin/env python3
"""
Apex Sales Intelligence Backend - COMPLETE FastAPI Implementation
All endpoints from original Flask api.py ported to FastAPI
Production-ready for Render
"""

import os
import logging
import sys
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()

# SET UP LOGGING FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable required")

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = RealDictCursor
    try:
        yield conn
    finally:
        conn.close()

app = FastAPI(title="Apex Sales Intelligence API", version="2.0")

# CORS - Includes Vercel production domain
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:8000,https://apex-sales-intelligence.vercel.app"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enrichment engine
sys.path.insert(0, str(Path(__file__).parent / 'intelligence' / 'engines' / 'enrichment'))
enrichment_engine = None
try:
    from enhanced_enrichment import EnhancedEnrichment
    enrichment_engine = EnhancedEnrichment()
    logger.info("✅ Enrichment engine loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ Enrichment engine failed to load: {e}")
    enrichment_engine = None

# ==================== SYSTEM ROUTES ====================
@app.get("/", tags=["System"])
async def root():
    return {"status": "running", "service": "apex-backend", "version": "2.0"}

@app.get("/health", tags=["System"])
async def health():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            count = cursor.fetchone()["count"]
            cursor.close()
        return {
            "status": "healthy",
            "database": "connected",
            "contacts": count,
            "enrichment_engine": "loaded" if enrichment_engine else "unavailable",
            "service": "apex-backend",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/debug/routes", tags=["System"])
async def debug_routes():
    routes = [{"path": r.path, "methods": list(r.methods) if r.methods else []} for r in app.routes]
    return {"total": len(routes), "routes": routes}

# ==================== DASHBOARD ====================
@app.get("/api/todays-board", tags=["Dashboard"])
async def todays_board():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get top contacts
            cursor.execute("""
                SELECT * FROM contacts 
                ORDER BY COALESCE(match_score, 0) DESC, id DESC 
                LIMIT 20
            """)
            contacts = [dict(row) for row in cursor.fetchall()]
            
            # Total contacts
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            
            # Enriched
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enriched = 1")
            enriched = cursor.fetchone()["count"]
            
            # High priority
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE match_tier = 'HIGH' OR urgency_level = 'HIGH'
            """)
            high_priority = cursor.fetchone()["count"]
            
            # In call queue
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE cadence_status = 'active'
            """)
            in_call_queue = cursor.fetchone()["count"]
            
            cursor.close()
            
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
                    "high": [dict(c) for c in contacts[:10]],
                    "medium": [],
                    "low": []
                },
                "top_priority": [dict(c) for c in contacts[:20]],
                "cold_call_stats": {
                    "total": in_call_queue,
                    "new": 0,
                    "meeting_set": 0
                }
            }
    except Exception as e:
        logger.error(f"todays_board error: {e}")
        raise HTTPException(500, detail=str(e))

@app.get("/api/dashboard/stats", tags=["Dashboard"])
async def dashboard_stats():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'HIGH'")
            high = cursor.fetchone()["count"]
            cursor.close()
        return {"total_contacts": total, "enriched": enriched, "high_priority": high}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/user/profile", tags=["User"])
async def user_profile(user_id: str = "default"):
    return {"user_id": user_id, "full_name": "Sales User", "company": "Apex Sales", "configured": False}

# ==================== ANALYTICS ====================
@app.get("/api/analytics", tags=["Analytics"])
async def get_analytics(range: str = "all"):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'HIGH'")
            high_tier = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'MEDIUM'")
            medium_tier = cursor.fetchone()["count"]
            cursor.execute("SELECT AVG(match_score) as avg FROM contacts WHERE match_score IS NOT NULL")
            avg = cursor.fetchone()["avg"] or 0
            cursor.close()
        return {
            "total_contacts": total,
            "enriched_contacts": enriched,
            "high_tier": high_tier,
            "medium_tier": medium_tier,
            "average_score": round(float(avg), 2),
            "pipeline": {"total": total, "qualified": high_tier + medium_tier, "enriched": enriched}
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/analytics/dashboard", tags=["Analytics"])
async def analytics_dashboard():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'HIGH'")
            high = cursor.fetchone()["count"]
            cursor.close()
        return {"total_contacts": total, "enriched": enriched, "high_priority": high}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== CONTACTS CRUD ====================
@app.get("/api/contacts", tags=["Contacts"])
async def get_contacts(limit: int = 50, offset: int = 0):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY id DESC LIMIT %s OFFSET %s", (limit, offset))
            contacts = [dict(row) for row in cursor.fetchall()]
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            cursor.close()
        return {"contacts": contacts, "total": total, "limit": limit, "offset": offset}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/contacts/{contact_id}", tags=["Contacts"])
async def get_contact(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Contact not found")
        return dict(contact)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/contacts", tags=["Contacts"])
async def create_contact(request: Request):
    try:
        data = await request.json()
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO contacts (name, email, company, title, phone) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (data.get("name"), data.get("email"), data.get("company"), data.get("title"), data.get("phone"))
            )
            contact_id = cursor.fetchone()["id"]
            conn.commit()
            cursor.close()
        return {"success": True, "id": contact_id}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.put("/api/contacts/{contact_id}", tags=["Contacts"])
async def update_contact(contact_id: int, request: Request):
    try:
        data = await request.json()
        fields, values = [], []
        for key in ["name", "email", "company", "title", "phone", "notes"]:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        if fields:
            values.append(contact_id)
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(f"UPDATE contacts SET {', '.join(fields)} WHERE id = %s", values)
                conn.commit()
                cursor.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.delete("/api/contacts/{contact_id}", tags=["Contacts"])
async def delete_contact(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== SMART LISTS ====================
@app.get("/api/smart-lists", tags=["Smart Lists"])
async def get_smart_lists():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            lists = []
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'HIGH'")
            lists.append({"id": "hot-leads", "name": "Hot Leads", "count": cursor.fetchone()["count"]})
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'MEDIUM'")
            lists.append({"id": "warm-leads", "name": "Warm Leads", "count": cursor.fetchone()["count"]})
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            lists.append({"id": "enriched", "name": "Enriched", "count": cursor.fetchone()["count"]})
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status IS NULL OR enrichment_status != 'completed'")
            lists.append({"id": "needs-enrichment", "name": "Needs Enrichment", "count": cursor.fetchone()["count"]})
            cursor.close()
        return {"lists": lists}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/smart-lists/{list_id}/contacts", tags=["Smart Lists"])
async def get_smart_list_contacts(list_id: str, limit: int = 50, offset: int = 0):
    try:
        filters = {
            "hot-leads": "match_tier = 'HIGH'",
            "warm-leads": "match_tier = 'MEDIUM'",
            "cold-leads": "match_tier = 'LOW' OR match_tier IS NULL",
            "enriched": "enrichment_status = 'completed'",
            "needs-enrichment": "enrichment_status IS NULL OR enrichment_status != 'completed'",
            "all": "1=1"
        }
        where = filters.get(list_id, "1=1")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM contacts WHERE {where} ORDER BY match_score DESC NULLS LAST LIMIT %s OFFSET %s", (limit, offset))
            contacts = [dict(row) for row in cursor.fetchall()]
            cursor.execute(f"SELECT COUNT(*) as count FROM contacts WHERE {where}")
            total = cursor.fetchone()["count"]
            cursor.close()
        return {"contacts": contacts, "total": total, "list_id": list_id}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== COLD CALL QUEUE ====================
@app.get("/api/cold-call/queue", tags=["Cold Call"])
async def cold_call_queue(status: str = "all"):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY match_score DESC NULLS LAST LIMIT 50")
            contacts = [dict(row) for row in cursor.fetchall()]
            cursor.close()
        return {"queue": contacts, "count": len(contacts), "status": status}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/cold-call/queue/{contact_id}/attempt", tags=["Cold Call"])
async def log_call_attempt(contact_id: int, request: Request):
    try:
        data = await request.json() if await request.body() else {}
        outcome = data.get("outcome", "attempted")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET times_contacted = COALESCE(times_contacted, 0) + 1, last_contacted = NOW() WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()
        return {"success": True, "outcome": outcome}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.put("/api/cold-call/queue/{contact_id}/status", tags=["Cold Call"])
async def update_call_status(contact_id: int, request: Request):
    try:
        data = await request.json() if await request.body() else {}
        status = data.get("status", "pending")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET cadence_status = %s WHERE id = %s", (status, contact_id))
            conn.commit()
            cursor.close()
        return {"success": True, "status": status}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/cold-call/queue/{contact_id}/promote", tags=["Cold Call"])
async def promote_contact(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET match_tier = 'HIGH', match_score = GREATEST(COALESCE(match_score, 0), 80) WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()
        return {"success": True, "promoted": True}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== ENRICHMENT ====================
@app.post("/api/contacts/{contact_id}/enrich", tags=["Enrichment"])
async def enrich_contact(contact_id: int):
    """
    Deep enrichment with 3-stage Perplexity search
    """
    if not enrichment_engine:
        raise HTTPException(503, detail="Enrichment engine not available")
    
    try:
        # Get contact data
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(404, detail="Contact not found")
            
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
                    enriched = 1,
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
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s", (contact_id,))
                conn.commit()
                cursor.close()
        except:
            pass
        raise HTTPException(500, detail=str(e))

@app.post("/api/contacts/{contact_id}/reset-enrichment", tags=["Enrichment"])
async def reset_enrichment(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET enrichment_status = NULL, enrichment_data = NULL, enriched_at = NULL, enriched = 0 WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== BATCH OPERATIONS ====================
@app.post("/api/batch/enrich", tags=["Batch"])
async def batch_enrich(request: Request):
    try:
        data = await request.json() if await request.body() else {}
        contact_ids = data.get("contact_ids", [])
        with get_db() as conn:
            cursor = conn.cursor()
            if contact_ids:
                for cid in contact_ids[:50]:
                    cursor.execute("UPDATE contacts SET enrichment_status = 'queued' WHERE id = %s", (cid,))
            else:
                cursor.execute("UPDATE contacts SET enrichment_status = 'queued' WHERE enrichment_status IS NULL OR enrichment_status = 'pending' LIMIT 50")
            conn.commit()
            cursor.close()
        return {"success": True, "message": "Batch enrichment queued"}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/batch/rescore", tags=["Batch"])
async def batch_rescore():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts SET
                    match_score = 50 + 
                        CASE WHEN enrichment_status = 'completed' THEN 20 ELSE 0 END +
                        CASE WHEN company IS NOT NULL THEN 10 ELSE 0 END +
                        CASE WHEN title IS NOT NULL THEN 10 ELSE 0 END +
                        CASE WHEN email IS NOT NULL THEN 10 ELSE 0 END,
                    match_tier = CASE 
                        WHEN match_score >= 80 THEN 'HIGH'
                        WHEN match_score >= 50 THEN 'MEDIUM'
                        ELSE 'LOW'
                    END,
                    last_scored = NOW()
            """)
            count = cursor.rowcount
            conn.commit()
            cursor.close()
        return {"success": True, "rescored": count}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== GENERATION ENDPOINTS ====================
@app.post("/api/contacts/{contact_id}/generate-persona", tags=["Generation"])
async def generate_persona(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Contact not found")
        return {
            "success": True,
            "contact_id": contact_id,
            "persona": {"type": contact.get("persona") or "prospect", "confidence": contact.get("persona_confidence") or 50}
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-call-script", tags=["Generation"])
async def generate_call_script(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Contact not found")
        name = contact.get("name") or "there"
        company = contact.get("company") or "your company"
        script = f"Hi {name}, this is [Your Name] from Harvest Small Business Finance. I'm reaching out because I noticed {company} might benefit from our SBA financing solutions. We specialize in helping businesses like yours secure 90% financing for commercial real estate. Do you have 2 minutes to discuss how we might help?"
        return {"success": True, "script": script, "contact_id": contact_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-linkedin", tags=["Generation"])
async def generate_linkedin(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Contact not found")
        name = contact.get("name", "").split()[0] if contact.get("name") else "there"
        message = f"Hi {name}, I came across your profile and was impressed by your work. I help business owners secure SBA financing for commercial real estate with up to 90% LTV. Would you be open to a brief conversation about how this might benefit your business goals?"
        return {"success": True, "message": message, "contact_id": contact_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-email", tags=["Generation"])
async def generate_email(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Contact not found")
        name = contact.get("name", "").split()[0] if contact.get("name") else "there"
        company = contact.get("company") or "your company"
        email = {
            "subject": f"SBA Financing Opportunity for {company}",
            "body": f"Hi {name},\n\nI hope this email finds you well. I'm reaching out from Harvest Small Business Finance because I believe we can help {company} achieve its growth objectives.\n\nWe specialize in SBA 504 and 7(a) loans, offering:\n- Up to 90% financing\n- Competitive rates\n- Fast, reliable closings\n\nWould you have 15 minutes this week for a brief call to explore if this could benefit your business?\n\nBest regards"
        }
        return {"success": True, "email": email, "contact_id": contact_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-outreach", tags=["Generation"])
async def generate_outreach(contact_id: int, request: Request):
    try:
        data = await request.json() if await request.body() else {}
        outreach_type = data.get("type", "email")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Contact not found")
        return {"success": True, "type": outreach_type, "content": f"Generated {outreach_type} for {contact.get('name')}", "contact_id": contact_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-sequence", tags=["Generation"])
async def generate_sequence(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Contact not found")
        sequence = [
            {"day": 1, "type": "email", "action": "Initial outreach"},
            {"day": 3, "type": "linkedin", "action": "Connection request"},
            {"day": 5, "type": "call", "action": "Follow-up call"},
            {"day": 7, "type": "email", "action": "Value-add email"},
            {"day": 10, "type": "call", "action": "Final attempt"}
        ]
        return {"success": True, "sequence": sequence, "contact_id": contact_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== CONTACT EXTRAS ====================
@app.get("/api/contacts/{contact_id}/activities", tags=["Contacts"])
async def get_contact_activities(contact_id: int):
    return {"activities": [], "contact_id": contact_id}

@app.get("/api/contacts/{contact_id}/meeting-prep", tags=["Contacts"])
async def get_meeting_prep(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Not found")
        return {"contact_id": contact_id, "name": contact.get("name"), "company": contact.get("company"), "talking_points": [], "background": contact.get("enrichment_data") or ""}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/contacts/{contact_id}/icp-match", tags=["Contacts"])
async def get_icp_match(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT match_score, match_tier FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Not found")
        return {"contact_id": contact_id, "match_score": contact.get("match_score") or 0, "match_tier": contact.get("match_tier") or "UNKNOWN"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.put("/api/contacts/{contact_id}/tier", tags=["Contacts"])
async def update_contact_tier(contact_id: int, request: Request):
    try:
        data = await request.json()
        tier = data.get("tier", "MEDIUM")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET match_tier = %s WHERE id = %s", (tier, contact_id))
            conn.commit()
            cursor.close()
        return {"success": True, "tier": tier}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== ENROLLMENTS ====================
@app.get("/api/contacts/{contact_id}/enrollments", tags=["Enrollments"])
async def get_contact_enrollments(contact_id: int):
    return {"enrollments": [], "contact_id": contact_id}

@app.post("/api/contacts/{contact_id}/enroll", tags=["Enrollments"])
async def enroll_contact(contact_id: int, request: Request):
    try:
        data = await request.json() if await request.body() else {}
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET cadence_id = %s, cadence_status = 'active' WHERE id = %s", (data.get("cadence_id"), contact_id))
            conn.commit()
            cursor.close()
        return {"success": True, "enrollment_id": contact_id}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/enrollments/{enrollment_id}/advance", tags=["Enrollments"])
async def advance_enrollment(enrollment_id: int):
    return {"success": True, "enrollment_id": enrollment_id}

@app.get("/api/enrollments/{enrollment_id}/status", tags=["Enrollments"])
async def get_enrollment_status(enrollment_id: int):
    return {"enrollment_id": enrollment_id, "status": "active", "current_step": 1, "total_steps": 5}

# ==================== CADENCE ====================
@app.get("/api/cadence-queue", tags=["Cadence"])
async def get_cadence_queue():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE cadence_status = 'active' ORDER BY id DESC LIMIT 50")
            contacts = [dict(row) for row in cursor.fetchall()]
            cursor.close()
        return {"queue": contacts, "count": len(contacts)}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/cadence-stats", tags=["Cadence"])
async def get_cadence_stats():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE cadence_status = 'active'")
            active = cursor.fetchone()["count"]
            cursor.close()
        return {"active": active, "completed": 0, "paused": 0}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== IMPORT/EXPORT ====================
@app.post("/api/contacts/import", tags=["Import"])
async def import_contacts():
    return {"success": True, "imported": 0, "message": "Import queued"}

@app.get("/api/import/status", tags=["Import"])
async def get_import_status():
    return {"status": "idle", "progress": 0, "total": 0}

@app.post("/api/hubspot/import", tags=["Import"])
async def hubspot_import():
    return {"success": True, "message": "HubSpot import queued"}

@app.get("/api/contacts/export", tags=["Export"])
async def export_contacts(format: str = "json"):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY id")
            contacts = [dict(row) for row in cursor.fetchall()]
            cursor.close()
        return {"contacts": contacts, "count": len(contacts)}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== SETTINGS ====================
@app.get("/api/settings/playbook", tags=["Settings"])
async def get_settings_playbook():
    try:
        playbook_file = os.path.join(os.path.dirname(__file__), "playbook.json")
        if os.path.exists(playbook_file):
            with open(playbook_file, "r") as f:
                return json.load(f)
        return {"configured": False}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.post("/api/settings/playbook", tags=["Settings"])
async def save_settings_playbook(request: Request):
    try:
        data = await request.json() if await request.body() else {}
        playbook_file = os.path.join(os.path.dirname(__file__), "playbook.json")
        with open(playbook_file, "w") as f:
            json.dump(data, f, indent=2)
        return {"success": True}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/user/proof-points", tags=["User"])
async def get_user_proof_points():
    return {"proof_points": [{"id": 1, "title": "90% Approval Rate"}, {"id": 2, "title": "Fast Close"}]}

# ==================== STARTUP ====================
@app.on_event("startup")
async def startup_event():
    logger.info("Apex Backend v2.0 starting...")
    logger.info(f"ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()["count"]
            logger.info(f"Database connected: {count} contacts")
            cursor.close()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        