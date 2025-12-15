# ENRICHMENT MODIFICATION — STEP-BY-STEP INTEGRATION

## WHAT TO MODIFY

Your attached `api.py` has the enrichment endpoint at **line ~1235**.

We need to:
1. **Add 2 helper functions** before the EnhancedEnrichment class (~line 90-95)
2. **Replace the entire enrich_contact endpoint** (~line 1235-1350)

---

## STEP 1: ADD HELPER FUNCTIONS (Insert at line ~90)

**Location:** After the imports and environment setup, BEFORE the `EnhancedEnrichment` class

**Find this:**
```python
# ═══════════════════════════════════════════════════════════════════════════
# INLINE PROFILE BUILDER ENRICHMENT ENGINE (3-Stage Intelligence)
# ═══════════════════════════════════════════════════════════════════════════

class EnhancedEnrichment:
    """
    Profile Builder - Three-stage enrichment pipeline:
    Stage 1: Perplexity sonar-pro comprehensive research
    Stage 2: GPT-4 intelligence interpolation & structuring
    Stage 3: Database persistence (handled by endpoint)

    Output matches "Profile Builder" Perplexity Space format
    """
```

**Add these functions JUST BEFORE that section:**

```python
# ════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR ENRICHMENT DATA PREPARATION
# ════════════════════════════════════════════════════════════════════════════

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

```

---

## STEP 2: REPLACE ENRICHMENT ENDPOINT (Replace at line ~1235)

**Find this section:**

```python
@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    """
    3-Stage Enrichment Pipeline:
    STAGE 1: Perplexity raw research
    STAGE 2: GPT-4 structuring + intelligence layers
    STAGE 3: Database save + MDCP scoring
    """
    try:
        if not enrichment_engine:
            return jsonify({'success': False, 'error': 'Enrichment engine unavailable'}), 503
        # ... rest of function through the final except block ...
```

**Replace the ENTIRE function with this:**

```python
@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    """
    3-Stage Enrichment Pipeline with improved data preparation:
    STAGE 1: Perplexity research with clean seed data
    STAGE 2: GPT-4 structuring + intelligence layers
    STAGE 3: Database save + MDCP scoring
    """
    try:
        if not enrichment_engine:
            return jsonify({'success': False, 'error': 'Enrichment engine unavailable'}), 503

        conn = get_db()
        cursor = dict_cursor(conn) if IS_PRODUCTION else conn.cursor()
        param_style = '%s' if IS_PRODUCTION else '?'

        cursor.execute(f"SELECT * FROM contacts WHERE id = {param_style}", (contact_id,))

        if IS_PRODUCTION:
            row = cursor.fetchone()
            contact = row if row else None
        else:
            row = cursor.fetchone()
            contact = dict(row) if row else None

        if not contact:
            conn.close()
            return jsonify({"success": False, "error": "Contact not found"}), 404

        conn.close()

        # ⭐ NEW: Prepare clean data
        seed_data = prepare_enrichment_data(contact)
        print(f"\n📊 ENRICHMENT DATA PREPARED:")
        print(f"   Name:    {seed_data['name']}")
        print(f"   Title:   {seed_data['title']}")
        print(f"   Company: {seed_data['company']}")
        print(f"   Phone:   {seed_data['phone']}")
        print(f"   LinkedIn: {seed_data['linkedin_url'] if seed_data['linkedin_url'] else '(none)'}")

        # ⭐ NEW: Build improved prompt
        research_prompt = build_enrichment_prompt(seed_data)

        # STAGE 1: Perplexity Research
        print(f"\n🔍 STAGE 1: Perplexity Research...")
        perplexity_response = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={
                'Authorization': f'Bearer {os.getenv("PERPLEXITY_API_KEY")}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'sonar-pro',
                'messages': [{'role': 'user', 'content': research_prompt}],
                'max_tokens': 2000,
                'temperature': 0.7,
                'search_context_size': 2  # ⭐ NEW: Richer context
            },
            timeout=60
        )

        if perplexity_response.status_code != 200:
            return jsonify({
                'error': f'Perplexity API failed: {perplexity_response.status_code}'
            }), 500

        research_content = perplexity_response.json()['choices'][0]['message']['content']
        print(f"✅ Research content ({len(research_content)} chars)")

        # STAGE 2: GPT-4 Synthesis
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
            return jsonify({'error': f'GPT-4 API failed: {gpt_response.status_code}'}), 500

        profile_content = gpt_response.json()['choices'][0]['message']['content']
        print(f"✅ Profile content ({len(profile_content)} chars)")

        # STAGE 3: Save to Database + Score
        print(f"\n💾 STAGE 3: Saving Profile & Scoring...")

        conn = get_db()
        cursor = dict_cursor(conn) if IS_PRODUCTION else conn.cursor()
        timestamp = datetime.now().isoformat()

        if IS_PRODUCTION:
            cursor.execute("""
                UPDATE contacts 
                SET profile_content = %s,
                    enrichment_status = %s,
                    enrichment_date = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (profile_content, 'completed', timestamp, contact_id))
        else:
            cursor.execute("""
                UPDATE contacts 
                SET profile_content = ?,
                    enrichment_status = ?,
                    enrichment_date = ?,
                    updated_at = ?
                WHERE id = ?
            """, (profile_content, 'completed', timestamp, timestamp, contact_id))

        conn.commit()

        print(f"✅ Profile saved to database")

        # Auto-score contact
        scores = None
        if SCORING_AVAILABLE:
            print(f"🎯 Running Unified Apex Scoring...")
            try:
                unified_scorer = UnifiedApexScorer(db_path=SCORING_DB_PATH)
                result = unified_scorer.score_contact_unified(contact_id, save_to_db=True)
                scores = result
                print(f"✅ Auto-scored: {result.get('mdcp_tier')} ({result.get('priority_score')})")
            except Exception as score_error:
                print(f"⚠️ Scoring failed: {score_error}")
                # Don't fail enrichment if scoring errors

        conn.close()

        print(f"✅ ✅ ✅ ENRICHMENT COMPLETE for contact {contact_id}")

        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'contact_name': seed_data['name'],
            'status': 'enriched',
            'profile_length': len(profile_content),
            'seed_data': seed_data,
            'scores': {
                'mdcp_score': scores.get('mdcp_score') if scores else None,
                'priority_score': scores.get('priority_score') if scores else None,
                'tier': scores.get('mdcp_tier') if scores else None
            } if scores else None,
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
```

---

## CRITICAL POINTS

✅ **DO NOT** modify the EnhancedEnrichment class — leave it as-is
✅ **DO** add the 2 helper functions BEFORE EnhancedEnrichment
✅ **DO** replace the entire enrich_contact function (lines ~1235-1350)
✅ **Make sure** prepare_enrichment_data() is called FIRST in enrich_contact()
✅ **Make sure** build_enrichment_prompt() uses the cleaned seed_data

---

## AFTER MODIFICATIONS

1. Save your modified `api.py`
2. Test locally: `python3 api.py` then `curl -X POST "http://localhost:8000/api/contacts/2067/enrich" | jq '.'`
3. Deploy: `git add api.py && git commit -m "Fix: Enrichment data prep improvements" && git push origin main`
4. Wait 60 seconds for Railway build
5. Test on production: `curl -X POST "https://apex-intelligence-production.up.railway.app/api/contacts/2067/enrich"`

---

## BEFORE vs AFTER COMPARISON

| Component | Before | After |
|-----------|--------|-------|
| **Phone** | Empty or main phone | Falls back to mobile → main phone |
| **LinkedIn** | Empty, ignored | Marked as `[searching for...]` |
| **Title** | "Senior Consultant at X NMLS#123 DRE#456" | "Senior Consultant" |
| **Prompt** | Minimal context | Rich research focus + data requirements |
| **Data Prep** | Inline in endpoint | Standardized function |
| **Logging** | Sparse | Stage-by-stage detail |
| **Result** | Weak profiles | Strong, structured profiles |

---

## NEXT STEP

Once deployed and tested:

```bash
# Test on 10 contacts
python3 << 'EOF'
import requests

TEST_IDS = [2067, 2070, 2075, ...]  # Your 10 contact IDs
API_URL = "https://apex-intelligence-production.up.railway.app"

for cid in TEST_IDS:
    r = requests.post(f"{API_URL}/api/contacts/{cid}/enrich")
    print(f"Contact {cid}: {r.status_code}")
EOF

# Wait 30 mins for enrichment to complete
# Review quality of profiles in database
# Proceed to bulk enrichment of all 1,222 contacts
```

Ready to integrate? Let me know if you need clarification on any line numbers!
