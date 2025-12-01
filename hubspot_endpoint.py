# ================================================================
# HUBSPOT IMPORT ENDPOINT (WITH PAGINATION + FILTERS)
# ================================================================
@app.route("/api/hubspot/import", methods=["POST", "OPTIONS"])
def hubspot_import():
    """Import qualified contacts from HubSpot CRM with pagination"""
    import requests as req
    
    if request.method == "OPTIONS":
        return "", 204
    
    HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
    if not HUBSPOT_API_KEY:
        return jsonify({"success": False, "error": "HUBSPOT_API_KEY not configured"}), 400
    
    # Lead statuses to EXCLUDE
    EXCLUDED_LEAD_STATUS = {'unqualified', 'do not contact', 'unsubscribed', 'bad timing', 'dq'}
    EXCLUDED_LIFECYCLE = {'unqualified'}
    
    try:
        headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
        all_contacts = []
        after = None
        page = 0
        
        while True:
            page += 1
            params = {
                "limit": 100, 
                "properties": "firstname,lastname,email,phone,mobilephone,company,jobtitle,hs_linkedinbio,linkedin,hs_lead_status,lifecyclestage"
            }
            if after:
                params["after"] = after
            
            print(f"📥 Fetching HubSpot page {page}...")
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
        
        print(f"📊 Total HubSpot contacts fetched: {len(all_contacts)}")
        
        imported, updated, skipped, filtered = 0, 0, 0, 0
        conn = get_db()
        cursor = conn.cursor()
        
        for hs_contact in all_contacts:
            props = hs_contact.get("properties", {})
            
            # FILTER: Must have email
            email = (props.get("email") or "").strip().lower()
            if not email:
                skipped += 1
                continue
            
            # FILTER: Must have company
            company = (props.get("company") or "").strip()
            if not company:
                filtered += 1
                continue
            
            # FILTER: Exclude bad lead statuses
            lead_status = (props.get("hs_lead_status") or "").strip().lower()
            if lead_status in EXCLUDED_LEAD_STATUS:
                filtered += 1
                continue
            
            # FILTER: Exclude unqualified lifecycle
            lifecycle = (props.get("lifecyclestage") or "").strip().lower()
            if lifecycle in EXCLUDED_LIFECYCLE:
                filtered += 1
                continue
            
            first = props.get("firstname") or ""
            last = props.get("lastname") or ""
            name = f"{first} {last}".strip() or email.split("@")[0]
            
            cursor.execute("SELECT id FROM contacts WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute(
                    "UPDATE contacts SET name=?, title=?, company=?, phone=?, phone_mobile=?, linkedin_url=?, hubspot_id=?, updated_at=CURRENT_TIMESTAMP WHERE email=?",
                    (name, props.get("jobtitle") or "", company, props.get("phone") or "", props.get("mobilephone") or "", props.get("hs_linkedinbio") or props.get("linkedin") or "", hs_contact.get("id"), email)
                )
                updated += 1
            else:
                cursor.execute(
                    "INSERT INTO contacts (name, email, title, company, phone, phone_mobile, linkedin_url, hubspot_id, created_at) VALUES (?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                    (name, email, props.get("jobtitle") or "", company, props.get("phone") or "", props.get("mobilephone") or "", props.get("hs_linkedinbio") or props.get("linkedin") or "", hs_contact.get("id"))
                )
                imported += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Import complete: {imported} new, {updated} updated, {skipped} no email, {filtered} filtered out")
        return jsonify({
            "success": True, 
            "imported": imported, 
            "updated": updated, 
            "skipped": skipped,
            "filtered": filtered,
            "total": len(all_contacts)
        })
    
    except Exception as e:
        print(f"❌ HubSpot import error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
