#!/usr/bin/env python3
"""
HUBSPOT SYNC - FIXED FOR YOUR EXACT SCHEMA
- Uses hubspot_id field (not id)
- Maps to title (not job_title)
- Uses email as upsert key
"""

import os
import sys
import logging
import requests
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class HubSpotSyncEngine:
    
    HUBSPOT_PROPERTIES = [
        'firstname', 'lastname', 'email', 'phone', 'mobilephone', 
        'company', 'jobtitle', 'hs_linkedin_url', 'linkedinbio', 
        'lifecyclestage', 'hs_lead_status', 'lead_status'
    ]
    
    def __init__(self, hubspot_token: str, db_connection):
        self.hubspot_token = hubspot_token
        self.db = db_connection
        self.search_url = 'https://api.hubapi.com/crm/v3/objects/contacts/search'
        
    def fetch_all_contacts(self) -> List[Dict]:
        """Fetch ALL contacts in batches"""
        all_contacts = []
        after = None
        
        headers = {
            'Authorization': f'Bearer {self.hubspot_token}',
            'Content-Type': 'application/json'
        }
        
        logger.info("=" * 80)
        logger.info("📡 FETCHING FROM HUBSPOT")
        logger.info("=" * 80)
        
        query = {
            "filterGroups": [{
                "filters": [
                    {"propertyName": "firstname", "operator": "HAS_PROPERTY"},
                    {"propertyName": "email", "operator": "HAS_PROPERTY"},
                    {"propertyName": "company", "operator": "HAS_PROPERTY"}
                ]
            }],
            "properties": self.HUBSPOT_PROPERTIES,
            "limit": 100
        }
        
        while True:
            try:
                if after:
                    query['after'] = after
                
                response = requests.post(self.search_url, headers=headers, json=query, timeout=30)
                
                if response.status_code != 200:
                    logger.error(f"❌ API error: {response.status_code}")
                    break
                
                data = response.json()
                batch = data.get('results', [])
                all_contacts.extend(batch)
                
                logger.info(f"📦 Fetched {len(batch)} (Total: {len(all_contacts)})")
                
                paging = data.get('paging', {})
                after = paging.get('next', {}).get('after')
                
                if not after:
                    break
                    
            except Exception as e:
                logger.error(f"❌ Error: {e}")
                break
        
        logger.info(f"✅ Total: {len(all_contacts)}")
        return all_contacts
    
    def map_contact(self, hs_contact: Dict) -> Dict:
        """Map to YOUR EXACT schema"""
        props = hs_contact.get('properties', {})
        
        def get_first(*fields):
            for field in fields:
                value = props.get(field)
                if value and str(value).strip():
                    return str(value).strip()
            return None
        
        # Extract LinkedIn
        linkedin_url = get_first('hs_linkedin_url', 'linkedinbio')
        if linkedin_url:
            linkedin_url = self._clean_linkedin_url(linkedin_url)
        
        # Build name
        first = get_first('firstname')
        last = get_first('lastname')
        full_name = f"{first} {last}" if (first and last) else (first or last or "Unknown")
        
        # Map to YOUR EXACT schema
        return {
            'hubspot_id': str(hs_contact.get('id')),  # Use hubspot_id field!
            'name': full_name,
            'firstname': first,
            'lastname': last,
            'email': get_first('email'),
            'phone': get_first('phone', 'mobilephone'),
            'phone_mobile': get_first('mobilephone'),
            'company': get_first('company'),
            'title': get_first('jobtitle'),  # Map to 'title' not 'job_title'!
            'linkedin_url': linkedin_url,
            'lead_status': get_first('hs_lead_status', 'lead_status'),
            'lifecycle_stage': get_first('lifecyclestage'),
            'enrichment_status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
    
    def _clean_linkedin_url(self, url: str) -> Optional[str]:
        """Clean LinkedIn URL"""
        url = url.strip().rstrip('/')
        
        if not url.startswith('http'):
            if url.startswith('linkedin.com'):
                url = f'https://{url}'
            else:
                url = f'https://linkedin.com/in/{url}'
        
        return url if 'linkedin.com' in url.lower() else None
    
    def filter_qualified(self, contacts: List[Dict]) -> List[Dict]:
        """Filter qualified contacts"""
        qualified = []
        
        for contact in contacts:
            props = contact.get('properties', {})
            
            # Skip unqualified
            lead_status = (props.get('hs_lead_status') or '').lower()
            if lead_status == 'unqualified':
                continue
            
            lifecycle = (props.get('lifecyclestage') or '').lower()
            if lifecycle == 'unqualified':
                continue
            
            # Must have basics
            if not props.get('firstname'):
                continue
            if not props.get('email'):
                continue
            if not props.get('company'):
                continue
            
            qualified.append(contact)
        
        return qualified
    
    def sync_to_database(self, contacts: List[Dict]) -> Dict:
        """Sync to database"""
        stats = {
            'total': len(contacts),
            'synced': 0,
            'inserted': 0,
            'updated': 0,
            'errors': 0,
            'with_linkedin': 0
        }
        
        for idx, hs_contact in enumerate(contacts, 1):
            try:
                mapped = self.map_contact(hs_contact)
                
                if mapped.get('linkedin_url'):
                    stats['with_linkedin'] += 1
                
                # Upsert
                was_update = self._upsert_contact(mapped)
                
                if was_update is not None:
                    stats['synced'] += 1
                    if was_update:
                        stats['updated'] += 1
                    else:
                        stats['inserted'] += 1
                    
                    if idx % 100 == 0:
                        logger.info(f"   Progress: {idx}/{len(contacts)}")
                else:
                    stats['errors'] += 1
                    
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"❌ Error on contact {idx}: {e}")
        
        return stats
    
    def _upsert_contact(self, contact_data: Dict) -> Optional[bool]:
        """
        Upsert using email as key (not id)
        Returns: True if updated, False if inserted, None if failed
        """
        cursor = self.db.cursor()
        email = contact_data.get('email')
        
        try:
            # Check if exists by EMAIL
            cursor.execute("SELECT id FROM contacts WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if existing:
                # UPDATE existing
                contact_id = existing[0] if isinstance(existing, tuple) else existing['id']
                
                update_fields = []
                values = []
                
                for key, value in contact_data.items():
                    if key != 'created_at':  # Don't update created_at
                        update_fields.append(f"{key} = ?")
                        values.append(value)
                
                values.append(contact_id)
                
                sql = f"UPDATE contacts SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(sql, values)
                self.db.commit()
                return True
            else:
                # INSERT new (let SQLite auto-generate id)
                insert_data = {k: v for k, v in contact_data.items() if v is not None}
                
                columns = list(insert_data.keys())
                placeholders = ', '.join(['?' for _ in columns])
                values = [insert_data[col] for col in columns]
                
                sql = f"INSERT INTO contacts ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                self.db.commit()
                return False
                
        except Exception as e:
            logger.error(f"❌ DB error: {e}")
            self.db.rollback()
            return None
    
    def run_full_sync(self) -> Dict:
        """Execute full sync"""
        # Fetch
        all_contacts = self.fetch_all_contacts()
        
        if not all_contacts:
            return {'success': False, 'error': 'No contacts fetched'}
        
        # Filter
        logger.info("\n🔍 FILTERING")
        logger.info("=" * 80)
        qualified = self.filter_qualified(all_contacts)
        logger.info(f"Fetched: {len(all_contacts)}")
        logger.info(f"Qualified: {len(qualified)}")
        
        if not qualified:
            return {'success': False, 'error': 'No qualified contacts'}
        
        # Sync
        logger.info("\n💾 SYNCING")
        logger.info("=" * 80)
        
        stats = self.sync_to_database(qualified)
        
        logger.info("=" * 80)
        logger.info("✅ COMPLETE")
        logger.info(f"   Synced: {stats['synced']}")
        logger.info(f"   Inserted: {stats['inserted']}")
        logger.info(f"   Updated: {stats['updated']}")
        logger.info(f"   Errors: {stats['errors']}")
        logger.info(f"   With LinkedIn: {stats['with_linkedin']}")
        logger.info("=" * 80)
        
        return {'success': True, **stats}


def main():
    import sqlite3
    
    token = os.getenv('HUBSPOT_ACCESS_TOKEN')
    if not token:
        print("❌ HUBSPOT_ACCESS_TOKEN not found")
        sys.exit(1)
    
    db = sqlite3.connect('./apex.db')
    db.row_factory = sqlite3.Row
    
    sync = HubSpotSyncEngine(token, db)
    result = sync.run_full_sync()
    
    db.close()
    
    if result['success']:
        print(f"\n🎉 SUCCESS!")
        print(f"   Synced: {result['synced']}")
        print(f"   Inserted: {result['inserted']}")
        print(f"   Updated: {result['updated']}")
        print(f"   With LinkedIn: {result['with_linkedin']}")
    else:
        print(f"❌ Failed: {result.get('error')}")


if __name__ == '__main__':
    main()
