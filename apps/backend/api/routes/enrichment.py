"""APEX Enrichment Routes v3 - Fixed schema validation"""
import os, json, logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, Body
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List

router = APIRouter(tags=['enrichment'])
logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv('DATABASE_URL')

try:
    from engines.intelligence.enrichment.engine_v3 import ApexEnrichmentEngineV3
    enrichment_engine = ApexEnrichmentEngineV3()
except:
    enrichment_engine = None

# Single contact enrichment (v2 endpoint - called from ContactDetail)
@router.post('/api/v2/contacts/{contact_id}/enrich')
async def enrich_single_contact(contact_id: str):
    """Enrich single contact"""
    logger.info(f"POST /api/v2/contacts/{contact_id}/enrich")
    return await enrich_contact_internal(contact_id)

# Batch enrichment
@router.post('/api/batch/enrich')
async def batch_enrich(contact_ids: List[str] = Body(...)):
    """Batch enrich contacts"""
    if not contact_ids:
        raise HTTPException(status_code=400, detail="contact_ids required")
    
    logger.info(f"Batch enriching {len(contact_ids)} contacts")
    results = []
    
    for contact_id in contact_ids:
        try:
            result = await enrich_contact_internal(contact_id)
            results.append(result)
        except Exception as e:
            results.append({'contact_id': contact_id, 'status': 'error', 'error': str(e)})
    
    return {'results': results}

async def enrich_contact_internal(contact_id: str) -> dict:
    """Internal enrichment handler"""
    try:
        if not DATABASE_URL or not enrichment_engine:
            raise HTTPException(status_code=500, detail="Service not ready")
        
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, name, company, title, email, linkedin_url FROM contacts WHERE id = %s",
            (contact_id,)
        )
        contact_row = cursor.fetchone()
        
        if not contact_row:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Contact not found")
        
        contact = dict(contact_row)
        logger.info(f"Enriching: {contact['name']}")
        
        enrichment_result = enrichment_engine.enrich_contact(contact)
        
        if enrichment_result['status'] == 'error':
            cursor.execute("UPDATE contacts SET enrichment_status = %s WHERE id = %s", ('failed', contact_id))
            conn.commit()
            cursor.close()
            conn.close()
            raise HTTPException(status_code=500, detail=enrichment_result['error'])
        
        enrichment_json = json.dumps({
            'version': '3.0',
            'markdown': enrichment_result.get('markdown', ''),
            'raw_context': enrichment_result.get('raw_context', {}),
            'enriched_at': enrichment_result.get('enriched_at', datetime.now().isoformat())
        })
        
        cursor.execute(
            "UPDATE contacts SET enrichment_status = %s, enrichment_data = %s::jsonb, enriched_at = %s WHERE id = %s",
            ('completed', enrichment_json, datetime.now().isoformat(), contact_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Enrichment done: {contact['name']}")
        
        return {
            'success': True,
            'contact_id': contact_id,
            'enrichment_status': 'completed',
            'markdown_length': len(enrichment_result.get('markdown', ''))
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrichment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/v2/contacts/{contact_id}/enrichment-status')
async def get_enrichment_status(contact_id: str):
    """Check enrichment status"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT enrichment_status, enriched_at FROM contacts WHERE id = %s", (contact_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return {
            'enrichment_status': result['enrichment_status'] or 'pending',
            'enriched_at': result['enriched_at']
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
