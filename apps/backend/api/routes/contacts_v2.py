"""
APEX Contacts API v2 - Clean schema-based endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import csv
import io

# Services
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from services.contact_service import (
    create_contact, get_contact, get_all_contacts, 
    update_contact, delete_contact, save_enrichment, 
    get_stats, import_from_csv, get_contact_by_hubspot_id
)

from services.enrichment_adapter import enrich_and_save
router = APIRouter(prefix="/api/v2/contacts", tags=["contacts"])

# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================
class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    hubspot_id: Optional[str] = None

class ContactUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None

# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/")
async def list_contacts(limit: int = 100, offset: int = 0):
    """List all contacts with pagination"""
    try:
        contacts = get_all_contacts(limit=limit, offset=offset)
        stats = get_stats()
        return {
            "contacts": contacts,
            "total": stats.get("total_contacts", len(contacts)),
            "enriched": stats.get("enriched_contacts", 0)
        }
    except Exception as e:
        print(f"Error in list_contacts: {e}")
        # Return contacts anyway, even if stats fails
        contacts = get_all_contacts(limit=limit, offset=offset)
        return {
            "contacts": contacts,
            "total": len(contacts),
            "enriched": 0
        }

@router.get("/stats")
async def contact_stats():
    """Get contact statistics"""
    return get_stats()

@router.post("/")
async def create_new_contact(contact: ContactCreate):
    """Create a new contact"""
    return create_contact(
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        title=contact.title,
        company=contact.company,
        hubspot_id=contact.hubspot_id
    )

@router.get("/{contact_id}")
async def get_single_contact(contact_id: str):
    """Get a contact by ID"""
    contact = get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}")
async def update_single_contact(contact_id: str, data: ContactUpdate):
    """Update a contact"""
    updates = {k: v for k, v in data.dict().items() if v is not None}
    contact = update_contact(contact_id, **updates)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.delete("/{contact_id}")
async def delete_single_contact(contact_id: str):
    """Delete a contact"""
    if not delete_contact(contact_id):
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"deleted": True}

@router.post("/{contact_id}/enrich")
async def enrich_single_contact(contact_id: str):
    """Enrich a contact with AI-generated intelligence"""
    result = enrich_and_save(contact_id)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Enrichment failed"))
    return get_contact(contact_id)

@router.post("/import/csv")
async def import_csv(file: UploadFile = File(...)):
    """Import contacts from CSV file"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    contacts = import_from_csv(list(reader))
    return {
        "imported": len(contacts),
        "contacts": contacts
    }

@router.post("/bulk-enrich")
async def bulk_enrich(limit: int = 10):
    """Enrich multiple contacts that haven't been enriched yet"""
    contacts = get_all_contacts(limit=limit)
    unenriched = [c for c in contacts if not c.get("enrichment")]
    
    results = []
    for contact in unenriched[:limit]:
        try:
            enrichment = await enrich_contact(
                first_name=contact["first_name"],
                last_name=contact["last_name"],
                title=contact.get("title", ""),
                company=contact.get("company", ""),
                email=contact.get("email", "")
            )
            if enrichment:
                save_enrichment(contact["id"], enrichment.model_dump())
                results.append({"id": contact["id"], "status": "success"})
            else:
                results.append({"id": contact["id"], "status": "failed"})
        except Exception as e:
            results.append({"id": contact["id"], "status": "error", "error": str(e)})
    
    return {"processed": len(results), "results": results}

@router.post("/sync/hubspot")
async def sync_from_hubspot(limit: int = 100):
    """Sync contacts from HubSpot"""
    from services.hubspot_sync_v2 import sync_hubspot_contacts
    
    try:
        stats = sync_hubspot_contacts(limit)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/hubspot")
async def sync_from_hubspot(limit: int = 100):
    """Sync contacts from HubSpot"""
    from services.hubspot_sync_v2 import sync_hubspot_contacts
    
    try:
        stats = sync_hubspot_contacts(limit)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/hubspot/filtered")
async def sync_from_hubspot_filtered():
        """Sync qualified contacts from HubSpot with filters (max 200)"""
        from intelligence.hubspot_sync_filtered import sync_contacts

    try:
                count = sync_contacts()
                return {"status": "success", "imported": count}
            except Exception as e:
                        raise HTTPException(status_code=500, detail=str(e))
