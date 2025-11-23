# In main.py, replace the run_perplexity_enrichment function with this:

# Add this import at the top of main.py (with other imports)
from perplexity_deep_enrichment_module import enrich_contact

# Then replace the entire run_perplexity_enrichment function with this simplified version:
async def run_perplexity_enrichment(contact_id: int, contact: Dict):
    """Background task that calls the enrichment module"""
    try:
        print(f"🚀 Starting enrichment for contact {contact_id}")

        # Update status to enriching
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contacts SET enrichment_status = 'enriching' WHERE id = ?",
                (contact_id,)
            )
            conn.commit()

        # Call the enrichment module
        result = enrich_contact(contact_id, contact)

        if result["status"] == "success":
            # Store results in database
            with get_db() as conn:
                cursor = conn.cursor()

                enrichment_data = result["enrichment_data"]
                pain_points = result["pain_points"]
                talking_points = result["talking_points"]
                myers_briggs = result["myers_briggs"]

                cursor.execute("""
                    UPDATE contacts SET 
                        enrichment_data = ?,
                        pain_points = ?,
                        talking_points = ?,
                        myers_briggs = ?,
                        enrichment_status = 'complete',
                        enriched_at = ?
                    WHERE id = ?
                """, (
                    json.dumps(enrichment_data),
                    json.dumps(pain_points) if isinstance(pain_points, list) else str(pain_points),
                    json.dumps(talking_points) if isinstance(talking_points, list) else str(talking_points),
                    myers_briggs,
                    datetime.now().isoformat(),
                    contact_id
                ))
                conn.commit()

                # Update name if discovered
                if result.get("person_name") and not contact.get("name"):
                    cursor.execute(
                        "UPDATE contacts SET name = ? WHERE id = ?",
                        (result["person_name"], contact_id)
                    )
                    conn.commit()

        else:
            # Mark as failed
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contacts SET enrichment_status = 'failed' WHERE id = ?",
                    (contact_id,)
                )
                conn.commit()
            print(f"❌ Enrichment failed: {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"❌ Enrichment task error: {e}")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contacts SET enrichment_status = 'failed' WHERE id = ?",
                (contact_id,)
            )
            conn.commit()
