#!/usr/bin/env python3

"""
Adapter to use existing EnhancedEnrichment and save to new DB schema
NOW WITH STRUCTURED PARSING
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from intelligence.engines.enrichment.enhanced_enrichment import EnhancedEnrichment
from services.contact_service import get_contact, save_enrichment
from services.enrichment_parser import parse_enrichment

def enrich_and_save(contact_id: str) -> dict:
	"""
	Run existing enrichment, parse into sections, and save to database.
	Stores BOTH raw_profile AND structured sections.
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
	
	# NEW: Parse sections from raw profile
	parsed = parse_enrichment(result["profile_text"])
	
	# Save to database - now with structured sections
	enrichment_data = {
		"version": "2.0",  # Bumped version
		"raw_profile": result["profile_text"],
		"sections": parsed["sections"],  # NEW: Structured sections
		"metadata": parsed["metadata"],  # NEW: Parsing metadata
		"character_count": result["character_count"]
	}
	
	save_enrichment(contact_id, enrichment_data)
	
	return {
		"success": True,
		"contact_id": contact_id,
		"character_count": result["character_count"],
		"sections_parsed": parsed["metadata"]["total_sections"]
	}
	

if __name__ == "__main__":
	import sys
	if len(sys.argv) > 1:
		contact_id = sys.argv[1]
	else:
		# Default test contact
		contact_id = "38efdb4b-64b2-464b-a537-53f5d07d093d"
		
	print(f"Enriching contact: {contact_id}")
	result = enrich_and_save(contact_id)
	print(result)
	