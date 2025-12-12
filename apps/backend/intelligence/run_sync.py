import sys
sys.path.insert(0, '..')
from intelligence.hubspot_sync import HubSpotSync

# Point to the correct database location (one level up)
sync = HubSpotSync(db_path="../apex.db")
print("🔄 Starting HubSpot contact import...")
result = sync.import_contacts_from_hubspot()

# Result is a list, not a dict
if isinstance(result, list):
    print(f"✅ Imported {len(result)} contacts")
else:
    print(f"✅ Imported {result.get('total', 0)} contacts")
    print(f"📊 Stats: {result}")
