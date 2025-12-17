"""
APEX Enrichment v2 Routes
Uses Orchestrator for 3-stage enrichment
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import logging
from datetime import datetime

from services.enrichment_orchestrator_v2 import ApexEnrichmentOrchestrator

router = APIRouter(tags=['enrichment_v2'])
enrichment_engine = ApexEnrichmentOrchestrator()
logger = logging.getLogger(__name__)

class EnrichContactRequest(BaseModel):
    contact_id: str
    name: str
    company: str
    title: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None

@router.post('/api/v2/contacts/{contact_id}/enrich')
async def enrich_contact_v2(contact_id: str):
    """
    Trigger 3-stage enrichment
    - Stage 1: Perplexity open-ended research
    - Stage 2: GPT-4 markdown synthesis
    - Stage 3: Frontend parses markdown → sections
    """
    try:
        # Fetch contact from DB
        from contextlib import contextmanager
        import psycopg2
        
        # Get DB connection (your existing pattern)
        DATABASEURL = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(DATABASEURL)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, name, company, title, email, linkedin_url FROM contacts WHERE id = %s",
            (contact_id,)
        )
        contact_row = cursor.fetchone()
        cursor.close()
        
        if not contact_row:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Map to dict
        contact = {
            'id': contact_row[0],
            'name': contact_row[1],
            'company': contact_row[2],
            'title': contact_row[3],
            'email': contact_row[4],
            'linkedin_url': contact_row[5]
        }
        
        # Run enrichment
        logger.info(f"Enriching {contact['name']}...")
        result = enrichment_engine.enrich_contact(contact)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result.get('error'))
        
        # Save to DB
        enrichment_json = json.dumps({
            'version': '3.0',
            'markdown': result['markdown'],
            'raw_context': result['raw_context'],
            'enriched_at': result['metadata']['enriched_at']
        })
        
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE contacts 
            SET enrichment_status = %s,
                enrichment_data = %s::jsonb,
                enriched_at = %s
            WHERE id = %s
            """,
            ('completed', enrichment_json, datetime.now().isoformat(), contact_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Enrichment saved for {contact['name']}")
        
        return {
            'success': True,
            'contact_id': contact_id,
            'enrichment_status': 'completed',
            'markdown_length': len(result['markdown'])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrichment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
