#!/usr/bin/env python3

# File: test_generation.py
import requests
import json
import time

# Test contact ID
contact_id = 35

# Step 1: Trigger enrichment
print(f"Starting enrichment for contact {contact_id}...")
response = requests.post(f"http://localhost:8000/api/contacts/{contact_id}/deep-enrich")
print(f"Enrichment response: {response.status_code}")

# Step 2: Wait for processing
print("Waiting for processing...")
time.sleep(5)

# Step 3: Check dashboard data
print(f"Fetching dashboard data for contact {contact_id}...")
response = requests.get(f"http://localhost:8000/api/dashboard/{contact_id}")
if response.ok:
	data = response.json()
	if "generated_scripts" in data:
		print("✅ Scripts found in dashboard!")
		print(json.dumps(data["generated_scripts"], indent=2))
	else:
		print("❌ No scripts in dashboard data")
		print("Attempting manual generation...")
		
		# Step 4: Try manual generation
		response = requests.post(f"http://localhost:8000/api/refresh-scripts/{contact_id}")
		print(f"Manual generation response: {response.status_code}")
		
		# Step 5: Re-check dashboard
		time.sleep(2)
		response = requests.get(f"http://localhost:8000/api/dashboard/{contact_id}")
		if response.ok:
			data = response.json()
			if "generated_scripts" in data:
				print("✅ Scripts generated after manual trigger!")
				print(json.dumps(data["generated_scripts"], indent=2))
			else:
				print("❌ Still no scripts - check logs for errors")
				