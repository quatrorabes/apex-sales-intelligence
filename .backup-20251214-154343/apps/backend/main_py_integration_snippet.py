
# ============================================================================
# APEX INTELLIGENCE INTEGRATION - Add to main.py
# ============================================================================

from intelligence.engines.enrichment.apex_intelligence_engine import ApexScoringEngine
from intelligence.engines.enrichment.persona_classifier_cre_sba import UltimatePersonaClassifier
from intelligence.sync.hubspot_sync import HubSpotSync

# Initialize intelligence engines
scoring_engine = ApexScoringEngine(db_path=DATABASE_PATH)
persona_classifier = UltimatePersonaClassifier()
hubspot_sync = HubSpotSync(db_path=DATABASE_PATH)

# ============================================================================
# NEW ENDPOINTS
# ============================================================================

@app.post("/api/import/hubspot")
async def import_from_hubspot(limit: int = 100):
    """Import contacts from HubSpot, score, and classify"""
    try:
        # Import from HubSpot
        contacts = hubspot_sync.import_contacts_from_hubspot(limit)

        # Score and classify each contact
        scored_count = 0
        classified_count = 0

        for contact in contacts:
            contact_id = contact.get("local_id")  # From DB insert

            if contact_id:
                # Score
                try:
                    scores = scoring_engine.score_contact(contact_id)
                    scored_count += 1
                except Exception as e:
                    print(f"Error scoring {contact_id}: {e}")

                # Classify persona
                try:
                    tier, persona_type, confidence, criteria = persona_classifier.classify_contact({
                        'job_title': contact.get('jobtitle'),
                        'company': contact.get('company'),
                        'industry': contact.get('industry'),
                        'skills': contact.get('skills', [])
                    })

                    # Save persona
                    cursor.execute("""
                        UPDATE contacts SET
                            persona_tier = ?,
                            persona_type = ?,
                            persona_confidence = ?
                        WHERE id = ?
                    """, (tier, persona_type, confidence, contact_id))
                    db.commit()

                    classified_count += 1

                except Exception as e:
                    print(f"Error classifying {contact_id}: {e}")

        return {
            "success": True,
            "imported_count": len(contacts),
            "scored_count": scored_count,
            "classified_count": classified_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/score-all")
async def score_all_contacts():
    """Bulk score all contacts"""
    try:
        cursor.execute("SELECT id FROM contacts WHERE enrichment_status = 'complete'")
        contacts = cursor.fetchall()

        scored_count = 0
        total_mdcp = 0
        total_rss = 0

        for contact in contacts:
            contact_id = contact[0]
            try:
                scores = scoring_engine.score_contact(contact_id)
                scored_count += 1
                total_mdcp += scores['mdcp_score']
                total_rss += scores['rss_score']
            except Exception as e:
                print(f"Error scoring {contact_id}: {e}")

        return {
            "success": True,
            "scored_count": scored_count,
            "average_mdcp": round(total_mdcp / scored_count, 2) if scored_count > 0 else 0,
            "average_rss": round(total_rss / scored_count, 2) if scored_count > 0 else 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/personas")
async def get_persona_distribution():
    """Get persona tier and type distribution"""
    try:
        cursor.execute("""
            SELECT 
                persona_tier,
                persona_type,
                COUNT(*) as count,
                AVG(persona_confidence) as avg_confidence,
                AVG(priority_score) as avg_priority
            FROM contacts
            WHERE persona_tier IS NOT NULL
            GROUP BY persona_tier, persona_type
            ORDER BY count DESC
        """)

        results = cursor.fetchall()

        tier1_count = 0
        tier2_count = 0
        breakdown = []

        for row in results:
            tier, persona_type, count, avg_conf, avg_priority = row

            if 'Tier 1' in tier:
                tier1_count += count
            elif 'Tier 2' in tier:
                tier2_count += count

            breakdown.append({
                'tier': tier,
                'persona_type': persona_type,
                'count': count,
                'avg_confidence': round(avg_conf, 2) if avg_conf else 0,
                'avg_priority': round(avg_priority, 2) if avg_priority else 0
            })

        return {
            "tier1_count": tier1_count,
            "tier2_count": tier2_count,
            "breakdown": breakdown
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/sync-hubspot")
async def sync_contact_to_hubspot(contact_id: int):
    """Sync contact scores and persona to HubSpot"""
    try:
        # Get contact data
        cursor.execute("""
            SELECT 
                mdcp_score, mdcp_tier, rss_score, rss_tier,
                priority_score, urgency_level, persona_tier,
                persona_type, persona_confidence
            FROM contacts WHERE id = ?
        """, (contact_id,))

        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Contact not found")

        scores = {
            'mdcp_score': result[0],
            'mdcp_tier': result[1],
            'rss_score': result[2],
            'rss_tier': result[3],
            'priority_score': result[4],
            'urgency_level': result[5],
            'persona_tier': result[6],
            'persona_type': result[7],
            'persona_confidence': result[8]
        }

        # Sync to HubSpot
        success = hubspot_sync.sync_scores_to_hubspot(contact_id, scores)

        return {
            "success": success,
            "synced_properties": list(scores.keys())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hubspot/setup-properties")
async def setup_hubspot_properties():
    """Create APEX custom properties in HubSpot (one-time setup)"""
    try:
        created_count = hubspot_sync.create_hubspot_custom_properties()

        return {
            "success": True,
            "created_count": created_count,
            "message": "HubSpot custom properties created/verified"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# UPDATED ENRICHMENT ENDPOINT - Now includes scoring and persona
# ============================================================================

@app.post("/api/contacts/{contact_id}/deep-enrich")
async def enrich_contact_with_scoring(contact_id: int):
    """
    Complete enrichment workflow:
    1. Web search enrichment
    2. Score contact (MDCP + RSS)
    3. Classify persona
    4. Sync to HubSpot
    """
    try:
        # Step 1: Existing enrichment
        # ... (keep existing enrichment code) ...

        # Step 2: Score contact
        try:
            scores = scoring_engine.score_contact(contact_id, save_to_db=True)
            print(f"✅ Scored contact {contact_id}: MDCP={scores['mdcp_score']}, RSS={scores['rss_score']}")
        except Exception as e:
            print(f"⚠️ Error scoring contact {contact_id}: {e}")
            scores = {}

        # Step 3: Classify persona
        try:
            # Get contact data for classification
            cursor.execute("""
                SELECT title, company, industry FROM contacts WHERE id = ?
            """, (contact_id,))

            contact_data = cursor.fetchone()

            if contact_data:
                tier, persona_type, confidence, criteria = persona_classifier.classify_contact({
                    'job_title': contact_data[0],
                    'company': contact_data[1],
                    'industry': contact_data[2]
                })

                # Save persona
                cursor.execute("""
                    UPDATE contacts SET
                        persona_tier = ?,
                        persona_type = ?,
                        persona_confidence = ?
                    WHERE id = ?
                """, (tier, persona_type, confidence, contact_id))
                db.commit()

                print(f"✅ Classified contact {contact_id}: {tier} - {persona_type} ({confidence}% confidence)")

        except Exception as e:
            print(f"⚠️ Error classifying persona: {e}")

        # Step 4: Sync to HubSpot (if enabled)
        try:
            if scores:
                hubspot_sync.sync_scores_to_hubspot(contact_id, scores)
                print(f"✅ Synced to HubSpot")
        except Exception as e:
            print(f"⚠️ HubSpot sync failed: {e}")

        return {"success": True, "contact_id": contact_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

