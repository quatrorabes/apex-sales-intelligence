async def run_perplexity_enrichment(contact_id: int, contact: Dict):
    '''Background task - Enhanced Perplexity deep enrichment with better person handling'''
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

        # Build contact details - handle missing names better
        firstname = contact.get('firstname', '').strip()
        lastname = contact.get('lastname', '').strip()

        # Try multiple name fields
        if firstname or lastname:
            name = f"{firstname} {lastname}".strip()
        elif contact.get('name'):
            name = contact.get('name').strip()
            # Try to split into first/last if full name provided
            if ' ' in name:
                parts = name.split(' ', 1)
                firstname = parts[0]
                lastname = parts[1] if len(parts) > 1 else ''
        else:
            name = ""

        company = contact.get('company', '').strip()
        title = contact.get('job_title', '') or contact.get('title', '')
        email = contact.get('email', '')
        linkedin = contact.get('linkedin_url', '') or contact.get('linkedin', '')

        # Log what we're searching for
        print(f"🔍 Deep enriching:")
        print(f"   Name: {name if name else '[No name provided]'}")
        print(f"   Company: {company if company else '[No company]'}")
        print(f"   Title: {title if title else '[No title]'}")
        print(f"   Email: {email if email else '[No email]'}")

        # Build search-focused prompt
        if name and company:
            search_focus = f"{name} who works at {company}"
            if title:
                search_focus += f" as {title}"
        elif name:
            search_focus = f"professional named {name}"
        elif company:
            search_focus = f"contacts at {company}"
            if email:
                search_focus += f" particularly someone with email {email}"
        else:
            search_focus = "available information"

        # Comprehensive prompt emphasizing PERSON data
        prompt = f"""You are a B2B sales intelligence researcher. Your PRIMARY GOAL is to find detailed information about the PERSON, not just the company.

SEARCH TARGET: {search_focus}

Known Information:
- Name: {name if name else 'FIND THE PERSON'S NAME'}
- Company: {company}
- Title: {title if title else 'FIND THEIR TITLE'}
- Email: {email}
- LinkedIn: {linkedin}

CRITICAL REQUIREMENTS:

1. PERSON PROFILE (MOST IMPORTANT - spend most effort here):
   - Full name (if not provided, try to find it)
   - Current job title and responsibilities
   - Professional background and career history
   - Education (universities, degrees, certifications)
   - Skills and areas of expertise
   - Recent activities (posts, articles, speaking engagements)
   - Social media profiles (LinkedIn, Twitter, Facebook, Instagram)
   - Professional interests and focus areas
   - Awards, recognition, or achievements

2. PERSONALITY ASSESSMENT:
   - Analyze their communication style from their online presence
   - Assess Myers-Briggs personality type based on professional behavior
   - Identify decision-making patterns
   - Communication preferences

3. SALES INTELLIGENCE:
   - Pain points specific to their role
   - Challenges they might be facing
   - Topics that would interest them
   - Trigger events for outreach
   - Budget authority level
   - Best way to approach them

4. COMPANY INFORMATION:
   - Company overview and mission
   - Products and services
   - Recent news and developments
   - Market position

IMPORTANT: Even if the person's name is not provided, try to identify them from the email, title, or LinkedIn URL. Use web search extensively to find current information.

Return your findings as valid JSON with ALL fields (use empty strings for unfound data):
{{
    "person_name": "Full name of the person",
    "current_title": "Current job title",
    "current_company": "Company name",
    "email": "Email address",
    "phone": "Phone number if found",
    "location": "City, State/Country",
    "overview": "2-3 sentence professional summary of the PERSON",
    "background": "Detailed work history",
    "education": "Educational background",
    "skills": ["Skill 1", "Skill 2", "Skill 3"],
    "recent_activities": "Recent posts, articles, or activities",
    "social_profiles": {{"linkedin": "", "twitter": "", "instagram": "", "facebook": ""}},
    "professional_interests": ["Interest 1", "Interest 2"],
    "myers_briggs": "MBTI type (e.g., ENTJ)",
    "personality_assessment": "Detailed personality analysis",
    "communication_style": "How they prefer to communicate",
    "decision_style": "How they make purchasing decisions",
    "pain_points": ["Pain point 1", "Pain point 2", "Pain point 3"],
    "talking_points": ["Topic 1", "Topic 2", "Topic 3"],
    "trigger_events": ["Event 1", "Event 2"],
    "budget_authority": "Their level of purchasing power",
    "best_contact_method": "Email, phone, or LinkedIn",
    "best_contact_time": "When to reach them",
    "company_overview": "Brief company description",
    "products_services": "What the company offers",
    "recent_company_news": "Latest developments",
    "market_position": "Industry standing",
    "competitors": ["Competitor 1", "Competitor 2"],
    "ai_score_reasoning": "Why this is a high-value contact (detailed)",
    "outreach_approach": "Personalized outreach strategy (2-3 paragraphs)"
}}"""

        # Call Perplexity API
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
                        "content": "You are an expert B2B sales researcher specializing in finding detailed personal and professional information. Always prioritize finding information about the PERSON over the company. Use web search extensively."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 4000,
                "search_domain_filter": ["linkedin.com", "twitter.com", "facebook.com"],
                "return_citations": True,
                "search_recency_filter": "month"
            },
            timeout=60
        )

        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']

            # Clean response
            content = content.replace("```json", "").replace("```", "").strip()
            if content.startswith('"') or content.startswith("'"):
                content = content[1:-1]

            try:
                enrichment_data = json.loads(content)

                # Update contact name if found
                if enrichment_data.get('person_name') and not name:
                    found_name = enrichment_data.get('person_name')
                    print(f"✅ Found person name: {found_name}")
                    with get_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE contacts SET name = ? WHERE id = ?",
                            (found_name, contact_id)
                        )
                        conn.commit()

            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing failed: {e}")
                enrichment_data = {
                    "overview": content[:500] if content else "Parse error",
                    "raw_response": content
                }

            # Extract fields
            pain_points = enrichment_data.get('pain_points', [])
            talking_points = enrichment_data.get('talking_points', [])
            myers_briggs = enrichment_data.get('myers_briggs', '')

            # Store in database
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """UPDATE contacts SET 
                        enrichment_data = ?,
                        pain_points = ?,
                        talking_points = ?,
                        myers_briggs = ?,
                        enrichment_status = 'complete',
                        enriched_at = ?
                    WHERE id = ?""",
                    (
                        json.dumps(enrichment_data),
                        json.dumps(pain_points) if isinstance(pain_points, list) else str(pain_points),
                        json.dumps(talking_points) if isinstance(talking_points, list) else str(talking_points),
                        myers_briggs,
                        datetime.now().isoformat(),
                        contact_id
                    )
                )
                conn.commit()

            print(f"✅ Deep enrichment complete!")
            print(f"   Person: {enrichment_data.get('person_name', 'Not found')}")
            print(f"   Title: {enrichment_data.get('current_title', 'Not found')}")
            print(f"   MBTI: {myers_briggs if myers_briggs else 'Not assessed'}")

        else:
            print(f"❌ Perplexity API error: {response.status_code}")
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE contacts SET enrichment_status = 'failed' WHERE id = ?",
                    (contact_id,)
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