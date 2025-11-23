async def run_perplexity_enrichment(contact_id: int, contact: Dict):
    '''Background task - Enhanced Perplexity deep enrichment with comprehensive prompt'''
    try:
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            print(f"❌ PERPLEXITY_API_KEY not set")
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contacts SET enrichment_status = 'failed' WHERE id = ?",
                    (contact_id,)
                )
                conn.commit()
            return

        # Build contact details
        name = f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        company = contact.get('company', '')
        title = contact.get('job_title', '') or contact.get('title', '')
        linkedin = contact.get('linkedin_url', '') or contact.get('linkedin', '')

        print(f"🔍 Deep enriching: {name} @ {company}...")

        # YOUR COMPREHENSIVE MAGIC PROMPT - Full version from perplexity_deep_enrichment.py
        prompt = f'''You are a professional profile-building assistant. Generate up-to-date profile using both public web sources for {name} at {company}. Use sources such as LinkedIn ({linkedin}) & Internet.

For a company ({company}), structure the profile as:

1. Overview – Description, mission, founding details, and HQ
2. Products & Services – Key offerings and markets served
3. Leadership – Key executives and founders
4. Market & Competitors – Industry, position, key competitors
5. Recent News – Major announcements, deals, or product launches

For a person ({name}), structure the profile as:

1. Overview – Current title and organization
2. Background – Work history, notable achievements
3. Education – Degrees and institutions
4. Recent Mentions – Any news, public appearances, LinkedIn posts, or online presence
5. Find instagram, facebook, and twitter user profiles.
6. Personality Detail - perform a Myers briggs assessment.
7. Compose and interpret Myers-Briggs Personality assessment summary.
8. Evaluate potential talking points regarding sales opportunities.
9. Search deals database for any past or current "deal"
10. Update all fields with new or inaccurate information
11. Find any relevant company news or fun facts. Populate results in "talking points" tab and on relevant company page.
12. Trigger Events - Identify any recent events that create sales opportunities (new funding, expansion, leadership changes)
13. Competitive Intelligence - What solutions are they currently using that we could replace?
14. Warm Introduction Paths - Find mutual connections or shared affiliations
15. Engagement Preferences - Best time to reach, preferred communication channels
16. Decision Making Style - How they evaluate vendors and make purchasing decisions
17. Budget Authority - Signs of budget availability or fiscal year timing
18. Success Metrics - What KPIs they care about based on their role

Additionally, provide:

- AI Score Reasoning: Why this is a high-value contact (100+ words)
- Relationship Tips: Based on their personality type
- Pain Points: Specific to their role and industry
- Outreach Approach: Multi-paragraph personalized approach

Format the response as JSON with these exact keys:
{
    "overview": "Professional overview",
    "background": "Work history and achievements",
    "education": "Educational background",
    "recent_mentions": "Recent news and mentions",
    "social_profiles": {"instagram": "", "facebook": "", "twitter": ""},
    "myers_briggs": "MBTI type (e.g., ENTJ)",
    "personality_assessment": "Detailed MBTI interpretation",
    "talking_points": ["Point 1", "Point 2", "Point 3"],
    "trigger_events": ["Event 1", "Event 2"],
    "competitive_intelligence": "Current solutions they use",
    "warm_intro_paths": ["Path 1", "Path 2"],
    "engagement_preferences": "Best times and channels",
    "decision_style": "How they evaluate vendors",
    "budget_signals": "Budget availability indicators",
    "success_metrics": "KPIs they care about",
    "ai_score_reasoning": "Why this is a high-value contact",
    "relationship_tips": "How to build rapport",
    "pain_points": ["Pain 1", "Pain 2", "Pain 3"],
    "outreach_approach": "Personalized outreach strategy",
    "company_overview": "Company description and mission",
    "products_services": "Key offerings",
    "leadership": "Key executives",
    "market_position": "Industry position and competitors",
    "recent_company_news": "Company announcements"
}'''

        # Call Perplexity API with proper structure
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a professional profile-building assistant. Generate comprehensive, actionable intelligence. Return valid JSON only, no markdown formatting."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 4000  # Increased for comprehensive response
            },
            timeout=60  # Increased timeout for longer response
        )

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']

            # Clean up response - remove markdown formatting if present
            content = content.replace("```json", "").replace("```", "").strip()
            if content.startswith("'{") or content.startswith('"{'):
                content = content[1:-1]  # Remove outer quotes if wrapped

            try:
                # Parse the JSON response
                enrichment_data = json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured data from text
                print(f"⚠️ JSON parsing failed, extracting data from text...")
                enrichment_data = {
                    "overview": content[:500],
                    "raw_response": content,
                    "parse_error": True
                }

            # Extract key fields for direct database columns
            pain_points = enrichment_data.get('pain_points', [])
            if isinstance(pain_points, list):
                pain_points_str = json.dumps(pain_points)
            else:
                pain_points_str = str(pain_points)

            talking_points = enrichment_data.get('talking_points', [])
            if isinstance(talking_points, list):
                talking_points_str = json.dumps(talking_points)
            else:
                talking_points_str = str(talking_points)

            myers_briggs = enrichment_data.get('myers_briggs', '')

            # Store in database with all enrichment data
            with get_db() as conn:
                cursor = conn.cursor()

                # First, get existing enrichment_data if any
                cursor.execute("SELECT enrichment_data FROM contacts WHERE id = ?", (contact_id,))
                row = cursor.fetchone()
                existing_data = {}
                if row and row[0]:
                    try:
                        existing_data = json.loads(row[0])
                    except:
                        existing_data = {}

                # Merge with new data
                merged_data = {**existing_data, **enrichment_data}

                # Update contact with comprehensive enrichment
                cursor.execute('''
                    UPDATE contacts SET 
                        enrichment_data = ?,
                        pain_points = ?,
                        talking_points = ?,
                        myers_briggs = ?,
                        enrichment_status = 'complete',
                        enriched_at = ?
                    WHERE id = ?
                ''', (
                    json.dumps(merged_data),  # Store complete enrichment data
                    pain_points_str,
                    talking_points_str,
                    myers_briggs,
                    datetime.now().isoformat(),
                    contact_id
                ))
                conn.commit()

            print(f"✅ Deep enrichment complete: {name}")
            print(f"   Found {len(pain_points)} pain points")
            print(f"   Found {len(talking_points)} talking points")
            print(f"   MBTI: {myers_briggs}")

        else:
            # Enhanced error logging
            error_detail = response.text if response.text else f"Status {response.status_code}"
            print(f"❌ Perplexity API error: {response.status_code}")
            print(f"   Response: {error_detail[:500]}")  # First 500 chars of error

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contacts SET enrichment_status = 'failed' WHERE id = ?",
                    (contact_id,)
                )
                conn.commit()

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse Perplexity response: {e}")
        print(f"   Response snippet: {content[:200] if 'content' in locals() else 'No content'}")
        # Store raw response even if JSON parsing fails
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contacts SET enrichment_status = 'partial', enrichment_data = ? WHERE id = ?",
                (json.dumps({"raw_response": content if 'content' in locals() else "", "error": str(e)}), contact_id)
            )
            conn.commit()

    except Exception as e:
        print(f"❌ Deep enrichment failed: {e}")
        import traceback
        traceback.print_exc()

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contacts SET enrichment_status = 'failed' WHERE id = ?",
                (contact_id,)
            )
            conn.commit()