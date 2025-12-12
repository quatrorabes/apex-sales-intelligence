"""
HubSpot Sync Module
Handles bi-directional sync between APEX and HubSpot
Integrates with scoring and persona classification
"""

import requests
import os
from typing import Dict, List, Optional
import sqlite3
from datetime import datetime
import json

class HubSpotSync:
    """Sync contacts and enrichment data with HubSpot"""
    
    def __init__(self, api_key: str = None, db_path: str = "./apex.db"):
        self.api_key = api_key or os.getenv("HUBSPOT_API_KEY")
        if not self.api_key:
            print("⚠️  Warning: HUBSPOT_API_KEY not set. HubSpot features disabled.")
        
        self.base_url = "https://api.hubapi.com"
        self.db_path = db_path
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        } if self.api_key else {}
    
    def import_contacts_from_hubspot(self, limit: int = 100) -> List[Dict]:
        """Import contacts from HubSpot"""
        
        if not self.api_key:
            print("❌ HubSpot API key not configured")
            return []
        
        url = f"{self.base_url}/crm/v3/objects/contacts"
        params = {
            "limit": limit,
            "properties": [
                "firstname", "lastname", "email", "phone", "company",
                "jobtitle", "industry", "hs_linkedin_url", "hs_object_id",
                "hs_analytics_source", "hs_lead_status", "lifecyclestage",
                "numemployees", "annualrevenue", "city", "state", "website"
            ]
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            contacts = data.get("results", [])
            
            print(f"✅ Retrieved {len(contacts)} contacts from HubSpot")
            
            # Save to database
            imported_count = self._save_contacts_to_db(contacts)
            
            return contacts
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error importing from HubSpot: {e}")
            return []
    
    def _save_contacts_to_db(self, contacts: List[Dict]) -> int:
        """Save HubSpot contacts to local database"""
        
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        saved_count = 0
        
        for contact in contacts:
            props = contact.get("properties", {})
            hubspot_id = contact.get("id")
            
            try:
                # Check if contact already exists
                cursor.execute("SELECT id FROM contacts WHERE hubspot_id = ?", (hubspot_id,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing
                    cursor.execute("""
                        UPDATE contacts SET
                            first_name = ?,
                            last_name = ?,
                            email = ?,
                            phone = ?,
                            company = ?,
                            title = ?,
                            industry = ?,
                            linkedin_url = ?,
                            updated_at = ?
                        WHERE hubspot_id = ?
                    """, (
                        props.get("firstname"),
                        props.get("lastname"),
                        props.get("email"),
                        props.get("phone"),
                        props.get("company"),
                        props.get("jobtitle"),
                        props.get("industry"),
                        props.get("hs_linkedin_url"),
                        datetime.now().isoformat(),
                        hubspot_id
                    ))
                else:
                    # Insert new
                    cursor.execute("""
                        INSERT INTO contacts (
                            hubspot_id, first_name, last_name, email, phone,
                            company, title, industry, linkedin_url,
                            created_at, updated_at, enrichment_status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        hubspot_id,
                        props.get("firstname"),
                        props.get("lastname"),
                        props.get("email"),
                        props.get("phone"),
                        props.get("company"),
                        props.get("jobtitle"),
                        props.get("industry"),
                        props.get("hs_linkedin_url"),
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        "pending"
                    ))
                
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving contact {props.get('email')}: {e}")
        
        db.commit()
        db.close()
        
        print(f"✅ Saved {saved_count} contacts to database")
        return saved_count
    
    def sync_scores_to_hubspot(self, contact_id: int, scores: Dict) -> bool:
        """Sync APEX scores and persona back to HubSpot"""
        
        if not self.api_key:
            print("⚠️  HubSpot sync skipped (no API key)")
            return False
        
        # Get HubSpot ID from database
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        cursor.execute("SELECT hubspot_id FROM contacts WHERE id = ?", (contact_id,))
        result = cursor.fetchone()
        db.close()
        
        if not result or not result[0]:
            print(f"⚠️  No HubSpot ID found for contact {contact_id}")
            return False
        
        hubspot_id = result[0]
        
        # Prepare custom properties (using safe field names)
        properties = {
            "apex_mdcp_score": str(scores.get("mdcp_score", 0)),
            "apex_mdcp_tier": str(scores.get("mdcp_tier", "")),
            "apex_rss_score": str(scores.get("rss_score", 0)),
            "apex_rss_tier": str(scores.get("rss_tier", "")),
            "apex_priority_score": str(scores.get("priority_score", 0)),
            "apex_urgency_level": str(scores.get("urgency_level", "")),
            "apex_persona_tier": str(scores.get("persona_tier", "")),
            "apex_persona_type": str(scores.get("persona_type", "")),
            "apex_persona_confidence": str(scores.get("persona_confidence", 0)),
            "apex_last_scored": datetime.now().isoformat()
        }
        
        url = f"{self.base_url}/crm/v3/objects/contacts/{hubspot_id}"
        
        try:
            response = requests.patch(
                url,
                headers=self.headers,
                json={"properties": properties}
            )
            response.raise_for_status()
            
            print(f"✅ Synced scores to HubSpot for contact {contact_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error syncing to HubSpot: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return False
    
    def create_hubspot_custom_properties(self):
        """Create APEX custom properties in HubSpot (one-time setup)"""
        
        if not self.api_key:
            print("❌ HubSpot API key required for property creation")
            return 0
        
        properties = [
            {
                "name": "apex_mdcp_score",
                "label": "APEX MDCP Score",
                "type": "number",
                "fieldType": "number",
                "groupName": "apex_intelligence",
                "description": "Money, Decision, Credibility, Pain score"
            },
            {
                "name": "apex_mdcp_tier",
                "label": "APEX MDCP Tier",
                "type": "enumeration",
                "fieldType": "select",
                "options": [
                    {"label": "HOT", "value": "HOT"},
                    {"label": "WARM", "value": "WARM"},
                    {"label": "QUALIFIED", "value": "QUALIFIED"},
                    {"label": "COLD", "value": "COLD"}
                ],
                "groupName": "apex_intelligence"
            },
            {
                "name": "apex_rss_score",
                "label": "APEX RSS Score",
                "type": "number",
                "fieldType": "number",
                "groupName": "apex_intelligence",
                "description": "Relationship Strength Score"
            },
            {
                "name": "apex_priority_score",
                "label": "APEX Priority Score",
                "type": "number",
                "fieldType": "number",
                "groupName": "apex_intelligence",
                "description": "Combined priority (MDCP + RSS)"
            },
            {
                "name": "apex_urgency_level",
                "label": "APEX Urgency",
                "type": "enumeration",
                "fieldType": "select",
                "options": [
                    {"label": "IMMEDIATE", "value": "IMMEDIATE"},
                    {"label": "HIGH", "value": "HIGH"},
                    {"label": "MEDIUM", "value": "MEDIUM"},
                    {"label": "LOW", "value": "LOW"}
                ],
                "groupName": "apex_intelligence"
            },
            {
                "name": "apex_persona_tier",
                "label": "APEX Persona Tier",
                "type": "enumeration",
                "fieldType": "select",
                "options": [
                    {"label": "Tier 1 (Referral)", "value": "Tier 1"},
                    {"label": "Tier 2 (Borrower)", "value": "Tier 2"},
                    {"label": "Unclassified", "value": "Unclassified"}
                ],
                "groupName": "apex_intelligence"
            },
            {
                "name": "apex_persona_type",
                "label": "APEX Persona Type",
                "type": "string",
                "fieldType": "text",
                "groupName": "apex_intelligence",
                "description": "Detailed persona classification"
            },
            {
                "name": "apex_persona_confidence",
                "label": "APEX Persona Confidence",
                "type": "number",
                "fieldType": "number",
                "groupName": "apex_intelligence"
            },
            {
                "name": "apex_last_scored",
                "label": "APEX Last Scored",
                "type": "datetime",
                "fieldType": "date",
                "groupName": "apex_intelligence"
            }
        ]
        
        url = f"{self.base_url}/crm/v3/properties/contacts"
        
        created_count = 0
        
        for prop in properties:
            try:
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=prop
                )
                
                if response.status_code in [200, 201]:
                    created_count += 1
                    print(f"✅ Created property: {prop['name']}")
                elif response.status_code == 409:
                    print(f"ℹ️  Property already exists: {prop['name']}")
                    created_count += 1
                else:
                    print(f"⚠️  Property {prop['name']}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️  Property {prop['name']}: {e}")
        
        print(f"\n✅ Created/verified {created_count} HubSpot custom properties")
        return created_count

# Quick utility functions
def import_from_hubspot(api_key: str = None, limit: int = 100) -> List[Dict]:
    """Quick function to import contacts"""
    sync = HubSpotSync(api_key)
    return sync.import_contacts_from_hubspot(limit)

def setup_hubspot_properties(api_key: str = None):
    """Quick function to setup custom properties"""
    sync = HubSpotSync(api_key)
    return sync.create_hubspot_custom_properties()

if __name__ == "__main__":
    print("🔄 HubSpot Sync Module")
    print("=" * 60)
    
    # Test connection
    api_key = os.getenv("HUBSPOT_API_KEY")
    if api_key:
        print(f"✅ API key found: {api_key[:10]}...")
        sync = HubSpotSync(api_key)
        print("\n📝 Ready to:")
        print("  - Import contacts: sync.import_contacts_from_hubspot()")
        print("  - Setup properties: sync.create_hubspot_custom_properties()")
        print("  - Sync scores: sync.sync_scores_to_hubspot(contact_id, scores)")
    else:
        print("❌ No HUBSPOT_API_KEY found in environment")
        print("Set it with: export HUBSPOT_API_KEY='your-key-here'")
