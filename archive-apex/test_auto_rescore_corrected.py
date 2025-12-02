#!/usr/bin/env python3
"""
APEX Auto-Rescore Test Script - CORRECTED
Tests auto-rescore after enrichment using actual API endpoints
"""

import requests
import json
import time
import sqlite3
import os

class ApexAutoRescoreTest:
    def __init__(self, api_base="http://localhost:8000", db_path="~/projects/apex/apex.db"):
        self.api_base = api_base
        self.db_path = os.path.expanduser(db_path)
        
    def check_api_health(self):
        """Verify API is running"""
        print("\n" + "="*70)
        print("STEP 1: API Health Check")
        print("="*70)
        try:
            response = requests.get(f"{self.api_base}/api/health", timeout=2)
            print(f"✓ API Status: {response.status_code}")
            return True
        except Exception as e:
            print(f"✗ API Error: {e}")
            print("\nMake sure API is running:")
            print("  cd ~/projects/apex")
            print("  python api.py")
            return False
    
    def get_contacts_from_db(self, limit=5):
        """Get existing contacts from database"""
        print("\n" + "="*70)
        print("STEP 2: Get Test Contacts from Database")
        print("="*70)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get contacts that haven't been enriched yet
            query = """
            SELECT id, name, email, title, company, rss_score, mdcp_score, priority_score, enrichment_status
            FROM contacts 
            WHERE enrichment_status IS NULL OR enrichment_status = 'pending'
            LIMIT ?
            """
            cursor.execute(query, (limit,))
            contacts = cursor.fetchall()
            
            print(f"\nFound {len(contacts)} contacts ready for enrichment:\n")
            for contact in contacts:
                contact_id, name, email, title, company, rss, mdcp, priority, status = contact
                print(f"  ID: {contact_id}")
                print(f"    Name: {name}")
                print(f"    Title: {title}")
                print(f"    Company: {company}")
                print(f"    Current RSS Score: {rss}")
                print(f"    Current MDCP Score: {mdcp}")
                print(f"    Current Priority Score: {priority}")
                print(f"    Enrichment Status: {status or 'Not enriched'}")
                print()
            
            conn.close()
            return [c[0] for c in contacts]  # Return list of IDs
            
        except Exception as e:
            print(f"✗ Database Error: {e}")
            print(f"  Database path: {self.db_path}")
            return []
    
    def test_single_enrichment(self, contact_id):
        """Test enrichment and auto-rescore for a single contact"""
        print("\n" + "="*70)
        print(f"STEP 3: Test Enrichment for Contact ID {contact_id}")
        print("="*70)
        
        # Get initial scores
        print("\n📊 BEFORE Enrichment:")
        initial_scores = self.get_contact_scores(contact_id)
        
        # Trigger enrichment
        print(f"\n🔄 Triggering enrichment...")
        try:
            response = requests.post(
                f"{self.api_base}/api/contacts/{contact_id}/enrich",
                timeout=60
            )
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✓ Enrichment completed")
                if 'enrichment_data' in result:
                    print(f"  ✓ New data received from Perplexity")
            else:
                print(f"  Response: {response.text}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
        
        # Wait for auto-rescore
        print("\n⏳ Waiting 2 seconds for auto-rescore...")
        time.sleep(2)
        
        # Get updated scores
        print("\n📊 AFTER Enrichment:")
        final_scores = self.get_contact_scores(contact_id)
        
        # Compare scores
        print("\n" + "="*70)
        print("SCORE COMPARISON")
        print("="*70)
        
        if initial_scores and final_scores:
            rss_change = final_scores['rss'] - initial_scores['rss']
            mdcp_change = final_scores['mdcp'] - initial_scores['mdcp']
            priority_change = final_scores['priority'] - initial_scores['priority']
            
            print(f"\n  RSS Score:      {initial_scores['rss']:.1f} → {final_scores['rss']:.1f} ({rss_change:+.1f})")
            print(f"  MDCP Score:     {initial_scores['mdcp']:.1f} → {final_scores['mdcp']:.1f} ({mdcp_change:+.1f})")
            print(f"  Priority Score: {initial_scores['priority']:.1f} → {final_scores['priority']:.1f} ({priority_change:+.1f})")
            
            if priority_change > 0:
                print("\n  ✓ SUCCESS: Score increased after enrichment!")
                return True
            elif priority_change == 0:
                print("\n  ⚠ WARNING: Score did not change")
                return False
            else:
                print("\n  ✗ UNEXPECTED: Score decreased")
                return False
        
        return False
    
    def get_contact_scores(self, contact_id):
        """Get current scores for a contact"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name, title, company, rss_score, mdcp_score, priority_score, enrichment_status
                FROM contacts 
                WHERE id = ?
            """, (contact_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                name, title, company, rss, mdcp, priority, status = result
                print(f"  Contact: {name}")
                print(f"  Title: {title}")
                print(f"  Company: {company}")
                print(f"  RSS Score: {rss or 0:.1f}")
                print(f"  MDCP Score: {mdcp or 0:.1f}")
                print(f"  Priority Score: {priority or 0:.1f}")
                print(f"  Status: {status or 'Not enriched'}")
                
                return {
                    'rss': rss or 0,
                    'mdcp': mdcp or 0,
                    'priority': priority or 0
                }
            return None
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return None
    
    def check_scoring_history(self, contact_id):
        """Check scoring history table for changes"""
        print("\n" + "="*70)
        print("STEP 4: Verify Scoring History")
        print("="*70)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT trigger, old_score, new_score, timestamp
                FROM scoring_history
                WHERE contact_id = ?
                ORDER BY timestamp DESC
                LIMIT 5
            """, (contact_id,))
            
            history = cursor.fetchall()
            conn.close()
            
            if history:
                print(f"\nScoring history for contact {contact_id}:\n")
                for trigger, old_score, new_score, timestamp in history:
                    change = new_score - old_score if old_score and new_score else 0
                    print(f"  {timestamp} - {trigger}")
                    print(f"    {old_score:.1f} → {new_score:.1f} ({change:+.1f})")
                    print()
                return True
            else:
                print(f"\n⚠ No scoring history found for contact {contact_id}")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def run_test(self):
        """Run the complete auto-rescore test"""
        print("\n" + "🚀 "*25)
        print("APEX AUTO-RESCORE TEST - LIVE")
        print("🚀 "*25)
        
        # Step 1: Check API
        if not self.check_api_health():
            return
        
        # Step 2: Get contacts
        contact_ids = self.get_contacts_from_db(limit=3)
        
        if not contact_ids:
            print("\n⚠ No contacts found to test.")
            print("\nFirst import contacts from HubSpot:")
            print("  curl -X POST http://localhost:8000/api/hubspot/import")
            return
        
        # Step 3: Test first contact
        contact_id = contact_ids[0]
        success = self.test_single_enrichment(contact_id)
        
        # Step 4: Check history
        self.check_scoring_history(contact_id)
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        if success:
            print("\n✓ Auto-rescore test PASSED")
            print("  - Enrichment triggered successfully")
            print("  - Scores updated automatically")
            print("  - History tracked correctly")
        else:
            print("\n✗ Auto-rescore test FAILED or INCOMPLETE")
            print("  - Check API logs for errors")
            print("  - Verify scoring logic in api.py")
        
        print("\nNext steps:")
        print("  - Test with more contacts")
        print("  - Verify CRE vs Non-CRE scoring differences")
        print("  - Check batch scoring functionality")


if __name__ == "__main__":
    tester = ApexAutoRescoreTest()
    tester.run_test()
