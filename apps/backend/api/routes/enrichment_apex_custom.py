"""
APEX Enrichment API - ApexCustomEnrichment Integration
Replaces current enrichment endpoint with three-stage apex_custom engine
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import sys
import os
from pathlib import Path
import traceback

# Add backend to path
BACKEND_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from intelligence.engines.enrichment.apex_custom_enrichment import ApexCustomEnrichment
from services.enrichment_parser_v2 import EnrichmentParser
from services import contact_service

router = APIRouter()


class Config:
    """Config for ApexCustomEnrichment"""
    def __init__(self):
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')


@router.post("/api/contacts/{contact_id}/enrich")
async def enrich_contact(contact_id: str):
    """
    Three-stage enrichment with ApexCustomEnrichment
    Stage 1: Raw data gathering (Perplexity)
    Stage 2: Intelligence synthesis (GPT-4)
    Stage 3: Field extraction & parsing
    """
    # Get contact
    contact = contact_service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    # Mark as enriching
    contact_service.update_contact(contact_id, enrichment_status="enriching")
    
    try:
        # Initialize enricher
        enricher = ApexCustomEnrichment(Config())
        
        print(f"🚀 Starting ApexCustomEnrichment for {contact['first_name']} {contact.get('last_name', '')}")
        
        # Run three-stage enrichment
        result = enricher.enrich_contact_full(contact)
        
        if not result.get('status') == 'success':
            raise Exception(result.get('error', 'Unknown enrichment error'))
        
        # Parse with new parser
        parser = EnrichmentParser()
        parsed = parser.parse(result['profile_data']['synthesized_intelligence'])
        
        # Build enrichment data structure
        enrichment_data = {
            "version": "2.1",
            "engine": "apex_custom",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "sections": parsed['sections'],
            "metadata": {
                **parsed['metadata'],
                "raw_data_sections": len(result['profile_data']['raw_data']),
                "parsed_fields": result['profile_data'].get('parsed_fields', {}),
                "enrichment_notes": result.get('enrichment_notes', '')
            }
        }
        
        # Save to database
        updated_contact = contact_service.save_enrichment(contact_id, enrichment_data)
        
        print(f"✅ Enrichment complete: {len(parsed['sections'])} sections, {parsed['metadata']['character_count']} chars")
        
        return {
            "success": True,
            "contact_id": contact_id,
            "status": "completed",
            "message": "Enrichment completed successfully",
            "sections_count": len(parsed['sections']),
            "character_count": parsed['metadata']['character_count'],
            "format_detected": parsed['metadata']['format_detected']
        }
    
    except Exception as e:
        print(f"❌ Enrichment failed: {e}")
        traceback.print_exc()
        
        # Mark as failed
        contact_service.update_contact(contact_id, enrichment_status="failed")
        
        raise HTTPException(
            status_code=500,
            detail=f"Enrichment failed: {str(e)}"
        )


@router.get("/api/contacts/{contact_id}/enrichment-status")
async def get_enrichment_status(contact_id: str):
    """
    Check enrichment status for a contact
    Returns current status and section count if enriched
    """
    contact = contact_service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    response = {
        "contact_id": contact_id,
        "enrichment_status": contact.get('enrichment_status', 'pending'),
        "enriched_at": contact.get('enriched_at'),
    }
    
    # If enriched, include metadata
    if contact.get('enrichment'):
        enrichment = contact['enrichment']
        if isinstance(enrichment, dict):
            response["sections_count"] = len(enrichment.get('sections', {}))
            response["version"] = enrichment.get('version')
            response["engine"] = enrichment.get('engine', 'unknown')
            response["character_count"] = enrichment.get('metadata', {}).get('character_count', 0)
    
    return response


@router.post("/api/contacts/bulk-enrich")
async def bulk_enrich_contacts(limit: int = 10):
    """
    Enrich multiple pending contacts
    Useful for batch processing
    """
    pending = contact_service.bulk_enrich(limit)
    
    if pending['count'] == 0:
        return {
            "success": True,
            "message": "No contacts pending enrichment",
            "enriched": 0
        }
    
    enricher = ApexCustomEnrichment(Config())
    parser = EnrichmentParser()
    
    enriched_count = 0
    failed_count = 0
    
    for contact in pending['contacts']:
        try:
            print(f"🔄 Enriching {contact['first_name']} {contact.get('last_name', '')}...")
            
            result = enricher.enrich_contact_full(contact)
            
            if result.get('status') == 'success':
                parsed = parser.parse(result['profile_data']['synthesized_intelligence'])
                
                enrichment_data = {
                    "version": "2.1",
                    "engine": "apex_custom",
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "sections": parsed['sections'],
                    "metadata": parsed['metadata']
                }
                
                contact_service.save_enrichment(contact['id'], enrichment_data)
                enriched_count += 1
                print(f"   ✅ Success")
            else:
                contact_service.update_contact(contact['id'], enrichment_status="failed")
                failed_count += 1
                print(f"   ❌ Failed")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            contact_service.update_contact(contact['id'], enrichment_status="failed")
            failed_count += 1
    
    return {
        "success": True,
        "message": f"Bulk enrichment completed",
        "enriched": enriched_count,
        "failed": failed_count,
        "total_processed": enriched_count + failed_count
    }
