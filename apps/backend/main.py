#!/usr/bin/env python3
"""
Apex Sales Intelligence Backend - Production v2.0
"""

import os
import logging
import sys
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL required")

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = RealDictCursor
    try:
        yield conn
    finally:
        conn.close()

app = FastAPI(title="Apex Sales Intelligence API", version="2.0")

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

# Load enrichment engine
sys.path.insert(0, str(Path(__file__).parent / 'intelligence' / 'engines' / 'enrichment'))
enrichment_engine = None
try:
    from enhanced_enrichment import EnhancedEnrichment
    enrichment_engine = EnhancedEnrichment()
    logger.info("✅ Enrichment engine loaded")
except Exception as e:
    logger.warning(f"⚠️ Enrichment engine unavailable: {e}")

# ==================== SYSTEM ====================

@app.get("/")
async def root():
    return {"status": "running", "service": "apex-backend", "version": "2.0"}

@app.get("/health")
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
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/debug/env")
async def debug_env():
    return {
        "DATABASE_URL": "✅" if os.getenv("DATABASE_URL") else "❌",
        "OPENAI_API_KEY": "✅" if os.getenv("OPENAI_API_KEY") else "❌",
        "PERPLEXITY_API_KEY": "✅" if os.getenv("PERPLEXITY_API_KEY") else "❌",
        "enrichment_engine": "✅" if enrichment_engine else "❌"
    }

# ==================== DASHBOARD ====================

@app.get("/api/todays-board")
async def todays_board():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY COALESCE(match_score, 0) DESC LIMIT 20")
            contacts = [dict(r) for r in cursor.fetchall()]
            cursor.execute("SELECT COUNT(*) as c FROM contacts")
            total = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) as c FROM contacts WHERE enriched = 1")
            enriched = cursor.fetchone()["c"]
            cursor.close()
        return {
            "success": True,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "stats": {"total_contacts": total, "enriched": enriched},
            "top_priority": contacts
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/user/profile")
async def user_profile(user_id: str = "default"):
    return {"user_id": user_id, "full_name": "Sales User"}

# ==================== CONTACTS ====================

@app.get("/api/contacts")
async def get_contacts(limit: int = 50, offset: int = 0):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts ORDER BY id DESC LIMIT %s OFFSET %s", (limit, offset))
            contacts = [dict(r) for r in cursor.fetchall()]
            cursor.execute("SELECT COUNT(*) as c FROM contacts")
            total = cursor.fetchone()["c"]
            cursor.close()
        return {"contacts": contacts, "total": total}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: int):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        if not contact:
            raise HTTPException(404, detail="Not found")
        return dict(contact)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== ENRICHMENT (THE KEY ROUTES) ====================

@app.post("/api/contacts/{contact_id}/enrich")
async def enrich_contact(contact_id: int):
    """Enrich a contact with AI profile data"""
    if not enrichment_engine:
        raise HTTPException(503, detail="Enrichment engine unavailable")
    
    try:
        # Get contact
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(404, detail="Contact not found")
            cursor.execute("UPDATE contacts SET enrichment_status = 'enriching' WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()
        
        contact_dict = dict(contact)
        logger.info(f"🚀 Enriching {contact_dict.get('name')} (ID: {contact_id})")
        
        # Run enrichment
        result = enrichment_engine.enrich_contact(contact_dict)
        profile_text = result.get('profile_text', '')
        
        # Parse sections
        sections = {"overview": "", "background": "", "company_info": "", "sales_opportunities": ""}
        current_section = "overview"
        for line in profile_text.split('\n'):
            if line.startswith('## '):
                section_name = line.replace('##', '').strip().lower()
                if 'overview' in section_name:
                    current_section = 'overview'
                elif 'background' in section_name or 'experience' in section_name:
                    current_section = 'background'
                elif 'company' in section_name or 'organization' in section_name:
                    current_section = 'company_info'
                elif 'sales' in section_name or 'opportunity' in section_name:
                    current_section = 'sales_opportunities'
            else:
                sections[current_section] += line + '\n'
        
        # Save to database
        enrichment_json = json.dumps({
            'profile_text': profile_text,
            'sections': sections,
            'character_count': len(profile_text),
            'enriched_at': datetime.now().isoformat(),
            'success': True
        })
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts SET
                    enrichment_status = 'completed',
                    enriched_at = NOW(),
                    enrichment_data = %s,
                    enriched = 1,
                    match_score = COALESCE(match_score, 0) + 20
                WHERE id = %s
            """, (enrichment_json, contact_id))
            conn.commit()
            cursor.close()
        
        logger.info(f"✅ Enrichment completed for {contact_id}")
        
        return {
            "success": True,
            "contact_id": contact_id,
            "enrichment": {
                "status": "completed",
                "profile_length": len(profile_text),
                "sections": {
                    "overview": sections["overview"][:500] + "..." if len(sections["overview"]) > 500 else sections["overview"],
                    "background": sections["background"][:500] + "..." if len(sections["background"]) > 500 else sections["background"],
                    "company_info": sections["company_info"][:500] + "..." if len(sections["company_info"]) > 500 else sections["company_info"],
                    "sales_opportunities": sections["sales_opportunities"][:500] + "..." if len(sections["sales_opportunities"]) > 500 else sections["sales_opportunities"]
                },
                "full_profile_available": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Enrichment error: {e}")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()
        raise HTTPException(500, detail=str(e))

@app.get("/api/contacts/{contact_id}/enrichment")
async def get_enrichment_data(contact_id: int):
    """Get enrichment data for a contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT enrichment_data, enrichment_status, enriched_at FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        
        if not contact:
            raise HTTPException(404, detail="Contact not found")
        
        if not contact.get("enrichment_data"):
            return {
                "success": False,
                "status": contact.get("enrichment_status") or "not_enriched",
                "message": "Not enriched yet"
            }
        
        enrichment_data = json.loads(contact["enrichment_data"]) if isinstance(contact["enrichment_data"], str) else contact["enrichment_data"]
        
        return {
            "success": True,
            "contact_id": contact_id,
            "status": contact.get("enrichment_status"),
            "enriched_at": contact.get("enriched_at").isoformat() if contact.get("enriched_at") else None,
            "profile": enrichment_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== SMART LISTS ====================

@app.get("/api/smart-lists")
async def get_smart_lists():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as c FROM contacts WHERE match_tier = 'HIGH'")
            high = cursor.fetchone()["c"]
            cursor.execute("SELECT COUNT(*) as c FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["c"]
            cursor.close()
        return {"lists": [
            {"id": "hot-leads", "name": "Hot Leads", "count": high},
            {"id": "enriched", "name": "Enriched", "count": enriched}
        ]}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

@app.get("/api/smart-lists/{list_id}/contacts")
async def get_smart_list_contacts(list_id: str, limit: int = 50):
    try:
        filters = {
            "hot-leads": "match_tier = 'HIGH'",
            "enriched": "enrichment_status = 'completed'",
            "all": "1=1"
        }
        where = filters.get(list_id, "1=1")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM contacts WHERE {where} LIMIT %s", (limit,))
            contacts = [dict(r) for r in cursor.fetchall()]
            cursor.close()
        return {"contacts": contacts, "list_id": list_id}
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup():
    logger.info("Apex Backend v2.0 starting...")
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()["count"]
            logger.info(f"Database connected: {count} contacts")
            cursor.close()
    except Exception as e:
        logger.error(f"Database error: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
