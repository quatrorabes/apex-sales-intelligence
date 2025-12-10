# This is the FIXED enrichment endpoint for main.py
# Replace your existing @app.post("/api/contacts/{contact_id}/enrich") with this:

@app.post("/api/contacts/{contact_id}/enrich", tags=["Enrichment"])
async def enrich_contact(contact_id: int):
    """
    Deep enrichment with 3-stage Perplexity search
    Returns structured, frontend-friendly response
    """
    if not enrichment_engine:
        raise HTTPException(503, detail="Enrichment engine not available")
    
    try:
        # Get contact data
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(404, detail="Contact not found")
            
            # Mark as enriching
            cursor.execute("UPDATE contacts SET enrichment_status = 'enriching' WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()
        
        contact_dict = dict(contact)
        
        logger.info(f"🚀 Starting enrichment for {contact_dict.get('name')} (ID: {contact_id})")
        
        # Call enrichment engine
        enrichment_result = enrichment_engine.enrich_contact(contact_dict)
        
        # Extract and structure the profile data
        profile_text = enrichment_result.get('profile_text', '')
        
        # Parse profile into structured sections (if it follows markdown format)
        sections = {
            "overview": "",
            "background": "",
            "company_info": "",
            "sales_opportunities": ""
        }
        
        # Simple section extraction (looks for ## headers)
        current_section = "overview"
        for line in profile_text.split('\n'):
            if line.startswith('## '):
                section_name = line.replace('##', '').strip().lower()
                if 'overview' in section_name:
                    current_section = 'overview'
                elif 'background' in section_name or 'experience' in section_name:
                    current_section = 'background'
                elif 'company' in section_name or 'organization' in section_name:
                    current_section = 'company_info'
                elif 'sales' in section_name or 'opportunity' in section_name:
                    current_section = 'sales_opportunities'
            else:
                sections[current_section] += line + '\n'
        
        # Prepare clean enrichment data for database
        enrichment_json = json.dumps({
            'profile_text': profile_text,
            'sections': sections,
            'character_count': len(profile_text),
            'enriched_at': datetime.now().isoformat(),
            'success': True
        })
        
        # Save to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts SET
                    enrichment_status = 'completed',
                    enriched_at = NOW(),
                    enrichment_data = %s,
                    enriched = 1,
                    match_score = COALESCE(match_score, 0) + 20
                WHERE id = %s
            """, (enrichment_json, contact_id))
            conn.commit()
            cursor.close()
        
        logger.info(f"✅ Enrichment completed for contact {contact_id} ({len(profile_text)} chars)")
        
        # Return CLEAN, structured response for frontend
        return {
            "success": True,
            "contact_id": contact_id,
            "enrichment": {
                "status": "completed",
                "profile_length": len(profile_text),
                "sections": {
                    "overview": sections["overview"][:500] + "..." if len(sections["overview"]) > 500 else sections["overview"],
                    "background": sections["background"][:500] + "..." if len(sections["background"]) > 500 else sections["background"],
                    "company_info": sections["company_info"][:500] + "..." if len(sections["company_info"]) > 500 else sections["company_info"],
                    "sales_opportunities": sections["sales_opportunities"][:500] + "..." if len(sections["sales_opportunities"]) > 500 else sections["sales_opportunities"]
                },
                "full_profile_available": True
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrichment error for contact {contact_id}: {e}")
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s", (contact_id,))
                conn.commit()
                cursor.close()
        except:
            pass
        raise HTTPException(500, detail=str(e))
