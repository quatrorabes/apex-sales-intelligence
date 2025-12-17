"""
apps/backend/api/routes/enrichment.py
Add /api/v2 prefix support (Dashboard calls this)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import logging
import json
import os
import sys
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(tags=["enrichment"])

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import existing proven engine (UNCHANGED)
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
except ImportError:
    PARSER_AVAILABLE = False

# PostgreSQL
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


def save_debug_file(filename: str, content: str, contact_id: str):
    try:
        debug_dir = "/tmp/apex_debug"
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{debug_dir}/contact_{contact_id}_{filename}_{timestamp}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"📝 {filepath}")
        return filepath
    except Exception as e:
        logger.warning(f"Debug file error: {e}")
        return None


def enrich_contact_internal(contact_id: str) -> Dict[str, Any]:
    """EXISTING ENRICHMENT LOGIC - UNCHANGED"""

    if not ENGINE_AVAILABLE:
        return {"success": False, "contactId": contact_id, "error": "Engine unavailable"}

    try:
        # 1. Fetch contact
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()

        if not contact:
            return {"success": False, "contactId": contact_id, "error": "Contact not found"}

        contact_dict = dict(contact)
        logger.info(f"🚀 Enriching {contact_id}: {contact_dict.get('name')}")

        # 2. Call PROVEN ENGINE (UNCHANGED)
        enrichment_result = enrichment_engine.enrich_contact(contact_dict)

        save_debug_file("01_raw_result", json.dumps(enrichment_result, indent=2, default=str), contact_id)

        if not enrichment_result.get("success"):
            error_msg = enrichment_result.get("error", "Enrichment failed")
            logger.error(f"❌ {error_msg}")

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE contacts SET enrichment_status = %s WHERE id = %s", ('failed', contact_id))
                conn.commit()
                cursor.close()

            return {"success": False, "contactId": contact_id, "error": error_msg}

        # 3. Extract output
        raw_profile = enrichment_result.get("profile_text", "")
        logger.info(f"📊 Got {len(raw_profile)} chars")

        save_debug_file("02_perplexity_openai", raw_profile, contact_id)

        # 4. Parse
        if PARSER_AVAILABLE and raw_profile:
            try:
                enrichment_object = integrate_enrichment_result(raw_profile)
                logger.info(f"✅ Parsed {len(enrichment_object.get('sections', {}))} sections")
                save_debug_file("03_parsed", json.dumps(enrichment_object, indent=2), contact_id)
            except Exception as e:
                logger.warning(f"Parser failed: {e}")
                enrichment_object = {
                    "sections": {"raw_text": raw_profile},
                    "metadata": {"format_detected": "raw", "character_count": len(raw_profile)}
                }
        else:
            enrichment_object = {
                "sections": {"raw_text": raw_profile},
                "metadata": {"format_detected": "raw", "character_count": len(raw_profile)}
            }

        # 5. Save
        enrichment_json = json.dumps(enrichment_object)

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contacts SET enrichment_status = %s, enriched_at = NOW(), enrichment_data = %s WHERE id = %s",
                ('completed', enrichment_json, contact_id)
            )
            conn.commit()
            cursor.close()

        logger.info(f"✅ Complete: {contact_id}")

        return {
            "success": True,
            "contactId": contact_id,
            "status": "completed",
            "sections": len(enrichment_object.get("sections", {})),
            "format": enrichment_object.get("metadata", {}).get("format_detected"),
            "characterCount": len(raw_profile)
        }

    except Exception as e:
        logger.error(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()

        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE contacts SET enrichment_status = %s WHERE id = %s", ('failed', contact_id))
                conn.commit()
                cursor.close()
        except:
            pass

        return {"success": False, "contactId": contact_id, "error": str(e)}


# ============================================================================
# ROUTES - THE ONLY THING THAT CHANGES
# Add /api/v2 routes that Dashboard expects
# ============================================================================

# NEW: Dashboard calls this
@router.post("/api/v2/contacts/{contact_id}/enrich")
async def enrich_v2(contact_id: str):
    """Dashboard endpoint"""
    result = enrich_contact_internal(contact_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result

# EXISTING: Keep for backwards compatibility
@router.post("/api/contacts/{contact_id}/enrich")
async def enrich_legacy(contact_id: str):
    """Legacy endpoint"""
    return await enrich_v2(contact_id)

# NEW: Dashboard status check
@router.get("/api/v2/contacts/{contact_id}/enrichment-status")
async def status_v2(contact_id: str):
    """Dashboard status endpoint"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT enrichment_status, enriched_at, enrichment_data FROM contacts WHERE id = %s",
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

        if row["enrichment_data"]:
            try:
                data = json.loads(row["enrichment_data"]) if isinstance(row["enrichment_data"], str) else row["enrichment_data"]
                if isinstance(data, dict):
                    response["sectionsCount"] = len(data.get("sections", {}))
                    response["formatDetected"] = data.get("metadata", {}).get("format_detected")
            except:
                pass

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# EXISTING: Keep for backwards compatibility
@router.get("/api/contacts/{contact_id}/enrichment-status")
async def status_legacy(contact_id: str):
    """Legacy status endpoint"""
    return await status_v2(contact_id)

# Batch enrich
@router.post("/api/batch/enrich")
async def batch_enrich(limit: int = Query(1, ge=1, le=1)):
    """Batch enrichment (limit 1 for testing)"""
    if not ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Engine unavailable")

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM contacts WHERE enrichment_status IS NULL OR enrichment_status != 'completed' ORDER BY created_at DESC LIMIT %s",
                (limit,)
            )
            targets = [row["id"] for row in cursor.fetchall()]
            cursor.close()

        if not targets:
            return {"status": "complete", "message": "No contacts to enrich", "processed": 0}

        logger.info(f"🔄 Batch enriching {len(targets)} contacts")

        results = [enrich_contact_internal(cid) for cid in targets]
        successful = sum(1 for r in results if r["success"])

        return {
            "status": "complete",
            "processed": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results
        }

    except Exception as e:
        logger.error(f"❌ Batch failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
