#!/usr/bin/env python3
"""Test HubSpot Import - Debug what data we're getting"""

import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()

# HubSpot API endpoint
hubspot_url = 'https://api.hubapi.com/crm/v3/objects/contacts'
headers = {
    'Authorization': f"Bearer {os.getenv('HUBSPOT_ACCESS_TOKEN')}",
    'Content-Type': 'application/json'
}

# Request MORE properties and specific filters
params = {
    'limit': 10,  # Start with 10 for testing
    'properties': ','.join([
        'firstname',
        'lastname', 
        'email',
        'phone',
        'mobilephone',
        'company',
        'jobtitle',
        'hs_object_id',
        'createdate',
        'lastmodifieddate',
        'lifecyclestage',
        'hs_lead_status',
        'website',
        'city',
        'state',
        'country',
        'linkedin_url',
        'linkedinbio',
        'industry'
    ]),
    'archived': False
}

print("🔍 Fetching contacts from HubSpot...\n")
response = requests.get(hubspot_url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    contacts = data.get('results', [])
    
    print(f"✅ Retrieved {len(contacts)} contacts\n")
    print("="*80)
    
    for i, contact in enumerate(contacts, 1):
        props = contact.get('properties', {})
        print(f"\n📇 Contact {i}:")
        print(f"   ID: {contact.get('id')}")
        print(f"   Name: {props.get('firstname', '')} {props.get('lastname', '')}")
        print(f"   Email: {props.get('email', 'N/A')}")
        print(f"   Phone: {props.get('phone') or props.get('mobilephone', 'N/A')}")
        print(f"   Company: {props.get('company', 'N/A')}")
        print(f"   Title: {props.get('jobtitle', 'N/A')}")
        print(f"   Lifecycle: {props.get('lifecyclestage', 'N/A')}")
        print(f"   Lead Status: {props.get('hs_lead_status', 'N/A')}")
        print(f"   LinkedIn: {props.get('linkedin_url') or props.get('linkedinbio', 'N/A')}")
        print(f"   Created: {props.get('createdate', 'N/A')}")
    
    print("\n" + "="*80)
    print(f"\n📊 Total available: {data.get('total', len(contacts))}")
    
    # Show raw data for first contact
    if contacts:
        print("\n🔬 Raw data for first contact:")
        print(json.dumps(contacts[0], indent=2))
        
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
