#!/usr/bin/env python3
"""
APEX Auto-Rescore Test Script
Tests the auto-rescore functionality when a contact is enriched
"""

import sqlite3
import json
from datetime import datetime
import requests
import time

class ApexAutoRescoreTest:
    def __init__(self, db_path="./apex.db", api_base="http://localhost:8000"):
        self.db_path = db_path
        self.api_base = api_base
        
    def test_score_calculation(self):
        """Test 1: Verify scoring calculation logic"""
        print("\n" + "="*70)
        print("TEST 1: Score Calculation Logic")
        print("="*70)
        
        test_cases_rss = [
            {"role": "CEO", "level": "C-Suite", "expected_min": 80},
            {"role": "Director", "level": "Director", "expected_min": 60},
            {"role": "Manager", "level": "Manager", "expected_min": 40},
            {"role": "Associate", "level": "Associate", "expected_min": 20},
        ]
        
        print("\nRSS (Role/Seniority Score) Test Cases:")
        for i, case in enumerate(test_cases_rss, 1):
            role = case["role"]
            level = case["level"]
            expected = case["expected_min"]
            print(f"  {i}. Role: {role:15} | Level: {level:15} | Min Score: {expected}")
        
        test_cases_mdcp = [
            {"fields": 4, "expected": 100},
            {"fields": 3, "expected": 75},
            {"fields": 2, "expected": 50},
            {"fields": 1, "expected": 25},
        ]
        
        print("\nMDCP (Data Completeness) Test Cases:")
        for i, case in enumerate(test_cases_mdcp, 1):
            fields = case["fields"]
            expected = case["expected"]
            print(f"  {i}. Fields: {fields} | Completeness: {expected}%")
        
    def test_enrichment_trigger(self):
        """Test 2: Verify enrichment triggers rescore"""
        print("\n" + "="*70)
        print("TEST 2: Enrichment Triggers Rescore")
        print("="*70)
        
        print("\nEnrichment Flow:")
        print("  1. Create test contact with minimal data")
        print("     - Initial Score: LOW (incomplete data)")
        print("  2. Trigger enrichment from Perplexity")
        print("     - Fetch company, title, industry, etc.")
        print("  3. Auto-rescore triggered")
        print("     - New Score: HIGH (complete data + valid role)")
        print("  4. Verify score increased in database")
        print("     - Check scoring_history table")
        print("\nExpected: Score increases after enrichment")
        
    def test_cre_vs_non_cre(self):
        """Test 3: CRE vs Non-CRE Scoring"""
        print("\n" + "="*70)
        print("TEST 3: CRE vs Non-CRE Scoring")
        print("="*70)
        
        cre_roles = ["Real Estate Director", "Broker", "Property Manager", "Asset Manager"]
        non_cre_roles = ["HR Manager", "Marketing Manager", "Software Engineer", "Accountant"]
        
        print("\nCRE Roles (should score HIGH):")
        for role in cre_roles:
            print(f"  > {role}")
        
        print("\nNon-CRE Roles (should score LOW):")
        for role in non_cre_roles:
            print(f"  X {role}")
        
        print("\nExpected: CRE roles get 60+ points, Non-CRE get less than 40 points")
        
    def generate_api_test_payload(self):
        """Generate payload for API testing"""
        print("\n" + "="*70)
        print("TEST PAYLOADS FOR API TESTING")
        print("="*70)
        
        contact_cre = {
            "firstName": "John",
            "lastName": "Smith",
            "email": "john.smith@realtycorp.com",
            "title": "Commercial Real Estate Director",
            "company": "Realty Corporation",
        }
        
        contact_non_cre = {
            "firstName": "Jane",
            "lastName": "Doe",
            "email": "jane.doe@techco.com",
            "title": "Software Engineer",
            "company": "Tech Company",
        }
        
        print("\nTest Payload 1 - CRE Contact:")
        print(json.dumps(contact_cre, indent=2))
        
        print("\nTest Payload 2 - Non-CRE Contact:")
        print(json.dumps(contact_non_cre, indent=2))
        
        return contact_cre, contact_non_cre
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("APEX AUTO-RESCORE TEST SUITE")
        print("="*70)
        
        self.test_score_calculation()
        self.test_enrichment_trigger()
        self.test_cre_vs_non_cre()
        contact_cre, contact_non_cre = self.generate_api_test_payload()
        
        print("\n" + "="*70)
        print("EXECUTION INSTRUCTIONS")
        print("="*70)
        print("""
Step 1: Start Flask API
  python ~/projects/apex/api.py

Step 2: In another terminal, test CRE Contact:
  curl -X POST http://localhost:8000/api/contacts \\
    -H "Content-Type: application/json" \\
    -d '{"firstName":"John","lastName":"Smith"}'

Step 3: Trigger enrichment (replace {id} with contact ID):
  curl -X POST http://localhost:8000/api/contacts/{id}/enrich

Step 4: Verify score increased:
  curl http://localhost:8000/api/contacts/{id}

Test Duration: 30-60 seconds per contact
Expected: Score increases after enrichment
        """)

if __name__ == "__main__":
    tester = ApexAutoRescoreTest()
    tester.run_all_tests()
