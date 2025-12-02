#!/usr/bin/env python3
"""
APEX ENRICHMENT ENGINE — DATA PREPARATION FIX
Ensures minimum required fields are extracted and passed to Perplexity/GPT-4

Location: Insert into ~/projects/apex/api.py (replace existing enrichment endpoint)
Issue: Weak enrichment results due to incomplete/missing data in Perplexity queries
Solution: Standardize data extraction and cleaning before enrichment call
"""

# ============================================================================
# ADD THIS FUNCTION TO api.py (around line 85, before enrichment class)
# ============================================================================

def prepare_enrichment_data(contact):
    """
    Extract and clean minimum required fields for enrichment.
    Handles missing/empty fields gracefully.
    
    Returns:
        dict: Cleaned contact data {name, title, company, email, phone, phone_mobile, linkedin_url}
    """
    # Extract core fields
    name = (contact.get('name') or contact.get('firstname', '') + ' ' + contact.get('lastname', '')).strip()
    
    # Clean title: extract just the title, remove company/license info
    raw_title = contact.get('title') or contact.get('job_title') or ''
    title = raw_title.split(' at ')[0].strip() if ' at ' in raw_title else raw_title[:50].strip()
    
    # Company
    company = (contact.get('company') or 'Unknown').strip()
    
    # Email
    email = (contact.get('email') or '').strip()
    
    # Phone: prefer mobile, fallback to main phone
    phone_mobile = (contact.get('phone_mobile') or '').strip()
    phone = (contact.get('phone') or '').strip()
    
    # Use mobile if available, otherwise main phone, otherwise empty
    best_phone = phone_mobile if phone_mobile else phone
    
    # LinkedIn URL (may be empty)
    linkedin_url = (contact.get('linkedin_url') or '').strip()
    
    return {
        'name': name,
        'title': title,
        'company': company,
        'email': email,
        'phone': best_phone,
        'phone_mobile': best_phone,  # Use same as phone if mobile not available
        'linkedin_url': linkedin_url,
        'original_title': raw_title  # Keep for reference
    }


def build_enrichment_prompt(seed_data):
    """
    Build Perplexity search prompt from seed data.
    Constructs research query with all available context.
    
    Args:
        seed_data: dict from prepare_enrichment_data()
        
    Returns:
        str: Formatted Perplexity research prompt
    """
    name = seed_data.get('name', 'Unknown')
    title = seed_data.get('title', 'Unknown')
    company = seed_data.get('company', 'Unknown')
    email = seed_data.get('email', '')
    phone = seed_data.get('phone', '')
    linkedin_url = seed_data.get('linkedin_url', '')
    
    # Build prompt with available contact info
    prompt = f"""Research professional: {name}
Title: {title}
Company: {company}"""
    
    # Add contact info if available
    if email:
        prompt += f"\nEmail: {email}"
    if phone:
        prompt += f"\nPhone: {phone}"
    
    # LinkedIn context
    if linkedin_url:
        prompt += f"\nLinkedIn: {linkedin_url}"
    else:
        prompt += "\nLinkedIn: [searching for LinkedIn profile]"
    
    # Research objectives
    prompt += """

Research Focus:
- Company background, recent news, growth trajectory
- Industry positioning and competitive landscape
- Pain points in their industry/role
- Recent funding, partnerships, or announcements
- Professional background and career progression
- Decision-making authority and influence
- Buying triggers and growth opportunities
- Communication style and personality indicators

Provide specific examples, quotes, and data points where possible."""
    
    return prompt


# ============================================================================
# UPDATED ENRICHMENT ENDPOINT (replace /api/contacts/<id>/enrich)
# ============================================================================

@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    """
    Trigger AI enrichment for a single contact.
    Enhanced with proper data preparation.
    
    Flow:
    1. Fetch contact from database
    2. Prepare/clean minimum data fields
    3. Build Perplexity research prompt
    4. Run 3-stage enrichment (Perplexity → GPT-4 → Save)
    5. Auto-score after enrichment
    """
    try:
        # 1. Fetch contact
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if IS_PRODUCTION:
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            contact = dict(contact) if contact else None
        else:
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            contact = dict(row) if row else None
        
        conn.close()
        
        if not contact:
            return jsonify({'error': f'Contact {contact_id} not found'}), 404
        
        # 2. Validate LinkedIn URL (warn if missing)
        linkedin_url = (contact.get('linkedin_url') or '').strip()
        if not linkedin_url:
            print(f"⚠️  Contact {contact['name']} has no LinkedIn URL - enrichment quality may be lower")
        
        # 3. Prepare enrichment data
        seed_data = prepare_enrichment_data(contact)
        print(f"\n📊 ENRICHMENT DATA PREPARED:")
        print(f"   Name:    {seed_data['name']}")
        print(f"   Title:   {seed_data['title']}")
        print(f"   Company: {seed_data['company']}")
        print(f"   Email:   {seed_data['email']}")
        print(f"   Phone:   {seed_data['phone']}")
        print(f"   LinkedIn: {seed_data['linkedin_url'] if seed_data['linkedin_url'] else '(none)'}")
        
        # 4. Build Perplexity prompt
        research_prompt = build_enrichment_prompt(seed_data)
        
        # 5. STAGE 1: Perplexity Research
        print(f"\n🔍 STAGE 1: Perplexity Research...")
        perplexity_response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={
                'Authorization': f'Bearer {os.getenv("PERPLEXITY_API_KEY")}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'sonar-pro',
                'messages': [
                    {
                        'role': 'user',
                        'content': research_prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.7,
                'search_context_size': 2
            },
            timeout=60
        )
        
        if perplexity_response.status_code != 200:
            return jsonify({
                'error': f'Perplexity API failed: {perplexity_response.status_code}',
                'details': perplexity_response.text
            }), 500
        
        perplexity_data = perplexity_response.json()
        research_content = perplexity_data['choices'][0]['message']['content']
        print(f"✅ Research content ({len(research_content)} chars)")
        
        # 6. STAGE 2: GPT-4 Synthesis
        print(f"\n🧠 STAGE 2: GPT-4 Profile Synthesis...")
        
        gpt_prompt = f"""Based on this research about {seed_data['name']}:

{research_content}

Create a structured professional profile with:
1. EXECUTIVE SUMMARY (3 sentences)
2. PAIN POINTS (top 3)
3. OPPORTUNITIES (for engagement)
4. PERSONALITY ASSESSMENT (communication style)
5. TALKING POINTS (3 conversation starters)
6. CALL SCRIPT LEVEL 1 (opener)
7. CALL SCRIPT LEVEL 2 (follow-up)
8. CALL SCRIPT LEVEL 3 (deep dive)
9. EMAIL TEMPLATE (initial outreach)
10. WHY NOW (urgency signal)
11. BUYING TRIGGERS (signals to watch)
12. NEXT STEPS (recommended action)

Format as JSON with these exact keys."""

        gpt_response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4',
                'messages': [
                    {
                        'role': 'user',
                        'content': gpt_prompt
                    }
                ],
                'max_tokens': 3000,
                'temperature': 0.7
            },
            timeout=60
        )
        
        if gpt_response.status_code != 200:
            return jsonify({
                'error': f'GPT-4 API failed: {gpt_response.status_code}',
                'details': gpt_response.text
            }), 500
        
        gpt_data = gpt_response.json()
        profile_content = gpt_data['choices'][0]['message']['content']
        print(f"✅ Profile content ({len(profile_content)} chars)")
        
        # 7. STAGE 3: Save to Database + Score
        print(f"\n💾 STAGE 3: Saving Profile & Scoring...")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        if IS_PRODUCTION:
            cursor.execute("""
                UPDATE contacts 
                SET profile_content = %s,
                    enrichment_status = %s,
                    enriched_at = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (profile_content, 'completed', timestamp, contact_id))
        else:
            cursor.execute("""
                UPDATE contacts 
                SET profile_content = ?,
                    enrichment_status = ?,
                    enriched_at = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (profile_content, 'completed', timestamp, contact_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Profile saved to database")
        
        # 8. Auto-score contact
        if SCORING_AVAILABLE:
            scoring_db_path = os.getenv('DATABASE_URL') if IS_PRODUCTION else DB_PATH
            unified_scorer = UnifiedApexScorer(db_path=scoring_db_path)
            result = unified_scorer.score_contact_unified(contact_id, save_to_db=True)
            print(f"✅ Auto-scored: {result.get('mdcp_tier')} ({result.get('priority_score')})")
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'contact_name': seed_data['name'],
            'status': 'enriched',
            'profile_length': len(profile_content),
            'seed_data': seed_data,
            'timestamp': timestamp
        }), 200
        
    except Exception as e:
        print(f"❌ Enrichment failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Enrichment failed',
            'details': str(e)
        }), 500


# ============================================================================
# TESTING: Use this to test enrichment with your 10 contacts
# ============================================================================

"""
Test enrichment with improved data:

cd ~/projects/apex
source .venv/bin/activate
python3 << 'EOF'
import requests

API_URL = 'http://localhost:8000'
TEST_CONTACTS = [2067]  # Add your contact IDs here

for contact_id in TEST_CONTACTS:
    print(f"\n{'='*60}")
    print(f"Testing enrichment for contact {contact_id}")
    print(f"{'='*60}")
    
    response = requests.post(f"{API_URL}/api/contacts/{contact_id}/enrich")
    print(response.json())
    
EOF

"""
