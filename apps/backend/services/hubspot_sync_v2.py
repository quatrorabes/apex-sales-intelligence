"""
HubSpot Sync Adapter v2
Syncs HubSpot contacts to the new apex.db schema with filters and pagination
"""

import os
from typing import Dict, List, Optional
from hubspot import HubSpot
from hubspot.crm.contacts import ApiException
from services.contact_service import create_contact, update_contact, get_contact_by_hubspot_id

class HubSpotSyncV2:
    """Sync HubSpot contacts to apex.db"""

    def __init__(self):
        self.api_key = os.getenv("HUBSPOT_API_KEY") or os.getenv("HUBSPOT_TOKEN")
        if not self.api_key:
            raise ValueError("HUBSPOT_API_KEY or HUBSPOT_TOKEN not set")
        self.client = HubSpot(access_token=self.api_key)

    def sync_contacts(self, limit: int = 100, apply_filters: bool = True) -> Dict:
        """
        Sync contacts from HubSpot to apex.db with pagination
        
        Filters:
        - Must have email, company name, and name
        - No lead_status or unqualified lead_status
        - No lifecycle_stage or exclude "unsubscribe", "customer", "evangelist"
        """
        stats = {"imported": 0, "updated": 0, "skipped": 0, "errors": []}
        
        try:
            properties = [
                "firstname", "lastname", "email", "phone", "mobilephone",
                "company", "jobtitle", "hs_object_id", "hs_linkedin_url",
                "lifecyclestage", "hs_lead_status"
            ]
            
            processed = 0
            after = None
            
            # Paginate through HubSpot API (max 100 per page)
            while processed < limit:
                batch_size = min(100, limit - processed + 50)  # Extra for filtering
                contacts_page = self.client.crm.contacts.basic_api.get_page(
                    limit=batch_size,
                    properties=properties,
                    archived=False,
                    after=after
                )
                
                if not contacts_page.results:
                    break  # No more contacts
                
                for hs_contact in contacts_page.results:
                    if processed >= limit:
                        break
                    
                    try:
                        props = hs_contact.properties
                        hubspot_id = hs_contact.id
                        
                        # Apply filters if enabled
                        if apply_filters:
                            # Must have email
                            email = props.get("email", "").strip() if props.get("email") else ""
                            if not email:
                                stats["skipped"] += 1
                                continue
                            
                            # Must have company
                            company = props.get("company", "").strip() if props.get("company") else ""
                            if not company:
                                stats["skipped"] += 1
                                continue
                            
                            # Must have name
                            first_name = props.get("firstname", "").strip() if props.get("firstname") else ""
                            last_name = props.get("lastname", "").strip() if props.get("lastname") else ""
                            if not first_name and not last_name:
                                stats["skipped"] += 1
                                continue
                            
                            # Filter by lead_status: exclude "unqualified"
                            lead_status = props.get("hs_lead_status", "").lower()
                            if lead_status == "unqualified":
                                stats["skipped"] += 1
                                continue
                            
                            # Filter by lifecycle_stage: exclude unsubscribe, customer, evangelist
                            lifecycle = props.get("lifecyclestage", "").lower()
                            if lifecycle in ["unsubscribe", "customer", "evangelist"]:
                                stats["skipped"] += 1
                                continue
                        
                        # Map HubSpot fields to our schema
                        contact_data = {
                            "hubspot_id": hubspot_id,
                            "first_name": props.get("firstname", ""),
                            "last_name": props.get("lastname", ""),
                            "email": props.get("email"),
                            "phone": props.get("phone") or props.get("mobilephone"),
                            "title": props.get("jobtitle"),
                            "company": props.get("company")
                        }
                        
                        # Check if contact exists
                        existing = get_contact_by_hubspot_id(hubspot_id)
                        if existing:
                            update_contact(existing["id"], **contact_data)
                            stats["updated"] += 1
                        else:
                            create_contact(**contact_data)
                            stats["imported"] += 1
                        
                        processed += 1
                    
                    except Exception as e:
                        stats["errors"].append(f"Error processing contact {hubspot_id}: {str(e)}")
                
                # Check for next page
                if hasattr(contacts_page, 'paging') and contacts_page.paging:
                    after = contacts_page.paging.next.after
                else:
                    break  # No more pages
            
            return stats
        
        except ApiException as e:
            raise Exception(f"HubSpot API error: {e}")

def sync_hubspot_contacts(limit: int = 100, apply_filters: bool = True) -> Dict:
    """Convenience function for syncing"""
    syncer = HubSpotSyncV2()
    return syncer.sync_contacts(limit, apply_filters)

if __name__ == "__main__":
    result = sync_hubspot_contacts(limit=10, apply_filters=True)
    print(f"✅ Sync complete: {result}")
