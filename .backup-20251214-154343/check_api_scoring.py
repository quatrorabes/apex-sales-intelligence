#!/usr/bin/env python3
"""
APEX API Scoring Logic Checker
Identifies why scores aren't being calculated
"""

import requests
import json

class ApexAPIChecker:
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base

    def check_enrichment_response(self, contact_id=1):
        """Check what enrichment endpoint returns"""
        print("="*70)
        print(f"CHECKING ENRICHMENT RESPONSE FOR CONTACT {contact_id}")
        print("="*70)

        try:
            response = requests.post(
                f"{self.api_base}/api/contacts/{contact_id}/enrich",
                timeout=60
            )

            print(f"\nStatus Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print("\nResponse JSON:")
                print(json.dumps(data, indent=2))

                # Check for scoring data
                print("\n" + "="*70)
                print("SCORING DATA CHECK")
                print("="*70)

                scoring_keys = ['rss_score', 'mdcp_score', 'priority_score', 
                               'score', 'scores', 'scoring']

                found_scoring = False
                for key in scoring_keys:
                    if key in data:
                        print(f"\n✓ Found scoring data in '{key}':")
                        print(f"  {data[key]}")
                        found_scoring = True

                if not found_scoring:
                    print("\n✗ No scoring data in response")
                    print("\nThis means:")
                    print("  1. Enrichment completed BUT")
                    print("  2. Scoring function was not called")
                    print("  3. Need to check api.py enrichment endpoint")

                # Check enrichment data
                if 'enrichment_data' in data:
                    print("\n✓ Enrichment data present:")
                    enrich = data['enrichment_data']
                    for key in ['title', 'company', 'industry', 'role']:
                        if key in enrich:
                            print(f"  {key}: {enrich[key]}")
            else:
                print(f"\nError response: {response.text}")

        except Exception as e:
            print(f"\n✗ Error: {e}")

    def check_contact_endpoint(self, contact_id=1):
        """Check contact details endpoint"""
        print("\n" + "="*70)
        print(f"CHECKING CONTACT DETAILS FOR ID {contact_id}")
        print("="*70)

        try:
            response = requests.get(f"{self.api_base}/api/contacts/{contact_id}")

            if response.status_code == 200:
                data = response.json()
                print("\nContact data:")

                important_fields = [
                    'id', 'name', 'title', 'company',
                    'rss_score', 'mdcp_score', 'priority_score',
                    'enrichment_status', 'enriched_at'
                ]

                for field in important_fields:
                    value = data.get(field, 'MISSING')
                    print(f"  {field:20}: {value}")

        except Exception as e:
            print(f"\n✗ Error: {e}")

    def suggest_api_fixes(self):
        """Suggest what to check in api.py"""
        print("\n" + "="*70)
        print("API.PY SCORING INTEGRATION CHECKLIST")
        print("="*70)

        print("""
Based on the test results, check these in ~/projects/apex/api.py:

1. ENRICHMENT ENDPOINT (/api/contacts/<id>/enrich)
   ─────────────────────────────────────────────────
   After enrichment completes, does it:

   [ ] Call the scoring function?
       → Example: scores = calculate_scores(contact)

   [ ] Update the contact record with scores?
       → Example: contact.rss_score = scores['rss']
                  contact.mdcp_score = scores['mdcp']
                  contact.priority_score = scores['priority']

   [ ] Commit to database?
       → Example: db.session.commit()

   [ ] Insert into scoring_history?
       → Example: history = ScoringHistory(...)
                  db.session.add(history)

2. SCORING FUNCTION LOCATION
   ──────────────────────────
   Check if scoring logic is in:

   [ ] apps/backend/intelligence/engines/scoring/
   [ ] Function imported in api.py?
   [ ] Function being called after enrichment?

3. DATABASE MODELS
   ────────────────
   [ ] Contact model has score fields?
   [ ] ScoringHistory model exists?
   [ ] Relationships defined correctly?

4. COMMON ISSUES
   ─────────────
   ✗ Scoring function exists but not called after enrichment
   ✗ Scores calculated but not saved to database
   ✗ Database commit missing
   ✗ Scoring history not being recorded

RECOMMENDED FIX:
───────────────
In api.py, find the /api/contacts/<id>/enrich endpoint and add:

    # After enrichment completes
    from apps.backend.intelligence.engines.scoring import calculate_scores

    scores = calculate_scores(contact)
    contact.rss_score = scores['rss']
    contact.mdcp_score = scores['mdcp'] 
    contact.priority_score = scores['priority']
    contact.enrichment_status = 'complete'
    db.session.commit()

    # Record in history
    history = ScoringHistory(
        contact_id=contact.id,
        trigger='enrichment',
        old_priority_score=0,
        new_priority_score=scores['priority'],
        # ... other fields
    )
    db.session.add(history)
    db.session.commit()
"""        )

    def run_all_checks(self):
        """Run all API checks"""
        print("\n" + "🔍 "*25)
        print("APEX API SCORING LOGIC DIAGNOSTIC")
        print("🔍 "*25)

        # Check enrichment response
        self.check_enrichment_response(contact_id=1)

        # Check contact details
        self.check_contact_endpoint(contact_id=1)

        # Suggest fixes
        self.suggest_api_fixes()

if __name__ == "__main__":
    checker = ApexAPIChecker()
    checker.run_all_checks()
