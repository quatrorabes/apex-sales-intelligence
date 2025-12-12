"""
Adapter to use existing EnhancedEnrichment and save to new DB schema
NO CHANGES to the enrichment engine - just wires it to new database
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from intelligence.engines.enrichment.enhanced_enrichment import EnhancedEnrichment
from services.contact_service import get_contact, save_enrichment

def enrich_and_save(contact_id: str) -> dict:
    """
    Run existing enrichment and save to database.
    Stores raw profile_text - parsing happens on frontend.
    """
    contact = get_contact(contact_id)
    if not contact:
        return {"success": False, "error": "Contact not found"}
    
    # Build contact dict for existing enrichment
    enrichment_input = {
        "name": f"{contact['first_name']} {contact['last_name']}",
        "firstname": contact["first_name"],
        "lastname": contact["last_name"],
        "company": contact.get("company", ""),
        "title": contact.get("title", ""),
        "email": contact.get("email", ""),
        "phone": contact.get("phone", "")
    }
    
    # Run existing enrichment (unchanged)
    engine = EnhancedEnrichment()
    result = engine.enrich_contact(enrichment_input)
    
    if not result.get("success"):
        return {"success": False, "error": "Enrichment failed"}
    
    # Save to database - store raw text for now
    enrichment_data = {
        "version": "1.0",
        "raw_profile": result["profile_text"],
        "character_count": result["character_count"]
    }
    
    save_enrichment(contact_id, enrichment_data)
    
    return {
        "success": True,
        "contact_id": contact_id,
        "character_count": result["character_count"]
    }


if __name__ == "__main__":
    # Test with Ed Colunga
    result = enrich_and_save("38efdb4b-64b2-464b-a537-53f5d07d093d")
    print(result)
