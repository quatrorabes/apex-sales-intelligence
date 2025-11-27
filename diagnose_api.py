#!/usr/bin/env python3
"""
APEX API Endpoint Diagnostic
Checks what endpoints are actually available
"""

import requests
import json

API_BASE = "http://localhost:8000"

print("="*70)
print("APEX API ENDPOINT DIAGNOSTIC")
print("="*70)

# Test 1: Check if API is running
print("\nTest 1: API Health Check")
try:
    response = requests.get(f"{API_BASE}/api/health", timeout=2)
    print(f"  Status: {response.status_code}")
    if response.status_code == 200:
        print("  Result: API is running")
    else:
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"  Error: {e}")

# Test 2: Check available routes (common patterns)
print("\nTest 2: Checking Common Endpoints")
endpoints_to_test = [
    ("/api/contacts", "GET"),
    ("/api/contacts", "POST"),
    ("/api/contact", "POST"),  # singular
    ("/contacts", "POST"),     # no /api prefix
    ("/api/import", "POST"),
    ("/api/enrich", "POST"),
]

for endpoint, method in endpoints_to_test:
    try:
        if method == "GET":
            response = requests.get(f"{API_BASE}{endpoint}", timeout=2)
        else:
            response = requests.post(f"{API_BASE}{endpoint}", 
                                    json={}, 
                                    timeout=2)
        print(f"  {method:6} {endpoint:30} -> {response.status_code}")
    except Exception as e:
        print(f"  {method:6} {endpoint:30} -> ERROR: {str(e)[:30]}")

print("\n" + "="*70)
print("RECOMMENDATION")
print("="*70)
print("""
Based on the 405 error, the endpoint exists but doesn't accept POST.
This usually means:
1. The route is GET only
2. The endpoint name is different
3. Need to check api.py for actual route definitions

Next step: Check ~/projects/apex/api.py for route definitions
""")
