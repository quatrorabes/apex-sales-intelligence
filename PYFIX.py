python3 << 'PYFIX'
import re

with open('/Users/chrisrabenold/projects/apex/api.py', 'r') as f:
    content = f.read()

# Find and remove broken HubSpot endpoint(s)
pattern = r'\n# =+\n# HUBSPOT IMPORT ENDPOINT.*?return jsonify\(\{[^}]+\}\), 500\n'
content = re.sub(pattern, '\n', content, flags=re.DOTALL)

# Find insertion point
insert_point = content.find("if __name__ == '__main__':")

hubspot_endpoint = '''
# ================================================================
# HUBSPOT IMPORT ENDPOINT (WITH PAGINATION)
# ================================================================
@app.route("/api/hubspot/import", methods=["POST", "OPTIONS"])
def hubspot_import():
    """Import ALL contacts from HubSpot CRM with pagination"""
    import requests as req
    
    if request.method == "OPTIONS":
        return "", 204
    
    HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
    if not HUBSPOT_API_KEY:
        return jsonify({"success": False, "error": "HUBSPOT_API_KEY not configured"}), 400
    
    try:
        headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
        all_contacts = []
        after = None
        page = 0
        
        while True:
            page += 1
            params = {"limit": 100, "properties": "firstname,lastname,email,phone,company,jobtitle,linkedinbio"}
            if after:
                params["after"] = after
            
            print(f"Fetching HubSpot page {page}...")
            response = req.get("https://api.hubapi.com/crm/v3/objects/contacts", headers=headers, params=params)
            
            if response.status_code != 200:
                return jsonify({"success": False, "error": f"HubSpot API error: {response.status_code}"}), 400
            
            data = response.json()
            results = data.get("results", [])
            all_contacts.extend(results)
            
            paging = data.get("paging", {})
            next_page = paging.get("next", {})
            after = next_page.get("after")
            
            if not after:
                break
        
        print(f"Total HubSpot contacts fetched: {len(all_contacts)}")
        
        imported, updated, skipped = 0, 0, 0
        conn = get_db()
        cursor = conn.cursor()
        
        for hs_contact in all_contacts:
            props = hs_contact.get("properties", {})
            email = (props.get("email") or "").strip()
            if not email:
                skipped += 1
                continue
            
            first = props.get("firstname") or ""
            last = props.get("lastname") or ""
            name = f"{first} {last}".strip() or email.split("@")[0]
            
            cursor.execute("SELECT id FROM contacts WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute(
                    "UPDATE contacts SET name=?, title=?, company=?, phone=?, hubspot_id=?, updated_at=CURRENT_TIMESTAMP WHERE email=?",
                    (name, props.get("jobtitle") or "", props.get("company") or "", props.get("phone") or "", hs_contact.get("id"), email)
                )
                updated += 1
            else:
                cursor.execute(
                    "INSERT INTO contacts (name, email, title, company, phone, hubspot_id, created_at) VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                    (name, email, props.get("jobtitle") or "", props.get("company") or "", props.get("phone") or "", hs_contact.get("id"))
                )
                imported += 1
        
        conn.commit()
        conn.close()
        
        print(f"Import complete: {imported} new, {updated} updated, {skipped} skipped")
        return jsonify({"success": True, "imported": imported, "updated": updated, "skipped": skipped, "total": len(all_contacts)})
    
    except Exception as e:
        print(f"HubSpot import error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


'''

content = content[:insert_point] + hubspot_endpoint + content[insert_point:]

with open('/Users/chrisrabenold/projects/apex/api.py', 'w') as f:
    f.write(content)

print("Done - HubSpot endpoint rewritten")
PYFIX
