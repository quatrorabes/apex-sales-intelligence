#!/usr/bin/env python3

# --- BEGIN MODULE: contact_refresh.py ---

from flask import Blueprint, jsonify, request
from datetime import datetime
import logging

contact_refresh_api = Blueprint('contact_refresh_api', __name__)

# Assume these are imported or injected elsewhere in the Apex system
# from enhancedenrichment import EnrichmentEngine
# from apexscoringengine import ApexScoringEngine
# from hubspotclient import HubSpotClient

logger = logging.getLogger("ApexContactRefresh")

@contact_refresh_api.route('/apicontacts/<int:contact_id>/refresh', methods=['POST'])
def refresh_contact(contact_id):
	"""
	Refreshes a contact's profile after enrichment, re-fetches vital info from HubSpot,
	and repopulates all dashboard-ready fields.

	Returns:
		JSON: { success: bool, contact: {...}, message: str, last_refreshed: str }
	"""
	
	try:
		# 1. Fetch contact from DB
		conn = get_db()
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
		contact = cursor.fetchone()
		if not contact:
			return jsonify(success=False, error="Contact not found.", contact_id=contact_id), 404
		contact_dict = dict(contact)
		
		# 2. Run enrichment (AI + HubSpot merge)
		enrichment_engine = EnrichmentEngine()
		enriched_data = enrichment_engine.enrich_contact(contact_dict)
		
		# 3. Pull latest from HubSpot (if enabled)
		hs_client = HubSpotClient()
		hubspot_details = hs_client.get_contact_details(contact_dict.get("email"))
		contact_dict.update(hubspot_details)
		
		# 4. Update DB
		cursor.execute("""
			UPDATE contacts 
			SET 
				profilecontent = ?, 
				enrichmentstatus = 'completed', 
				enrichmentdata = ?,
				mdcpscore = ?, 
				rssscore = ?, 
				priorityscore = ?, 
				updatedat = ?
			WHERE id = ?
		""", (
			enriched_data.get("profilecontent"),
			enriched_data.get("enrichmentdata_json"),
			enriched_data.get("mdcp_score"),
			enriched_data.get("rss_score"),
			enriched_data.get("priority_score"),
			datetime.now().isoformat(),
			contact_id
		))
		conn.commit()
		
		# 5. Return refreshed contact block for Dashboard_v1
		cursor.execute("""
			SELECT id, name, firstname, lastname, email, phone, company, title, hubspotid, linkedinurl, 
					enrichmentstatus, profilecontent, mdcpscore, rssscore, priorityscore, lifecyclestage,
					leadstatus, lastcontactdate, updatedat
			FROM contacts WHERE id = ?
		""", (contact_id,))
		refreshed_contact = dict(cursor.fetchone())
		
		# 6. Close DB connection
		conn.close()
		
		return jsonify(
			success=True,
			contact=refreshed_contact,
			message="Contact refreshed and vital fields repopulated.",
			last_refreshed=refreshed_contact['updatedat']
		), 200
	
	except Exception as e:
		logger.error(f"[Apex] Refresh error: {str(e)}")
		return jsonify(success=False, error=str(e)), 500
	
# --- END MODULE: contact_refresh.py ---
	