"""
apps/backend/api/routes/contacts_v2_enrichment.py
APEX Enrichment Routes v2 - WITH PROVEN ENGINES
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import logging
import json
import os
import sys
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/contacts", tags=["enrichment"])

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import parser
try:
    from services.enrichment_integration import integrate_enrichment_result
    PARSER_AVAILABLE = True
    logger.info("✅ Parser loaded")
except ImportError as e:
    logger.error(f"Parser import failed: {e}")
    PARSER_AVAILABLE = False

# Import EnhancedEnrichment
try:
    from intelligence.engines.enrichment.enhanced_enrichment import EnhancedEnrichment
    enrichment_engine = EnhancedEnrichment()
    ENGINE_AVAILABLE = True
    logger.info("✅ EnhancedEnrichment engine loaded")
except ImportError as e:
    logger.error(f"Engine import failed: {e}")
    enrichment_engine = None
    ENGINE_AVAILABLE = False

# Database connection
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def enrich_contact_internal(contact_id: int) -> Dict[str, Any]:
    """
    Complete enrichment pipeline with proven engines.
    
    Flow:
    1. Fetch contact from DB
    2. EnhancedEnrichment (Perplexity + GPT-4)
    3. Parse output with new parser
    4. Save structured JSON to DB
    """
    if not ENGINE_AVAILABLE:
        return {
            "success": False,
            "contactId": contact_id,
            "status": "error",
            "error": "EnhancedEnrichment engine not available"
        }
    
    if not PARSER_AVAILABLE:
        return {
            "success": False,
            "contactId": contact_id,
            "status": "error",
            "error": "Parser not available"
        }
    
    try:
        # 1. Fetch contact
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        
        if not contact:
            return {
                "success": False,
                "contactId": contact_id,
                "status": "error",
                "error": f"Contact {contact_id} not found"
            }
        
        contact_dict = dict(contact)
        
        # 2. Call EnhancedEnrichment (Perplexity 3-stage + GPT-4)
        logger.info(f"🚀 Enriching contact {contact_id}: {contact_dict.get('name')}")
        enrichment_result = enrichment_engine.enrich_contact(contact_dict)
        
        if not enrichment_result.get("success"):
            error_msg = enrichment_result.get("error", "Enrichment failed")
            logger.error(f"❌ Enrichment failed for {contact_id}: {error_msg}")
            
            # Mark as failed in DB
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s",
                    (contact_id,)
                )
                conn.commit()
                cursor.close()
            
            return {
                "success": False,
                "contactId": contact_id,
                "status": "error",
                "error": error_msg
            }
        
        # 3. Parse with new parser
        raw_profile = enrichment_result.get("profile_text", "")
        logger.info(f"📝 Parsing {len(raw_profile)} chars for contact {contact_id}")
        
        enrichment_object = integrate_enrichment_result(raw_profile)
        
        # 4. Save to DB
        enrichment_json = json.dumps(enrichment_object)
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE contacts 
                SET enrichment_status = 'completed',
                    enriched_at = NOW(),
                    enrichment_data = %s
                WHERE id = %s
                """,
                (enrichment_json, contact_id)
            )
            conn.commit()
            cursor.close()
        
        logger.info(f"✅ Enrichment complete for contact {contact_id}")
        
        return {
            "success": True,
            "contactId": contact_id,
            "status": "completed",
            "sections": len(enrichment_object.get("sections", {})),
            "format": enrichment_object.get("metadata", {}).get("format_detected", "unknown"),
            "characterCount": len(raw_profile)
        }
    
    except Exception as e:
        logger.error(f"❌ Enrichment exception for {contact_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Mark as failed
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s",
                    (contact_id,)
                )
                conn.commit()
                cursor.close()
        except:
            pass
        
        return {
            "success": False,
            "contactId": contact_id,
            "status": "error",
            "error": str(e)
        }


# ROUTES

@router.post("/{contact_id}/enrich")
async def enrich_contact(contact_id: int):
    """Enrich single contact"""
    result = enrich_contact_internal(contact_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result


@router.post("/batch/enrich")
async def batch_enrich(limit: int = Query(10, ge=1, le=100)):
    """
    Batch enrich multiple contacts using proven engines.
    """
    if not ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Enrichment engine not available")
    
    try:
        # Find unenriched contacts
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id FROM contacts 
                WHERE enrichment_status IS NULL 
                   OR enrichment_status != 'completed'
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (limit,)
            )
            targets = [row["id"] for row in cursor.fetchall()]
            cursor.close()
        
        if not targets:
            return {
                "status": "complete",
                "message": "No contacts to enrich",
                "processed": 0
            }
        
        logger.info(f"🔄 Batch enriching {len(targets)} contacts...")
        
        # Enrich each contact
        results = []
        for contact_id in targets:
            result = enrich_contact_internal(contact_id)
            results.append(result)
        
        successful = sum(1 for r in results if r["success"])
        
        return {
            "status": "complete",
            "processed": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"❌ Batch enrich failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contact_id}/enrichment-status")
async def get_enrichment_status(contact_id: int):
    """Check enrichment status"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT enrichment_status, enriched_at, enrichment_data 
                FROM contacts 
                WHERE id = %s
                """,
                (contact_id,)
            )
            row = cursor.fetchone()
            cursor.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        response = {
            "contactId": contact_id,
            "enrichmentStatus": row["enrichment_status"] or "pending",
            "enrichedAt": str(row["enriched_at"]) if row["enriched_at"] else None
        }
        
        # Include metadata if enriched
        if row["enrichment_data"]:
            try:
                enrichment = json.loads(row["enrichment_data"]) if isinstance(row["enrichment_data"], str) else row["enrichment_data"]
                if isinstance(enrichment, dict):
                    response["sectionsCount"] = len(enrichment.get("sections", {}))
                    response["formatDetected"] = enrichment.get("metadata", {}).get("format_detected", "unknown")
                    response["totalSections"] = enrichment.get("metadata", {}).get("total_sections", 0)
            except:
                pass
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
