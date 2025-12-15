from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import json
import sqlite3
import sys
from pathlib import Path

# Add services to path
BACKEND_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from services.intelligence_service import IntelligenceService

router = APIRouter(prefix="/api/v1/outreach", tags=["Outreach"])

# Initialize intelligence service
intelligence = IntelligenceService('./apex.db')

# ═══════════════════════════════════════════════════════════════
# ENRICHMENT
# ═══════════════════════════════════════════════════════════════

@router.post("/contacts/{contact_id}/deep-enrich")
async def deep_enrich_contact(contact_id: int, background_tasks: BackgroundTasks):
    """Deep enrichment using Perplexity AI"""
    try:
        conn = sqlite3.connect('./apex.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, first_name, last_name, email, company, title, linkedin_url 
            FROM contacts WHERE id = ?
        """, (contact_id,))
        
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        contact_data = {
            'first_name': contact[1],
            'last_name': contact[2],
            'email': contact[3],
            'company': contact[4],
            'title': contact[5],
            'linkedin_url': contact[6]
        }
        
        # Run enrichment in background
        background_tasks.add_task(
            intelligence.enrich_contact_deep,
            contact_id=contact_id,
            contact_data=contact_data
        )
        
        return {
            "status": "enrichment_started",
            "contact_id": contact_id,
            "message": "AI enrichment running in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# CALL SCRIPTS
# ═══════════════════════════════════════════════════════════════

@router.post("/contacts/{contact_id}/call-scripts")
async def generate_call_scripts(contact_id: int):
    """Generate 3 DISC-optimized call script variants"""
    result = intelligence.generate_call_scripts(contact_id)
    
    if result['status'] == 'error':
        raise HTTPException(status_code=400, detail=result['message'])
    
    return result

# ═══════════════════════════════════════════════════════════════
# KERNEL INTELLIGENCE
# ═══════════════════════════════════════════════════════════════

@router.get("/contacts/{contact_id}/kernel-intelligence")
async def get_kernel_intelligence(contact_id: int):
    """Get WHO/WHEN/WHAT intelligence"""
    try:
        conn = sqlite3.connect('./apex.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT first_name, last_name, company, title, enrichment_data
            FROM contacts WHERE id = ?
        """, (contact_id,))
        
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        enrichment = json.loads(contact[4]) if contact[4] else {}
        contact_data = {
            'name': f"{contact[0]} {contact[1]}",
            'company': contact[2],
            'title': contact[3],
            'recent_activity': enrichment.get('recent_news', '').split('\n')[:3]
        }
        
        result = intelligence.get_kernel_intelligence(contact_data)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════════════════════════════════
# SEQUENCES
# ═══════════════════════════════════════════════════════════════

@router.post("/contacts/{contact_id}/sequences/start")
async def start_sequence(contact_id: int, sequence_type: str = 'standard'):
    """Start automated sequence (aggressive/standard/nurture)"""
    result = intelligence.start_sequence(contact_id, sequence_type)
    
    if result.get('status') == 'error':
        raise HTTPException(status_code=400, detail=result.get('message'))
    
    return result

@router.get("/sequences/active")
async def get_active_sequences():
    """Get all active sequences"""
    sequences = intelligence.get_active_sequences()
    return {
        "status": "success",
        "count": len(sequences),
        "sequences": sequences
    }

@router.get("/sequences/pending-touches")
async def get_pending_touches():
    """Get pending touches"""
    touches = intelligence.get_pending_touches()
    return {
        "status": "success",
        "count": len(touches),
        "touches": touches
    }

# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════

@router.get("/intelligence/summary")
async def get_intelligence_summary():
    """Get complete intelligence summary"""
    summary = intelligence.get_dashboard_summary()
    return {
        "status": "success",
        "summary": summary
    }
