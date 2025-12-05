#!/usr/bin/env python3
"""
Apex API Server - PRODUCTION VERSION
Three Perplexity Queries + MBTI/DISC Append
"""

import os
import sys
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sqlite3
from dotenv import load_dotenv
import requests
import logging
import traceback
from openai import OpenAI

# ============= SETUP =============
load_dotenv('/Users/chrisrabenold/projects/apex/.env')

BACKEND_PATH = '/Users/chrisrabenold/projects/apex/apps/backend'
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HUBSPOT_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HUBSPOT_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logger.info(f"Perplexity Key: {'✅ Found' if PERPLEXITY_API_KEY else '❌ Missing'}")
logger.info(f"OpenAI Key: {'✅ Found' if OPENAI_API_KEY else '❌ Missing'}")


# ============= ENHANCED ENRICHMENT =============
class EnhancedEnrichment:
    """
    Pipeline: 3 Perplexity Queries → Save ALL Data → GPT for MBTI/DISC only → Append
    """

    def __init__(self):
        self.perplexity_key = PERPLEXITY_API_KEY
        self.openai_key = OPENAI_API_KEY
        self.output_dir = '/Users/chrisrabenold/projects/apex/enrichment_profiles'

        if not self.perplexity_key:
            raise ValueError("Missing Perplexity API key")

        os.makedirs(self.output_dir, exist_ok=True)

    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment pipeline"""
        try:
            result = self.build_profile(contact)
            return result
        except Exception as e:
            logger.error(f"❌ Enrichment failed: {e}")
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def build_profile(self, contact: dict) -> dict:
        """Three Perplexity queries + MBTI/DISC append"""

        name = contact.get('name') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        title = contact.get('title', '')
        company = contact.get('company', '')

        logger.info("=" * 80)
        logger.info(f"🔍 PROFILE BUILDER: {name} at {company}")
        logger.info("=" * 80)

        # =========================================================================
        # STAGE 1A: PERSON RESEARCH
        # =========================================================================
        logger.info("📡 STAGE 1A: PERPLEXITY - PERSON RESEARCH")

        person_query = f"""Research {name}, {title} at {company}.

Find and report everything you can about:
1. Current role, responsibilities, and tenure
2. Complete career history with dates and previous positions
3. Education, degrees, and credentials
4. Professional achievements, awards, and recognition
5. LinkedIn activity, posts, and thought leadership
6. Speaking engagements, podcasts, or media appearances
7. Professional associations, board positions, and affiliations
8. Management style and professional philosophy
9. Notable deals, projects, or accomplishments

Be extremely thorough. Include all dates, company names, titles, and specific details."""

        person_research = self.call_perplexity(person_query)
        person_chars = len(person_research or '')
        logger.info(f"✅ Person research: {person_chars} chars")

        # =========================================================================
        # STAGE 1B: COMPANY RESEARCH
        # =========================================================================
        logger.info("📡 STAGE 1B: PERPLEXITY - COMPANY RESEARCH")

        company_query = f"""Research {company} as a business entity.

Find and report everything about:
1. Company overview - founding date, headquarters, employee count, revenue
2. Business model and how they make money
3. Products, services, and offerings
4. Target markets and customer segments
5. Competitive landscape - key competitors and differentiation
6. Recent news - funding, acquisitions, leadership changes, strategic moves
7. Company culture, values, and mission
8. Leadership team and organizational structure
9. Technology stack and innovations
10. Market position, growth trajectory, and industry standing

Be extremely thorough with specific numbers, dates, and details."""

        company_research = self.call_perplexity(company_query)
        company_chars = len(company_research or '')
        logger.info(f"✅ Company research: {company_chars} chars")

        # =========================================================================
        # STAGE 1C: SALES INTELLIGENCE
        # =========================================================================
        logger.info("📡 STAGE 1C: PERPLEXITY - SALES INTELLIGENCE")

        sales_query = f"""Analyze sales opportunity for reaching {name}, {title} at {company}.

Research and report on:
1. Industry trends affecting {company}'s sector right now
2. Common pain points for {title} roles in this industry
3. Regulatory or compliance challenges they likely face
4. Technology trends impacting their business
5. Economic factors affecting their decision-making
6. Recent company challenges or opportunities in the news
7. Typical buying triggers for this persona type
8. Budget cycles and procurement patterns in this industry
9. Key initiatives companies like {company} are prioritizing
10. Competitive pressures they're facing

Focus on actionable intelligence for sales engagement."""

        sales_research = self.call_perplexity(sales_query)
        sales_chars = len(sales_research or '')
        logger.info(f"✅ Sales research: {sales_chars} chars")

        # =========================================================================
        # COMBINE ALL RESEARCH (PRESERVE EVERYTHING)
        # =========================================================================
        combined_research = f"""=== PERSON RESEARCH: {name} ===

{person_research or 'No data available'}

=== COMPANY RESEARCH: {company} ===

{company_research or 'No data available'}

=== SALES INTELLIGENCE ===

{sales_research or 'No data available'}
"""

        total_chars = len(combined_research)
        logger.info(f"✅ STAGE 1 COMPLETE: {total_chars} characters total")

        # =========================================================================
        # STAGE 2: GPT FOR MBTI/DISC ONLY (APPEND, DON'T REPLACE)
        # =========================================================================
        logger.info("🧠 STAGE 2: GPT-4O - MBTI/DISC ANALYSIS ONLY")

        personality_analysis = self.get_personality_analysis(combined_research, name, title, company)

        if personality_analysis:
            logger.info(f"✅ Personality analysis: {len(personality_analysis)} chars")
            # APPEND personality to the end
            final_profile = combined_research + "\n\n" + personality_analysis
        else:
            logger.warning("⚠️ Personality analysis failed, using raw research only")
            final_profile = combined_research

        final_chars = len(final_profile)
        logger.info(f"✅ FINAL PROFILE: {final_chars} characters")

        # Save debug file
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.output_dir}/profile_{contact.get('id', 'unknown')}_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"# Profile: {name}\n")
                f.write(f"# Generated: {timestamp}\n")
                f.write(f"# Person: {person_chars} | Company: {company_chars} | Sales: {sales_chars} | Total: {final_chars}\n")
                f.write("=" * 80 + "\n\n")
                f.write(final_profile)
            logger.info(f"💾 Saved: {filename}")
        except Exception as e:
            logger.warning(f"Could not save profile file: {e}")

        logger.info("=" * 80)
        logger.info("✅ ENRICHMENT COMPLETE!")
        logger.info("=" * 80)

        return {
            'success': True,
            'profile_text': final_profile,
            'character_count': final_chars,
            'breakdown': {
                'person': person_chars,
                'company': company_chars,
                'sales': sales_chars,
                'personality': len(personality_analysis or '')
            }
        }

    def call_perplexity(self, query: str) -> str:
        """Call Perplexity API"""
        try:
            logger.info("📡 Calling Perplexity API...")

            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a professional research analyst. Provide extremely thorough, factual research. Include ALL specific details, dates, names, numbers, and sources you can find. Do not summarize - be comprehensive."
                        },
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.1
                },
                timeout=90
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                logger.info("✅ Perplexity API successful")
                return content
            else:
                logger.error(f"❌ Perplexity error {response.status_code}: {response.text[:200]}")
                return None

        except Exception as e:
            logger.error(f"❌ Perplexity error: {e}")
            return None

    def get_personality_analysis(self, research: str, name: str, title: str, company: str) -> str:
        """Small focused GPT call for MBTI/DISC only - APPENDS to data"""

        if not self.openai_key:
            return None

        prompt = f"""Based on this research about {name}, {title} at {company}, infer their personality profile.

RESEARCH:
{research[:8000]}

Provide ONLY the following analysis (this will be APPENDED to the research above):

=== PERSONALITY ANALYSIS ===

## Myers-Briggs (MBTI) Assessment

**Inferred Type:** [XXXX]
**Confidence:** [High/Medium/Low]

| Dimension | Preference | Evidence from Research |
|-----------|------------|----------------------|
| Energy | [E or I] - Extraversion/Introversion | [Specific evidence] |
| Information | [S or N] - Sensing/Intuition | [Specific evidence] |
| Decisions | [T or F] - Thinking/Feeling | [Specific evidence] |
| Structure | [J or P] - Judging/Perceiving | [Specific evidence] |

**Work Style:** [How they likely approach work based on type]

## DISC Profile Assessment

**Primary Style:** [D, I, S, or C]
**Secondary Style:** [D, I, S, or C]

| Style | Estimated % | Evidence |
|-------|-------------|----------|
| D - Dominance | [X]% | [Evidence of direct, results-oriented behavior] |
| I - Influence | [X]% | [Evidence of people-oriented, enthusiastic behavior] |
| S - Steadiness | [X]% | [Evidence of patient, reliable behavior] |
| C - Conscientiousness | [X]% | [Evidence of analytical, detail-oriented behavior] |

## Communication Playbook

### ✅ DO: How to Engage This Person
- [Specific approach based on their personality]
- [Communication style that resonates]
- [Topics/angles that will interest them]

### ❌ DON'T: What to Avoid
- [Communication mistakes to avoid]
- [Approaches that won't work]
- [Topics to steer clear of]

### 🎯 Best Opening Approach
[Specific recommendation for first outreach based on personality]

Be specific and cite evidence from the research. If evidence is limited, note lower confidence."""

        try:
            client = OpenAI(api_key=self.openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert in personality assessment. Analyze the research and provide MBTI and DISC profiles with specific evidence."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ GPT-4 personality error: {e}")
            return None


# Mark enrichment as available
ENRICHMENT_AVAILABLE = True
logger.info("✅ EnhancedEnrichment loaded (Perplexity + MBTI/DISC append)")


# ============= SCORING FALLBACK =============
SCORING_AVAILABLE = False

def score_contact_from_db(conn, contact_id, trigger='manual'):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
    row = cursor.fetchone()
    if not row:
        return {'error': 'Contact not found'}

    columns = [desc[0] for desc in cursor.description]
    contact = dict(zip(columns, row))

    score = 50
    if contact.get('email'): score += 10
    if contact.get('phone'): score += 10
    if contact.get('company'): score += 10
    if contact.get('title'): score += 10
    if contact.get('linkedin_url'): score += 10

    tier = 'HOT' if score >= 80 else 'WARM' if score >= 70 else 'QUALIFIED'

    cursor.execute('''
        UPDATE contacts
        SET mdcp_score = ?, mdcp_tier = ?, last_scored = ?
        WHERE id = ?
    ''', (score, tier, datetime.now().isoformat(), contact_id))
    conn.commit()

    return {'success': True, 'contact_id': contact_id, 'scores': {'mdcp_score': score, 'mdcp_tier': tier}}


# ============= FLASK APP =============
app = Flask(__name__)
CORS(app)

DATABASE = '/Users/chrisrabenold/projects/apex/apex.db'
PORT = 8000


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_columns():
    conn = get_db()
    cursor = conn.cursor()
    columns = [
        ('mdcp_score', 'REAL'), ('mdcp_tier', 'TEXT'), ('priority_score', 'REAL'),
        ('enrichment_status', 'TEXT'), ('enrichment_data', 'TEXT'),
        ('enriched', 'INTEGER'), ('enriched_at', 'TEXT'), ('last_scored', 'TEXT')
    ]
    for col, typ in columns:
        try:
            cursor.execute(f'ALTER TABLE contacts ADD COLUMN {col} {typ}')
        except:
            pass
    conn.commit()
    conn.close()

ensure_columns()


# ============= ROUTES =============

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'enrichment_available': ENRICHMENT_AVAILABLE,
        'features': ['perplexity_research', 'mbti_disc_analysis']
    })


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    try:
        conn = get_db()
        cursor = conn.cursor()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        cursor.execute('SELECT * FROM contacts ORDER BY id DESC LIMIT ? OFFSET ?', (limit, offset))
        contacts = [dict(row) for row in cursor.fetchall()]

        cursor.execute('SELECT COUNT(*) FROM contacts')
        total = cursor.fetchone()[0]
        conn.close()

        return jsonify({'contacts': contacts, 'total': total})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = cursor.fetchone()
        conn.close()

        if contact:
            return jsonify(dict(contact))
        return jsonify({'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"success": False, "error": "Contact not found"}), 404

        contact = dict(row)

        cursor.execute("UPDATE contacts SET enrichment_status = 'processing' WHERE id = ?", (contact_id,))
        conn.commit()
        conn.close()

        name = contact.get('name') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        logger.info(f"🔍 Starting enrichment for {name}")

        enricher = EnhancedEnrichment()
        result = enricher.enrich_contact(contact)

        if result and result.get('success'):
            conn = get_db()
            conn.execute("""
                UPDATE contacts SET
                enrichment_data = ?,
                enriched = 1,
                enriched_at = ?,
                enrichment_status = 'completed'
                WHERE id = ?
            """, (result['profile_text'], datetime.now().isoformat(), contact_id))
            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'contact_id': contact_id,
                'status': 'completed',
                'profile_length': result['character_count'],
                'breakdown': result.get('breakdown', {})
            }), 200
        else:
            conn = get_db()
            conn.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = ?", (contact_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': False, 'error': result.get('error', 'Failed')}), 500

    except Exception as e:
        logger.error(f"❌ Enrichment error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>/enrichment-status', methods=['GET'])
def get_enrichment_status(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT enrichment_status, enriched_at FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': 'Contact not found'}), 404

        return jsonify({
            'contact_id': contact_id,
            'status': row['enrichment_status'] or 'pending',
            'last_enriched': row['enriched_at']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>/reset-enrichment', methods=['POST'])
def reset_enrichment(contact_id):
    try:
        conn = get_db()
        conn.execute("""
            UPDATE contacts SET enrichment_status = 'pending', enrichment_data = NULL, enriched = 0, enriched_at = NULL
            WHERE id = ?
        """, (contact_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/todays-board', methods=['GET'])
def get_todays_board():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, email, phone, company, title, mdcp_score, enrichment_status, enriched_at
            FROM contacts ORDER BY id DESC LIMIT 100
        """)
        contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()

        hot = [c for c in contacts if (c.get('mdcp_score') or 0) >= 80]
        warm = [c for c in contacts if 60 <= (c.get('mdcp_score') or 0) < 80]

        return jsonify({
            'success': True,
            'date': datetime.now().strftime('%B %d, %Y'),
            'total_contacts': len(contacts),
            'hot_count': len(hot),
            'warm_count': len(warm),
            'contacts': contacts
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# =============================================================================
# ADD TO api.py - PERSONA GENERATION ENDPOINT
# =============================================================================
    
from persona_generator import process_profile, generate_persona_outputs

@app.post("/api/contacts/{contact_id}/generate-persona")
async def generate_persona(contact_id: int):
    """
    Generate full persona outputs (PDFs, briefs, CRM summary) from enrichment data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"error": "Contact not found"}, 404
    
    contact = dict(row)
    
    if contact['enrichment_status'] != 'enriched' or not contact['enrichment_data']:
        return {"error": "Contact must be enriched first"}, 400
    
    # Process through GPT-4o pipeline
    result = process_profile(
        raw_data=contact['enrichment_data'],
        contact_name=f"{contact['first_name']} {contact['last_name']}",
        contact_id=contact_id
    )
    
    return result


@app.get("/api/contacts/{contact_id}/persona-outputs")
async def get_persona_outputs(contact_id: int):
    """
    Get previously generated persona outputs for a contact.
    """
    from persona_generator import OUTPUT_DIR
    import glob
    
    files = glob.glob(os.path.join(OUTPUT_DIR, f"*_{contact_id}_*"))
    
    if not files:
        return {"status": "not_found", "message": "No persona outputs found for this contact"}
    
    return {
        "status": "found",
        "files": files
    }

# =============================================================================
# ADD TO api.py - FILE DOWNLOAD ENDPOINT
# =============================================================================

from flask import send_file
import os

@app.route('/api/download')
def download_file():
    """Serve generated files for download."""
    filepath = request.args.get('path', '')
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    # Security: ensure file is in allowed directory
    allowed_dir = os.path.expanduser("~/projects/apex/persona_outputs")
    if not os.path.abspath(filepath).startswith(os.path.abspath(allowed_dir)):
        return jsonify({"error": "Access denied"}), 403
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=os.path.basename(filepath)
    )
    


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 APEX API SERVER")
    logger.info("=" * 60)
    logger.info(f"📊 Database: {DATABASE}")
    logger.info(f"🔌 Port: {PORT}")
    logger.info("🧠 Pipeline: Perplexity (17K) + MBTI/DISC append")
    logger.info("=" * 60)
    app.run(host='0.0.0.0', port=PORT, debug=True)
    