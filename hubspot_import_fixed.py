"""
Fixed HubSpot import endpoint with defensive parsing and logging.
Replace lines 1015-1150 in api.py with this.
"""

import requests
import sqlite3
import logging

logger = logging.getLogger(__name__)

@app.route("/api/hubspot/import", methods=["POST"])
def hubspot_import():
    """
    Paginated HubSpot import with quality filters.
    - Excludes: unqualified, do not contact, unsubscribed
    - Captures: phone, mobile, LinkedIn
    - Upserts to Apex database
    
    Returns: { success, imported, updated, skipped, filtered }
    """
    hubspot_api_key = os.getenv("HUBSPOT_API_KEY")
    if not hubspot_api_key:
        return {"success": False, "error": "HUBSPOT_API_KEY not set"}, 401
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        imported = 0
        updated = 0
        skipped = 0
        filtered_out = 0
        
        after = None
        headers = {"Authorization": f"Bearer {hubspot_api_key}"}
        
        logger.info("🔄 Starting HubSpot import with filters...")
        
        batch_num = 0
        while True:
            batch_num += 1
            url = "https://api.hubapi.com/crm/v3/objects/contacts"
            params = {
                "limit": 100,
                "properties": [
                    "firstname",
                    "lastname", 
                    "email",
                    "phone",
                    "mobilephone",
                    "company",
                    "jobtitle",
                    "lifecyclestage",
                    "hs_lead_status",
                    "do_not_contact",
                    "hs_email_open",
                    "linkedin_url"
                ]
            }
            if after:
                params["after"] = after
            
            logger.info(f"📦 Batch {batch_num}: Fetching from HubSpot...")
            
            # Fetch batch from HubSpot
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Debug: log the response structure
            logger.info(f"   Response type: {type(data)}")
            logger.info(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'NOT A DICT'}")
            
            if not data.get("results"):
                logger.info("✅ No more contacts to fetch")
                break
            
            results = data.get("results", [])
            logger.info(f"   Processing {len(results)} contacts...")
            
            # Process each contact
            for idx, hs_contact in enumerate(results):
                try:
                    # Defensive: ensure hs_contact is a dict
                    if not isinstance(hs_contact, dict):
                        logger.warning(f"   ⚠️  Contact {idx} is not a dict: {type(hs_contact)}")
                        skipped += 1
                        continue
                    
                    props = hs_contact.get("properties", {})
                    
                    # Defensive: ensure props is a dict
                    if not isinstance(props, dict):
                        logger.warning(f"   ⚠️  Properties for contact {idx} is not a dict: {type(props)}")
                        skipped += 1
                        continue
                    
                    email = props.get("email", {})
                    if isinstance(email, dict):
                        email = email.get("value", "").strip()
                    else:
                        email = str(email).strip() if email else ""
                    
                    # FILTER 1: No email = skip
                    if not email:
                        skipped += 1
                        continue
                    
                    # FILTER 2: Lifecycle stage (UNQUALIFIED FILTER)
                    lifecycle_obj = props.get("lifecyclestage", {})
                    lifecycle = lifecycle_obj.get("value", "").lower() if isinstance(lifecycle_obj, dict) else str(lifecycle_obj).lower()
                    if lifecycle in ["subscriber", "other", "unqualified", ""]:
                        filtered_out += 1
                        logger.debug(f"   ⏭️  Filtered (lifecycle={lifecycle}): {email}")
                        continue
                    
                    # FILTER 3: Do not contact flag
                    do_not_contact_obj = props.get("do_not_contact", {})
                    do_not_contact = do_not_contact_obj.get("value", "").lower() if isinstance(do_not_contact_obj, dict) else str(do_not_contact_obj).lower()
                    if do_not_contact in ["yes", "true"]:
                        filtered_out += 1
                        logger.debug(f"   ⏭️  Filtered (do_not_contact): {email}")
                        continue
                    
                    # FILTER 4: Lead status "Unsubscribed"
                    lead_status_obj = props.get("hs_lead_status", {})
                    lead_status = lead_status_obj.get("value", "").lower() if isinstance(lead_status_obj, dict) else str(lead_status_obj).lower()
                    if "unsubscribed" in lead_status:
                        filtered_out += 1
                        logger.debug(f"   ⏭️  Filtered (unsubscribed): {email}")
                        continue
                    
                    # Extract fields (defensive parsing)
                    first_obj = props.get("firstname", {})
                    first_name = first_obj.get("value", "").strip() if isinstance(first_obj, dict) else str(first_obj).strip()
                    
                    last_obj = props.get("lastname", {})
                    last_name = last_obj.get("value", "").strip() if isinstance(last_obj, dict) else str(last_obj).strip()
                    
                    name = f"{first_name} {last_name}".strip() or email.split("@")[0]
                    
                    phone_obj = props.get("phone", {})
                    phone = phone_obj.get("value", "").strip() if isinstance(phone_obj, dict) else str(phone_obj).strip()
                    
                    mobile_obj = props.get("mobilephone", {})
                    mobile = mobile_obj.get("value", "").strip() if isinstance(mobile_obj, dict) else str(mobile_obj).strip()
                    
                    company_obj = props.get("company", {})
                    company = company_obj.get("value", "").strip() if isinstance(company_obj, dict) else str(company_obj).strip()
                    
                    title_obj = props.get("jobtitle", {})
                    title = title_obj.get("value", "").strip() if isinstance(title_obj, dict) else str(title_obj).strip()
                    
                    linkedin_obj = props.get("linkedin_url", {})
                    linkedin_url = linkedin_obj.get("value", "").strip() if isinstance(linkedin_obj, dict) else str(linkedin_obj).strip()
                    
                    hs_contact_id = hs_contact.get("id", "")
                    
                    # UPSERT into Apex database
                    cursor.execute("""
                        INSERT INTO contacts 
                        (name, email, phone, phone_mobile, company, title, 
                         linkedin_url, hs_contact_id, data_source, sync_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'hubspot', datetime('now'))
                        ON CONFLICT(email) DO UPDATE SET
                            name = CASE WHEN excluded.name != '' THEN excluded.name ELSE name END,
                            phone = COALESCE(excluded.phone, phone),
                            phone_mobile = COALESCE(excluded.phone_mobile, phone_mobile),
                            company = COALESCE(excluded.company, company),
                            title = COALESCE(excluded.title, title),
                            linkedin_url = COALESCE(excluded.linkedin_url, linkedin_url),
                            hs_contact_id = excluded.hs_contact_id,
                            sync_date = datetime('now')
                    """, (name, email, phone, mobile, company, title, linkedin_url, hs_contact_id))
                    
                    if cursor.rowcount > 0:
                        updated += 1
                    else:
                        imported += 1
                    
                except Exception as e:
                    logger.error(f"   ❌ Error processing contact {idx}: {e}")
                    skipped += 1
                    continue
            
            conn.commit()
            
            # Pagination
            paging = data.get("paging", {})
            after = paging.get("next", {}).get("after")
            if not after:
                logger.info("✅ Pagination complete")
                break
        
        conn.close()
        
        # Log results
        total = imported + updated + skipped + filtered_out
        logger.info(f"""
        ✅ IMPORT COMPLETE
        Total HubSpot contacts: {total}
        ✅ Imported (new): {imported}
        ♻️  Updated (existing): {updated}
        ⏭️  Filtered out: {filtered_out}
        ⚠️  Skipped (errors): {skipped}
        """)
        
        return {
            "success": True,
            "message": f"Import complete: {imported} new, {updated} updated, {filtered_out} filtered, {skipped} skipped",
            "imported": imported,
            "updated": updated,
            "filtered": filtered_out,
            "skipped": skipped,
            "total": total,
            "qualified_count": imported + updated
        }, 200
        
    except requests.RequestException as e:
        logger.error(f"❌ HubSpot API error: {e}")
        return {"success": False, "error": str(e)}, 500
    except Exception as e:
        logger.error(f"❌ Import failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}, 500
