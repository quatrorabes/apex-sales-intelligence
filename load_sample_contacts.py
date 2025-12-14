#!/usr/bin/env python3
import requests
import sys

API_URL = "https://apex-backend-i7b0.onrender.com"

SAMPLE_CONTACTS = [
    {
        "name": "Sarah Johnson",
        "email": "sarah.johnson@techcorp.com",
        "company": "TechCorp Industries",
        "title": "VP of Sales",
        "phone": "+1-555-0101",
        "vertical": "SaaS"
    },
    {
        "name": "Michael Chen",
        "email": "m.chen@innovate.io",
        "company": "Innovate Solutions",
        "title": "Chief Technology Officer",
        "phone": "+1-555-0102",
        "vertical": "SaaS"
    },
    {
        "name": "Emily Rodriguez",
        "email": "emily.r@cloudnine.com",
        "company": "CloudNine Systems",
        "title": "Director of Engineering",
        "phone": "+1-555-0103",
        "linkedin_url": "https://linkedin.com/in/emilyrodriguez",
        "vertical": "SaaS"
    },
    {
        "name": "David Park",
        "email": "dpark@enterprise.com",
        "company": "Enterprise Solutions Group",
        "title": "Senior Product Manager",
        "phone": "+1-555-0104",
        "vertical": "SaaS"
    },
    {
        "name": "Jennifer Williams",
        "email": "jwilliams@insureco.com",
        "company": "InsureCo Financial",
        "title": "Agency Owner",
        "phone": "+1-555-0105",
        "vertical": "Insurance"
    },
]

def load_contacts():
    print(f"Loading {len(SAMPLE_CONTACTS)} sample contacts...\n")
    
    loaded = 0
    failed = 0
    
    for i, contact in enumerate(SAMPLE_CONTACTS, 1):
        try:
            print(f"[{i}/{len(SAMPLE_CONTACTS)}] {contact['name']}...", end=" ")
            
            response = requests.post(
                f"{API_URL}/api/contacts",
                json=contact,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Created (ID: {result.get('contact_id')})")
                loaded += 1
            else:
                print(f"❌ Failed ({response.status_code})")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Summary: ✅ {loaded} loaded, ❌ {failed} failed")
    print(f"{'='*50}\n")
    
    return loaded > 0

if __name__ == "__main__":
    success = load_contacts()
    sys.exit(0 if success else 1)
