"""
HubSpot Sync Adapter v2
Syncs HubSpot contacts to the new apex.db schema
"""
import os
from typing import Dict, List, Optional
from hubspot import HubSpot
import sys
import os as os_module
sys.path.insert(0, os_module.path.dirname(os_module.path.dirname(os_module.path.abspath(__file__))))

from hubspot.crm.contacts import ApiException

from services.contact_service import create_contact, update_contact, get_contact_by_hubspot_id

class HubSpotSyncV2:
    """Sync HubSpot contacts to apex.db"""
    
    def __init__(self):
        self.api_key = os.getenv("HUBSPOT_API_KEY") or os.getenv("HUBSPOT_TOKEN")
        if not self.api_key:
            raise ValueError("HUBSPOT_API_KEY or HUBSPOT_TOKEN not set")
        
        self.client = HubSpot(access_token=self.api_key)
    
    def sync_contacts(self, limit: int = 100) -> Dict:
        """
        Sync contacts from HubSpot to apex.db
        Returns: {imported: int, updated: int, skipped: int, errors: list}
        """
        stats = {"imported": 0, "updated": 0, "skipped": 0, "errors": []}
        
        try:
            # Fetch contacts from HubSpot
            properties = [
                "firstname", "lastname", "email", "phone", "mobilephone",
                "company", "jobtitle", "hs_object_id", "hs_linkedin_url"
            ]
            
            contacts_page = self.client.crm.contacts.basic_api.get_page(
                limit=limit,
                properties=properties,
                archived=False
            )
            
            for hs_contact in contacts_page.results:
                try:
                    props = hs_contact.properties
                    hubspot_id = hs_contact.id
                    
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
                    
                    # Skip if missing critical data
                    if not contact_data["first_name"] and not contact_data["last_name"]:
                        stats["skipped"] += 1
                        continue
                    
                    # Check if contact exists
                    existing = get_contact_by_hubspot_id(hubspot_id)
                    
                    if existing:
                        # Update existing contact
                        update_contact(existing["id"], **contact_data)
                        stats["updated"] += 1
                    else:
                        # Create new contact
                        create_contact(**contact_data)
                        stats["imported"] += 1
                
                except Exception as e:
                    stats["errors"].append(f"Error processing contact {hubspot_id}: {str(e)}")
            
            return stats
        
        except ApiException as e:
            raise Exception(f"HubSpot API error: {e}")


def sync_hubspot_contacts(limit: int = 100) -> Dict:
    """Convenience function for syncing"""
    syncer = HubSpotSyncV2()
    return syncer.sync_contacts(limit)


if __name__ == "__main__":
    # Test sync
    result = sync_hubspot_contacts(limit=10)
    print(f"✅ Sync complete: {result}")
