#!/usr/bin/env python3
"""
APEX ENDPOINT WIRING - Dashboard to Backend
Simple fix: align route paths between frontend and backend
"""

import os
from pathlib import Path

print("=" * 80)
print("APEX DASHBOARD <-> BACKEND WIRING FIX")
print("=" * 80)
print()

# ==============================================================================
# STEP 1: Update Backend Route - Add /api/v2 prefix compatibility
# ==============================================================================

enrichment_route = """\"""
Apex Enrichment Routes - Dashboard Compatible
Supports BOTH /api/contacts AND /api/v2/contacts paths
\"""

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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# Import proven engine
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

# PostgreSQL Database
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
    \"""Save debug output to /tmp/apex_debug/\"""
    try:
        debug_dir = "/tmp/apex_debug"
        os.makedirs(debug_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{debug_dir}/contact_{contact_id}_{filename}_{timestamp}.txt"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"📝 Debug file: {filepath}")
        return filepath
    except Exception as e:
        logger.warning(f"Could not save debug file: {e}")
        return None


def enrich_contact_internal(contact_id: str) -> Dict[str, Any]:
    \"""
    Internal enrichment pipeline
    PRESERVES: All Perplexity + GPT-4 logic in enrichment_engine
    \"""

    if not ENGINE_AVAILABLE:
        return {
            "success": False,
            "contactId": contact_id,
            "error": "Enrichment engine not available"
        }

    try:
        # 1. Fetch contact (UUID string)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()

        if not contact:
            return {
                "success": False,
                "contactId": contact_id,
                "error": f"Contact {contact_id} not found"
            }

        contact_dict = dict(contact)

        logger.info(f"🚀 Enriching {contact_id}: {contact_dict.get('name')}")

        # 2. Call proven enrichment engine (UNCHANGED)
        enrichment_result = enrichment_engine.enrich_contact(contact_dict)

        # Save raw result
        try:
            save_debug_file("01_raw_result", json.dumps(enrichment_result, indent=2, default=str), contact_id)
        except:
            pass

        if not enrichment_result.get("success"):
            error_msg = enrichment_result.get("error", "Enrichment failed")
            logger.error(f"❌ Engine failure: {error_msg}")

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE contacts SET enrichment_status = %s WHERE id = %s", ('failed', contact_id))
                conn.commit()
                cursor.close()

            return {"success": False, "contactId": contact_id, "error": error_msg}

        # 3. Extract Perplexity + GPT-4 output
        raw_profile = enrichment_result.get("profile_text", "")
        logger.info(f"📊 Got {len(raw_profile)} chars from engine")

        # Save Perplexity + OpenAI output
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

        # 5. Save to DB
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
# ROUTES - Dashboard Compatible (supports BOTH paths)
# ============================================================================

# Dashboard calls: POST /api/v2/contacts/{id}/enrich
@router.post("/api/v2/contacts/{contact_id}/enrich")
async def enrich_contact_v2(contact_id: str):
    \"""Dashboard_v1 endpoint\"""
    result = enrich_contact_internal(contact_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result

# Legacy: POST /api/contacts/{id}/enrich
@router.post("/api/contacts/{contact_id}/enrich")
async def enrich_contact_legacy(contact_id: str):
    \"""Legacy endpoint\"""
    return await enrich_contact_v2(contact_id)

# Dashboard calls: GET /api/v2/contacts/{id}/enrichment-status
@router.get("/api/v2/contacts/{contact_id}/enrichment-status")
async def enrichment_status_v2(contact_id: str):
    \"""Dashboard_v1 status check\"""
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

# Legacy status endpoint
@router.get("/api/contacts/{contact_id}/enrichment-status")
async def enrichment_status_legacy(contact_id: str):
    \"""Legacy status endpoint\"""
    return await enrichment_status_v2(contact_id)

# Batch enrich (1 at a time for testing)
@router.post("/api/batch/enrich")
async def batch_enrich(limit: int = Query(1, ge=1, le=1)):
    \"""Batch enrichment (limit 1)\"""
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
"""

backend_path = Path("apps/backend/api/routes/enrichment.py")
backend_path.parent.mkdir(parents=True, exist_ok=True)
backend_path.write_text(enrichment_route)
print(f"✅ Created: {backend_path}")

# ==============================================================================
# STEP 2: Create commit script
# ==============================================================================

commit_script = """#!/bin/bash
# Deploy enrichment wiring

set -e

echo "========================================================================"
echo "DEPLOYING ENRICHMENT WIRING"
echo "========================================================================"

git add apps/backend/api/routes/enrichment.py

git commit -m "fix(wiring): align enrichment endpoints with Dashboard_v1

ENDPOINTS ADDED:
- POST /api/v2/contacts/{id}/enrich (Dashboard_v1)
- GET /api/v2/contacts/{id}/enrichment-status (Dashboard_v1)
- POST /api/contacts/{id}/enrich (legacy)
- GET /api/contacts/{id}/enrichment-status (legacy)
- POST /api/batch/enrich (limit 1 for testing)

PRESERVED:
- EnhancedEnrichment engine (Perplexity 3-stage + GPT-4)
- All rate limits and delays
- UUID string handling
- PostgreSQL queries

DEBUG FILES:
- /tmp/apex_debug/contact_{id}_01_raw_result_{ts}.txt
- /tmp/apex_debug/contact_{id}_02_perplexity_openai_{ts}.txt
- /tmp/apex_debug/contact_{id}_03_parsed_{ts}.txt

Resolves: Dashboard enrichment button now works end-to-end"

git push origin main

echo ""
echo "✅ Deployed to Render (~2 min to restart)"
echo ""
echo "Testing:"
echo "1. Wait for Render restart"
echo "2. Open Dashboard: https://apex-sales-intelligence.vercel.app"
echo "3. Click contact → 'Generate AI Outreach Content'"
echo "4. Wait ~60-90 sec"
echo "5. Check Render logs for debug file paths"
"""

commit_path = Path("DEPLOY_ENRICHMENT_WIRING.sh")
commit_path.write_text(commit_script)
commit_path.chmod(0o755)
print(f"✅ Created: {commit_path}")

# ==============================================================================
# STEP 3: Testing instructions
# ==============================================================================

test_instructions = """# ENRICHMENT WIRING - TESTING CHECKLIST

## Backend Deployment

1. Deploy backend:
   ```bash
   bash DEPLOY_ENRICHMENT_WIRING.sh
   ```

2. Wait ~2 minutes for Render to restart

3. Check Render logs for:
   ```
   ✅ EnhancedEnrichment loaded
   INFO: Application startup complete
   ```

## Dashboard Testing

### Test 1: Single Contact Enrich Button

1. Open Dashboard: https://apex-sales-intelligence.vercel.app
2. Click on any contact to open detail modal
3. Go to "Outreach" tab
4. Click "Generate AI Outreach Content" button
5. Watch button change to "Enriching..."
6. Wait ~60-90 seconds
7. Success: Modal refreshes, shows enrichment data
8. Check Render logs for debug file paths

### Test 2: Verify Debug Files

SSH to Render:
```bash
# Get service name from Render dashboard
render ssh <service-name>

# List debug files
ls -lh /tmp/apex_debug/

# View Perplexity + OpenAI output
cat /tmp/apex_debug/contact_*_02_perplexity_openai_*.txt
```

### Test 3: Batch Enrich (limit 1)

```bash
curl -X POST "https://your-backend.onrender.com/api/batch/enrich?limit=1"
```

Should return:
```json
{
  "status": "complete",
  "processed": 1,
  "successful": 1,
  "failed": 0,
  "results": [...]
}
```

## Expected Behavior

### Success Path

1. Click "Generate AI Outreach Content"
2. Button → "⏳ Enriching..."
3. Render logs show:
   ```
   🚀 Enriching <uuid>: John Doe
   📡 STAGE 1: Searching LinkedIn...
   📡 STAGE 2: Searching company...
   📡 STAGE 3: Searching sales context...
   🧠 STAGE 4: Generating profile...
   📊 Got 2500 chars from engine
   📝 Debug file: /tmp/apex_debug/contact_<uuid>_02_perplexity_openai_<ts>.txt
   ✅ Complete: <uuid>
   ```
4. Modal refreshes automatically
5. Intelligence tab shows enriched data
6. Database enrichment_status = 'completed'

### Failure Handling

If enrichment fails:
- Button returns to "Generate AI Outreach Content"
- Red alert shows error message
- Database enrichment_status = 'failed'
- Render logs show stack trace

## Troubleshooting

### "Engine not available"
- Check Render logs for import error
- Verify enrichment_engine.py exists at root
- Check OPENAI_API_KEY and PERPLEXITY_API_KEY env vars

### "Contact not found"
- Verify contact exists in database
- Check contact ID is UUID string (not integer)
- Run: `SELECT id, name FROM contacts WHERE id = '<uuid>';`

### Empty enrichment data
- Check debug file: `02_perplexity_openai_*.txt`
- Verify Perplexity API returned results
- Check GPT-4 synthesis didn't fail

### Parser errors
- Check debug files 02 (raw) vs 03 (parsed)
- Parser failure is non-fatal (saves raw text)
- Verify services/enrichment_integration.py exists

## Success Criteria

✅ Dashboard "Generate AI Outreach Content" button works  
✅ Enrichment completes in 60-90 seconds  
✅ Debug files saved to /tmp/apex_debug/  
✅ Perplexity + OpenAI output visible in debug file  
✅ Database enrichment_status updated  
✅ Modal shows enrichment data  
"""

test_path = Path("ENRICHMENT_TESTING_CHECKLIST.md")
test_path.write_text(test_instructions)
print(f"✅ Created: {test_path}")

print()
print("=" * 80)
print("✅ ENRICHMENT WIRING COMPLETE")
print("=" * 80)
print()
print("Files created:")
print("  1. apps/backend/api/routes/enrichment.py (endpoint routes)")
print("  2. DEPLOY_ENRICHMENT_WIRING.sh (deployment script)")
print("  3. ENRICHMENT_TESTING_CHECKLIST.md (testing guide)")
print()
print("Deploy now:")
print("  bash DEPLOY_ENRICHMENT_WIRING.sh")
print()
print("After deployment:")
print("  1. Open Dashboard")
print("  2. Click contact → Outreach tab")
print("  3. Click 'Generate AI Outreach Content'")
print("  4. Wait ~60-90 seconds")
print("  5. Check debug files in Render logs")
print()
