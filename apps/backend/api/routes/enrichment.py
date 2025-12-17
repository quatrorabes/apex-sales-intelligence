"""
Apex Enrichment Routes - With Debug Logging
PostgreSQL Compatible + Single Contact Limit + Debug Files
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import logging
import json
import os
import sys
from datetime import datetime

logger = logging.getLogger(__name__)

# NO PREFIX - explicit paths
router = APIRouter(tags=["enrichment"])

# Add path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import engine
try:
    from enrichment_engine import EnhancedEnrichment
    enrichment_engine = EnhancedEnrichment()
    ENGINE_AVAILABLE = True
    logger.info("✅ EnhancedEnrichment loaded")
except ImportError as e:
    logger.error(f"❌ Engine import failed: {e}")
    enrichment_engine = None
    ENGINE_AVAILABLE = False

# Import parser
try:
    from services.enrichment_integration import integrate_enrichment_result
    PARSER_AVAILABLE = True
    logger.info("✅ Parser loaded")
except ImportError as e:
    logger.warning(f"⚠️ Parser not available: {e}")
    PARSER_AVAILABLE = False

# Database (PostgreSQL)
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_db():
    """PostgreSQL connection context manager"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


def save_debug_file(filename: str, content: str, contact_id: int):
    """Save debug output to file for testing"""
    try:
        debug_dir = "/tmp/apex_debug"
        os.makedirs(debug_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{debug_dir}/contact_{contact_id}_{filename}_{timestamp}.txt"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"📝 Debug file saved: {filepath}")
        return filepath
    except Exception as e:
        logger.warning(f"Could not save debug file: {e}")
        return None


def enrich_contact_internal(contact_id: int) -> Dict[str, Any]:
    """
    Enrichment with debug logging and file output
    """
    
    if not ENGINE_AVAILABLE:
        logger.error("Engine not available")
        return {
            "success": False,
            "contactId": contact_id,
            "status": "error",
            "error": "Enrichment engine not available"
        }
    
    try:
        # 1. Fetch contact (PostgreSQL compatible)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
        
        if not contact:
            logger.error(f"Contact {contact_id} not found")
            return {
                "success": False,
                "contactId": contact_id,
                "status": "error",
                "error": f"Contact {contact_id} not found"
            }
        
        contact_dict = dict(contact)
        contact_name = contact_dict.get('name', 'Unknown')
        
        logger.info(f"🚀 Starting enrichment for contact {contact_id}: {contact_name}")
        
        # 2. Call proven engine (PRESERVES ALL PERPLEXITY + GPT-4 LOGIC)
        enrichment_result = enrichment_engine.enrich_contact(contact_dict)
        
        # DEBUG: Save raw engine result
        try:
            raw_result_json = json.dumps(enrichment_result, indent=2, default=str)
            save_debug_file("01_engine_raw_result", raw_result_json, contact_id)
        except:
            pass
        
        # Check engine success
        if not enrichment_result.get("success"):
            error_msg = enrichment_result.get("error", "Enrichment failed")
            logger.error(f"❌ Engine returned failure: {error_msg}")
            
            # Mark as failed (PostgreSQL)
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contacts SET enrichment_status = %s WHERE id = %s",
                    ('failed', contact_id)
                )
                conn.commit()
                cursor.close()
            
            return {
                "success": False,
                "contactId": contact_id,
                "status": "error",
                "error": error_msg
            }
        
        # 3. Extract Perplexity + GPT-4 output
        raw_profile = enrichment_result.get("profile_text", "")
        
        if not raw_profile:
            logger.warning(f"Empty profile_text for contact {contact_id}")
            raw_profile = ""
        
        logger.info(f"📊 AFTER PERPLEXITY + GPT-4: {len(raw_profile)} characters")
        
        # DEBUG: Save Perplexity + OpenAI combined output
        save_debug_file("02_after_perplexity_and_openai", raw_profile, contact_id)
        
        # Show first 500 chars in logs
        preview = raw_profile[:500] if raw_profile else "(empty)"
        logger.info(f"Preview of enrichment output:\n{preview}\n...")
        
        # 4. Parse output (post-processing)
        if PARSER_AVAILABLE and raw_profile:
            try:
                enrichment_object = integrate_enrichment_result(raw_profile)
                sections_count = len(enrichment_object.get('sections', {}))
                logger.info(f"✅ Parsed into {sections_count} sections")
                
                # DEBUG: Save parsed output
                parsed_json = json.dumps(enrichment_object, indent=2)
                save_debug_file("03_after_parsing", parsed_json, contact_id)
                
            except Exception as parse_error:
                logger.warning(f"Parser failed: {parse_error}, saving raw")
                enrichment_object = {
                    "sections": {"raw_text": raw_profile},
                    "metadata": {
                        "format_detected": "raw",
                        "total_sections": 1,
                        "character_count": len(raw_profile)
                    }
                }
        else:
            # No parser, save raw
            enrichment_object = {
                "sections": {"raw_text": raw_profile},
                "metadata": {
                    "format_detected": "raw",
                    "total_sections": 1,
                    "character_count": len(raw_profile)
                }
            }
        
        # 5. Save to PostgreSQL database
        enrichment_json = json.dumps(enrichment_object)
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE contacts 
                SET enrichment_status = %s,
                    enriched_at = NOW(),
                    enrichment_data = %s
                WHERE id = %s
                """,
                ('completed', enrichment_json, contact_id)
            )
            conn.commit()
            cursor.close()
        
        logger.info(f"✅ Enrichment complete for contact {contact_id}")
        logger.info(f"📂 Debug files saved to /tmp/apex_debug/contact_{contact_id}_*.txt")
        
        return {
            "success": True,
            "contactId": contact_id,
            "status": "completed",
            "sections": len(enrichment_object.get("sections", {})),
            "format": enrichment_object.get("metadata", {}).get("format_detected", "unknown"),
            "characterCount": len(raw_profile),
            "debugFiles": f"/tmp/apex_debug/contact_{contact_id}_*"
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
                    "UPDATE contacts SET enrichment_status = %s WHERE id = %s",
                    ('failed', contact_id)
                )
                conn.commit()
                cursor.close()
        except Exception as db_error:
            logger.error(f"Could not update DB status: {db_error}")
        
        return {
            "success": False,
            "contactId": contact_id,
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/api/batch/enrich")
async def batch_enrich(limit: int = Query(1, ge=1, le=1)):
    """
    Batch enrichment - LIMIT 1 for testing
    
    Path: POST /api/batch/enrich?limit=1
    """
    
    if not ENGINE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Enrichment engine not available"
        )
    
    try:
        # Find unenriched contacts (PostgreSQL compatible)
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
            rows = cursor.fetchall()
            targets = [row["id"] for row in rows]
            cursor.close()
        
        if not targets:
            logger.info("No contacts to enrich")
            return {
                "status": "complete",
                "message": "No contacts to enrich",
                "processed": 0,
                "successful": 0,
                "failed": 0
            }
        
        logger.info(f"🔄 Batch enriching {len(targets)} contact(s): {targets}")
        
        # Enrich (one at a time for testing)
        results = []
        for contact_id in targets:
            logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"Starting enrichment for contact {contact_id}")
            logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            result = enrich_contact_internal(contact_id)
            results.append(result)
            
            logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            logger.info(f"Completed enrichment for contact {contact_id}")
            logger.info(f"Result: {result}")
            logger.info(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        logger.info(f"✅ Batch complete: {successful}/{len(results)} successful")
        
        return {
            "status": "complete",
            "processed": len(results),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    except Exception as e:
        logger.error(f"❌ Batch enrich failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/contacts/{contact_id}/enrich")
async def enrich_single_contact(contact_id: int):
    """Single contact enrichment with debug output"""
    result = enrich_contact_internal(contact_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Enrichment failed")
        )
    
    return result


@router.get("/api/contacts/{contact_id}/enrichment-status")
async def get_enrichment_status(contact_id: int):
    """Check enrichment status (PostgreSQL compatible)"""
    
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
        
        # Include metadata
        if row["enrichment_data"]:
            try:
                enrichment = json.loads(row["enrichment_data"]) if isinstance(row["enrichment_data"], str) else row["enrichment_data"]
                
                if isinstance(enrichment, dict):
                    sections = enrichment.get("sections", {})
                    metadata = enrichment.get("metadata", {})
                    
                    response["sectionsCount"] = len(sections)
                    response["formatDetected"] = metadata.get("format_detected", "unknown")
                    response["totalSections"] = metadata.get("total_sections", len(sections))
                    response["characterCount"] = metadata.get("character_count", 0)
            except Exception as e:
                logger.warning(f"Could not parse enrichment_data: {e}")
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
