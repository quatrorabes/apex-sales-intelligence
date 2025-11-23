#!/usr/bin/env python3

# test_hubspot.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('pat-na2-f9d23c17-86f8-4a63-83f7-9742a77c5645')
print(f"Token found: {bool(token)}")

if token:
	headers = {'Authorization': f'Bearer {token}'}
	response = requests.get('https://api.hubapi.com/crm/v3/objects/contacts?limit=1', headers=headers)
	print(f"Status: {response.status_code}")
	if response.status_code == 200:
		print("✅ HubSpot connection works!")
	else:
		print(f"❌ Error: {response.text}")
else:
	print("❌ No token found in environment variables")