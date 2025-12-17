#!/bin/bash
# Surgical fix: Route wiring only, preserve core enrichment engine

set -e

echo "========================================================================"
echo "SURGICAL ROUTING FIX — PRESERVE ENRICHMENT CORE"
echo "========================================================================"

# Step 1: Create minimal routing wrapper (NO engine changes)
cat > apps/backend/api/routes/enrichment.py << 'ROUTE_EOF'
"""
Apex Enrichment Routes - Minimal Routing Layer
PRESERVES EXISTING ENGINE LOGIC — Only fixes route paths
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import logging
import json
import os
import sys

logger = logging.getLogger(__name__)

# NO PREFIX - explicit paths to match Dashboard_v1
router = APIRouter(tags=["enrichment"])

# Add path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import EXISTING proven engine (DO NOT MODIFY ENGINE CODE)
try:
    from enrichment_engine import EnhancedEnrichment
    enrichment_engine = EnhancedEnrichment()
    ENGINE_AVAILABLE = True
    logger.info("✅ EnhancedEnrichment loaded (using proven engine)")
except ImportError as e:
    logger.error(f"❌ Engine import failed: {e}")
    enrichment_engine = None
    ENGINE_AVAILABLE = False

# Import parser (for post-processing only)
try:
    from services.enrichment_integration import integrate_enrichment_result
    PARSER_AVAILABLE = True
    logger.info("✅ Parser loaded")
except ImportError as e:
    logger.warning(f"⚠️ Parser not available: {e}")
    PARSER_AVAILABLE = False

# Database
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
    Minimal wrapper around proven enrichment engine.
    
    Flow (PRESERVE EXISTING LOGIC):
    1. Fetch contact
    2. Call enrichment_engine.enrich_contact() [UNCHANGED]
    3. Parse output (new step)
    4. Save to DB
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
        # 1. Fetch contact
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
        
        # 2. Call PROVEN ENGINE (DO NOT MODIFY THIS CALL)
        logger.info(f"🚀 Enriching contact {contact_id}: {contact_dict.get('name')}")
        
        # THIS IS THE SACRED CALL — PRESERVE EXACTLY
        enrichment_result = enrichment_engine.enrich_contact(contact_dict)
        
        # Check if enrichment succeeded
        if not enrichment_result.get("success"):
            error_msg = enrichment_result.get("error", "Enrichment failed")
            logger.error(f"❌ Engine returned failure: {error_msg}")
            
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
        
        # 3. Extract profile text from engine result
        raw_profile = enrichment_result.get("profile_text", "")
        
        if not raw_profile:
            logger.warning(f"Empty profile_text for contact {contact_id}")
        
        logger.info(f"📝 Got {len(raw_profile)} chars from engine")
        
        # 4. Parse output (NEW STEP — does not affect engine)
        if PARSER_AVAILABLE and raw_profile:
            try:
                enrichment_object = integrate_enrichment_result(raw_profile)
                logger.info(f"✅ Parsed into {len(enrichment_object.get('sections', {}))} sections")
            except Exception as parse_error:
                logger.warning(f"Parser failed, saving raw: {parse_error}")
                enrichment_object = {
                    "sections": {"raw_text": raw_profile},
                    "metadata": {
                        "format_detected": "raw",
                        "total_sections": 1,
                        "character_count": len(raw_profile)
                    }
                }
        else:
            # No parser or empty profile, save raw
            enrichment_object = {
                "sections": {"raw_text": raw_profile},
                "metadata": {
                    "format_detected": "raw",
                    "total_sections": 1,
                    "character_count": len(raw_profile)
                }
            }
        
        # 5. Save to DB
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


# ============================================================================
# ROUTES — EXPLICIT PATHS (Match Dashboard_v1 Expectations)
# ============================================================================

@router.post("/api/batch/enrich")
async def batch_enrich(limit: int = Query(10, ge=1, le=100)):
    """
    Batch enrichment endpoint for Dashboard_v1
    
    Path: POST /api/batch/enrich (NO prefix)
    Query: ?limit=10 (default)
    
    Returns: {status, processed, successful, failed, results}
    """
    
    if not ENGINE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Enrichment engine not available"
        )
    
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
            logger.info("No contacts to enrich")
            return {
                "status": "complete",
                "message": "No contacts to enrich",
                "processed": 0,
                "successful": 0,
                "failed": 0
            }
        
        logger.info(f"🔄 Batch enriching {len(targets)} contacts...")
        
        # Enrich each contact using proven engine
        results = []
        for contact_id in targets:
            result = enrich_contact_internal(contact_id)
            results.append(result)
        
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
    """
    Single contact enrichment
    
    Path: POST /api/contacts/{contact_id}/enrich
    
    Returns: {success, contactId, status, sections, format}
    """
    
    result = enrich_contact_internal(contact_id)
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Enrichment failed")
        )
    
    return result


@router.get("/api/contacts/{contact_id}/enrichment-status")
async def get_enrichment_status(contact_id: int):
    """
    Check enrichment status for a contact
    
    Path: GET /api/contacts/{contact_id}/enrichment-status
    
    Returns: {contactId, enrichmentStatus, enrichedAt, sectionsCount, formatDetected}
    """
    
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
        
        # Include enrichment metadata if available
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
ROUTE_EOF

echo "✅ Created: apps/backend/api/routes/enrichment.py (routing layer only)"

# Step 2: Update main.py router registration (minimal change)
echo ""
echo "Updating main.py router registration..."

# Check if enrichment router is already registered
if grep -q "from api.routes.enrichment import router as enrichment_router" apps/backend/main.py; then
    echo "✅ Enrichment router already registered in main.py"
else
    # Add import and registration (after existing routers)
    
    # Find line with contacts_v2_enrichment import
    if grep -q "from api.routes.contacts_v2_enrichment" apps/backend/main.py; then
        # Replace old import with new one
        sed -i.bak 's/from api.routes.contacts_v2_enrichment import router as contacts_v2_enrichment_router/from api.routes.enrichment import router as enrichment_router/' apps/backend/main.py
        sed -i.bak 's/app.include_router(contacts_v2_enrichment_router)/app.include_router(enrichment_router)/' apps/backend/main.py
        echo "✅ Updated main.py: replaced contacts_v2_enrichment with enrichment router"
    else
        # Add new import after existing route imports
        sed -i.bak '/from api.routes.contacts_v2 import router as contacts_v2_router/a\
from api.routes.enrichment import router as enrichment_router' apps/backend/main.py
        
        # Add router registration after contacts_v2
        sed -i.bak '/app.include_router(contacts_v2_router)/a\
app.include_router(enrichment_router)' apps/backend/main.py
        
        echo "✅ Added enrichment router to main.py"
    fi
fi

# Step 3: Backup old route file (if exists)
if [ -f apps/backend/api/routes/contacts_v2_enrichment.py ]; then
    mv apps/backend/api/routes/contacts_v2_enrichment.py apps/backend/api/routes/contacts_v2_enrichment.py.backup-$(date +%s)
    echo "✅ Backed up old contacts_v2_enrichment.py"
fi

# Step 4: Commit changes
git add apps/backend/api/routes/enrichment.py
git add apps/backend/main.py

git commit -m "fix(routing): create minimal enrichment route wrapper

PRESERVES EXISTING ENGINE LOGIC:
- EnhancedEnrichment.enrich_contact() unchanged
- All Perplexity 3-stage logic unchanged  
- GPT-4 synthesis prompts unchanged
- Rate limits and delays preserved

ROUTING FIXES:
- Create apps/backend/api/routes/enrichment.py (thin wrapper)
- POST /api/batch/enrich (no prefix, matches Dashboard_v1)
- POST /api/contacts/{id}/enrich
- GET /api/contacts/{id}/enrichment-status
- Integrate parser AFTER engine returns
- Update main.py router registration

Result: Dashboard batch enrich now calls correct endpoint"

git push origin main

echo ""
echo "========================================================================"
echo "✅ SURGICAL ROUTING FIX COMPLETE"
echo "========================================================================"
echo ""
echo "PRESERVED (Unchanged):"
echo "  ✅ enrichment_engine.py (EnhancedEnrichment class)"
echo "  ✅ All Perplexity search logic"
echo "  ✅ GPT-4 synthesis and prompts"
echo "  ✅ Rate limiting and delays"
echo ""
echo "FIXED (Routing only):"
echo "  🔧 POST /api/batch/enrich (no prefix collision)"
echo "  🔧 POST /api/contacts/{id}/enrich"
echo "  🔧 GET /api/contacts/{id}/enrichment-status"
echo "  🔧 Parser integration (post-processing)"
echo ""
echo "Next Steps:"
echo "  1. Wait ~2min for Render to restart"
echo "  2. Check logs for: ✅ EnhancedEnrichment loaded"
echo "  3. Click 'Enrich All' in Dashboard_v1"
echo "  4. Verify enrichments complete successfully"
echo ""
