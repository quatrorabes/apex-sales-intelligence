# apps/backend/api/routes/enrichment.py
"""
APEX v3.0 Enrichment Routes
Handles contact enrichment with 10-stage pipeline
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(tags=["enrichment"])

# Import v3.0 engine
try:
    from engines.intelligence.enrichment import ApexEnrichmentEngineV3, EnrichmentRequest
    enrichment_engine = ApexEnrichmentEngineV3()
except ImportError as e:
    logger.warning(f"⚠️ v3.0 engine not available: {e}")
    enrichment_engine = None

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class EnrichmentResponse(BaseModel):
    success: bool
    contact_id: str
    message: str
    status: str

class EnrichmentStatusResponse(BaseModel):
    contact_id: str
    enrichment_status: Optional[str]
    enriched_at: Optional[datetime]
    enrichment_version: Optional[str]

# ============================================================================
# ENDPOINT 1: Single Contact Enrich (v2 compatible)
# ============================================================================

@router.post("/api/v2/contacts/{contact_id}/enrich")
async def enrich_contact_v2(contact_id: str, background_tasks: BackgroundTasks):
    """
    Enrich a specific contact using v3.0 engine
    UUID: contact_id is string, NEVER integer
    """
    if not enrichment_engine:
        raise HTTPException(status_code=503, detail="Enrichment engine not available")
    
    try:
        # Import database function
        from services.database import get_db
        
        # Fetch contact from DB (UUID as string)
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            row = cursor.fetchone()
            cursor.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        contact = dict(row)
        
        # Enrich in background (takes 60-90 seconds)
        background_tasks.add_task(enrich_contact_internal, contact_id, contact)
        
        return EnrichmentResponse(
            success=True,
            contact_id=contact_id,
            message=f"Enrichment started for {contact['name']}",
            status="pending"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Enrich v2 failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT 2: Batch Enrich
# ============================================================================

@router.post("/api/batch/enrich")
async def batch_enrich(
    background_tasks: BackgroundTasks,
    request: Optional[EnrichmentRequest] = None
):
    """
    Batch enrichment - accepts contact_ids
    """
    if not enrichment_engine:
        raise HTTPException(status_code=503, detail="Enrichment engine not available")
    
    try:
        from services.database import get_db
        
        contact_ids = []
        
        # If specific IDs provided, use those
        if request and request.contact_ids:
            contact_ids = request.contact_ids[:5]  # Limit to 5 at a time
            logger.info(f"🔄 Batch enriching {len(contact_ids)} specific contacts")
        else:
            # Auto-select next unenriched contacts
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM contacts WHERE enrichment_status IS NULL "
                    "OR enrichment_status = 'failed' LIMIT 5"
                )
                contact_ids = [row["id"] for row in cursor.fetchall()]
                cursor.close()
        
        # Queue each contact for enrichment
        for cid in contact_ids:
            background_tasks.add_task(enrich_contact_internal, cid, None)
        
        return {
            "status": "complete",
            "message": f"Queued {len(contact_ids)} contacts for enrichment",
            "contact_ids": contact_ids
        }
    
    except Exception as e:
        logger.error(f"❌ Batch enrich failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CORE FUNCTION: enrich_contact_internal (Business Logic)
# ============================================================================

def enrich_contact_internal(contact_id: str, contact_data: Optional[dict] = None) -> Dict[str, Any]:
    """
    Internal enrichment function (runs in background)
    - Fetches contact if not provided
    - Calls v3.0 engine
    - Parses sections
    - Saves to DB
    - Preserves all fields
    """
    try:
        from services.database import get_db
        
        logger.info(f"⏳ Starting enrichment: {contact_id}")
        
        # 1. Fetch contact (UUID preserved as string)
        if not contact_data:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
                row = cursor.fetchone()
                cursor.close()
            
            if not row:
                logger.error(f"❌ Contact not found: {contact_id}")
                return {"success": False, "error": "Contact not found"}
            
            contact_data = dict(row)
        
        # 2. Call enrichment engine v3.0
        logger.info(f"🚀 Calling APEX v3.0 engine for {contact_data.get('name')}")
        enrichment_result = enrichment_engine.enrich_contact(contact_data)
        
        if not enrichment_result.success:
            logger.error(f"❌ Enrichment failed: {enrichment_result.error}")
            
            # Save error to DB
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE contacts SET enrichment_status = %s, 
                       enrichment_error = %s, updated_at = NOW() 
                       WHERE id = %s""",
                    ('failed', enrichment_result.error, contact_id)
                )
                conn.commit()
                cursor.close()
            
            return {"success": False, "error": enrichment_result.error}
        
        # 3. Build complete enrichment_data object
        enrichment_data = {
            "version": "3.0",
            "contact_id": contact_id,
            "contact_info": enrichment_result.contact_info.dict() if enrichment_result.contact_info else {},
            "sections": enrichment_result.sections,
            "raw_profile": enrichment_result.raw_profile,
            "metadata": enrichment_result.metadata.dict() if enrichment_result.metadata else {},
            "preserved_fields": enrichment_result.preserved_fields
        }
        
        # 4. Save to database
        enrichment_json = json.dumps(enrichment_data)
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE contacts SET 
                   enrichment_data = %s,
                   enrichment_status = %s,
                   enrichment_version = %s,
                   enriched_at = NOW(),
                   enrichment_error = NULL,
                   updated_at = NOW()
                   WHERE id = %s""",
                (enrichment_json, 'completed', 'v3.0', contact_id)
            )
            conn.commit()
            cursor.close()
        
        logger.info(f"✅ Enrichment complete: {contact_id} ({enrichment_result.metadata.character_count} chars)")
        
        return {
            "success": True,
            "contact_id": contact_id,
            "character_count": enrichment_result.metadata.character_count,
            "word_count": enrichment_result.metadata.word_count,
            "sections_count": enrichment_result.metadata.total_sections
        }
    
    except Exception as e:
        logger.error(f"❌ enrichment_contact_internal failed: {str(e)}", exc_info=True)
        
        # Save error
        try:
            from services.database import get_db
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contacts SET enrichment_status = %s, enrichment_error = %s WHERE id = %s",
                    ('failed', str(e), contact_id)
                )
                conn.commit()
                cursor.close()
        except:
            pass
        
        return {"success": False, "error": str(e)}

# ============================================================================
# ENDPOINT 3: Check Enrichment Status
# ============================================================================

@router.get("/api/v2/contacts/{contact_id}/enrichment-status")
async def get_enrichment_status(contact_id: str):
    """Get enrichment status for a contact"""
    try:
        from services.database import get_db
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT enrichment_status, enriched_at, enrichment_version FROM contacts WHERE id = %s",
                (contact_id,)
            )
            row = cursor.fetchone()
            cursor.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return EnrichmentStatusResponse(
            contact_id=contact_id,
            enrichment_status=row["enrichment_status"],
            enriched_at=row["enriched_at"],
            enrichment_version=row["enrichment_version"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT 4: Get Enrichment Data Only
# ============================================================================

@router.get("/api/contacts/{contact_id}/enrichment")
async def get_enrichment_data(contact_id: str):
    """Get enrichment_data for a contact"""
    try:
        from services.database import get_db
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT enrichment_data FROM contacts WHERE id = %s",
                (contact_id,)
            )
            row = cursor.fetchone()
            cursor.close()
        
        if not row or not row["enrichment_data"]:
            return {"enrichment_data": None, "message": "No enrichment data available"}
        
        return {"enrichment_data": row["enrichment_data"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENDPOINT 5: Health Check
# ============================================================================

@router.get("/health/enrichment", tags=["Health"])
async def enrichment_health():
    """Check enrichment engine health"""
    return {
        "status": "ok",
        "enrichment_engine_v3": enrichment_engine is not None,
        "timestamp": datetime.now().isoformat()
    }
