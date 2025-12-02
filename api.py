#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
APEX SALES INTELLIGENCE API SERVER

Smart Dual-Environment Configuration

- LOCAL: SQLite (fast development)
- PRODUCTION: PostgreSQL on Railway

Date: December 1, 2025
Modified: Added enrichment data preparation, 8-persona classifier,
          and Dashboard_v1 /api/todays-board endpoint
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# ================================================================
# ENVIRONMENT SETUP
# ================================================================

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# ================================================================
# SMART ENVIRONMENT DETECTION
# ================================================================

IS_PRODUCTION = os.getenv('DATABASE_URL') is not None
ENVIRONMENT = "PRODUCTION" if IS_PRODUCTION else "LOCAL"
logger.info(f"🌍 Environment: {ENVIRONMENT}")

# ================================================================
# PATH CONFIGURATION
# ================================================================

BACKEND_PATH = Path(__file__).parent / 'apps' / 'backend'
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

GENERATORS_PATH = BACKEND_PATH / 'intelligence' / 'engines' / 'outreach' / 'generators'
if str(GENERATORS_PATH) not in sys.path:
    sys.path.insert(0, str(GENERATORS_PATH))

# ================================================================
# API KEYS
# ================================================================

HUBSPOT_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HUBSPOT_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logger.info(f"HubSpot Token: {'✅ Found' if HUBSPOT_TOKEN else '❌ Missing'}")
logger.info(f"Perplexity Key: {'✅ Found' if PERPLEXITY_API_KEY else '❌ Missing'}")
logger.info(f"OpenAI Key: {'✅ Found' if OPENAI_API_KEY else '❌ Missing'}")

# ================================================================
# IMPORT / INITIALIZE ENGINES
# ================================================================

enrichment_engine = object()  # simple truthy stub for /health
scoring_engine = None
auto_sequence_engine = None
cadence_router = None

# Unified Apex Scoring (optional)
DB_PATH = os.path.join(os.path.dirname(__file__), 'apex.db')
scoring_path = os.path.join(os.path.dirname(__file__), 'apps', 'backend', 'intelligence', 'engines', 'scoring')
sys.path.insert(0, scoring_path)

try:
    from unified_apex_scorer import UnifiedApexScorer  # type: ignore
    SCORING_AVAILABLE = True
    if IS_PRODUCTION:
        SCORING_DB_PATH = os.getenv('DATABASE_URL')
    else:
        SCORING_DB_PATH = DB_PATH
    logger.info(f"✅ Unified Apex Scoring Engine loaded (DB: {'PostgreSQL' if IS_PRODUCTION else 'SQLite'})")
except Exception as e:
    logger.warning(f"⚠️ Scoring engine not available: {e}")
    SCORING_AVAILABLE = False
    SCORING_DB_PATH = None

# 8-PERSONA CLASSIFIER
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps/backend/intelligence/engines/classification'))
try:
    from apex_8persona_classifier import Apex8PersonaClassifier  # type: ignore
    persona_engine = Apex8PersonaClassifier()
    PERSONA_AVAILABLE = True
    logger.info("✅ 8-Persona Classifier loaded (loan_broker / banker / etc.)")
except Exception as e:
    logger.warning(f"⚠️ Persona classifier unavailable: {e}")
    persona_engine = None
    PERSONA_AVAILABLE = False

# ================================================================
# FLASK APP INITIALIZATION
# ================================================================

app = Flask(__name__)
CORS(app)
PORT = int(os.getenv('PORT', 8000))

# ================================================================
# SMART DATABASE CONFIGURATION
# ================================================================

if IS_PRODUCTION:
    # PostgreSQL on Railway
    DATABASE_URL = os.getenv('DATABASE_URL')
    logger.info("📊 Database: PostgreSQL (Railway)")

    try:
        import psycopg2  # type: ignore
        from psycopg2.extras import RealDictCursor  # type: ignore

        def get_db():
            return psycopg2.connect(DATABASE_URL)

        def dict_cursor(conn):
            return conn.cursor(cursor_factory=RealDictCursor)

    except ImportError:
        logger.error("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
        raise
else:
    # SQLite local
    import sqlite3
    DATABASE = DB_PATH
    logger.info(f"📊 Database: SQLite ({DATABASE})")

    def get_db():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    def dict_cursor(conn):
        return conn.cursor()

def get_db_connection():
    return get_db()

logger.info(f"🚀 Server Port: {PORT}")

# ================================================================
# SCHEMA MANAGEMENT
# ================================================================

def ensure_schema():
  """Ensure required tables/columns exist (production-safe, no txn poisoning)."""
  conn = get_db()
  try:
    # Force autocommit in production to avoid InFailedSqlTransaction
    if IS_PRODUCTION:
      try:
        conn.autocommit = True
      except Exception:
        pass
    cursor = dict_cursor(conn)
    
    if IS_PRODUCTION:
      # ─────────────────────────────────────────────
      # PERSONA COLUMNS (idempotent)
      # ─────────────────────────────────────────────
      alter_statements = [
        "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS persona VARCHAR(50)",
        "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS persona_confidence INTEGER",
        "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS persona_multiplier DECIMAL(3,2) DEFAULT 1.00",
        "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS persona_criteria TEXT",
        "ALTER TABLE contacts ADD COLUMN IF NOT EXISTS persona_date TIMESTAMP",
      ]
      for sql in alter_statements:
        try:
          cursor.execute(sql)
          logger.info(f"✅ {sql}")
        except Exception as e:
          # Log and continue; do not abort schema setup
          logger.info(f"ℹ️ Skipping `{sql}`: {e}")
          
      # ─────────────────────────────────────────────
      # ACTIVITY / SIGNAL TABLES (if not present)
      # ─────────────────────────────────────────────
      try:
        cursor.execute("""
          CREATE TABLE IF NOT EXISTS contact_activities (
            id SERIAL PRIMARY KEY,
            contact_id INTEGER NOT NULL,
            activity_type VARCHAR(50) NOT NULL,
            activity_date TIMESTAMP NOT NULL,
            direction VARCHAR(20),
            subject TEXT,
            notes TEXT,
            outcome VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          )
        """)
        cursor.execute("""
          CREATE TABLE IF NOT EXISTS opportunity_signals (
            id SERIAL PRIMARY KEY,
            contact_id INTEGER NOT NULL,
            signal_type VARCHAR(50) NOT NULL,
            signal_date TIMESTAMP NOT NULL,
            signal_data TEXT,
            urgency_boost INTEGER DEFAULT 0,
            viewed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
          )
        """)
        logger.info("✅ Production activity/signal tables verified")
      except Exception as e:
        logger.warning(f"⚠️ Could not create activity/signal tables: {e}")
        
      # We deliberately do NOT run all the historical ALTERs again in prod.
      logger.info("✅ Production schema verified (minimal, autocommit-safe).")
      return
    
    # ─────────────────────────────────────────────
    # LOCAL (SQLite) – keep light, DB already built
    # ─────────────────────────────────────────────
    logger.info("✅ Local schema assumed up-to-date (SQLite).")
    
  finally:
    try:
      conn.close()
    except Exception:
      pass
      
# ================================================================
# ENRICHMENT HELPERS (Profile Builder)
# ================================================================

def prepare_enrichment_data(contact: dict) -> dict:
    """Clean minimum required fields for enrichment."""
    name = (contact.get('name') or (contact.get('firstname', '') + ' ' + contact.get('lastname', ''))).strip()
    raw_title = contact.get('title') or contact.get('job_title') or ''
    title = raw_title.split(' at ')[0].strip() if ' at ' in raw_title else raw_title[:50].strip()
    company = (contact.get('company') or 'Unknown').strip()
    email = (contact.get('email') or '').strip()
    phone_mobile = (contact.get('phone_mobile') or '').strip()
    phone = (contact.get('phone') or '').strip()
    best_phone = phone_mobile or phone
    linkedin_url = (contact.get('linkedin_url') or '').strip()

    return {
        'name': name,
        'title': title,
        'company': company,
        'email': email,
        'phone': best_phone,
        'phone_mobile': best_phone,
        'linkedin_url': linkedin_url,
        'original_title': raw_title
    }

def build_enrichment_prompt(seed_data: dict) -> str:
    """Build Perplexity research prompt from seed data."""
    name = seed_data.get('name', 'Unknown')
    title = seed_data.get('title', 'Unknown')
    company = seed_data.get('company', 'Unknown')
    email = seed_data.get('email', '')
    phone = seed_data.get('phone', '')
    linkedin_url = seed_data.get('linkedin_url', '')

    prompt = f"Research professional: {name}\nTitle: {title}\nCompany: {company}"
    if email:
        prompt += f"\nEmail: {email}"
    if phone:
        prompt += f"\nPhone: {phone}"
    if linkedin_url:
        prompt += f"\nLinkedIn: {linkedin_url}"
    else:
        prompt += "\nLinkedIn: [searching for LinkedIn profile]"

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

Provide specific examples, dates, and data points where possible."""
    return prompt

# ================================================================
# HEALTH
# ================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'environment': ENVIRONMENT,
        'timestamp': datetime.now().isoformat(),
        'services': {
            'enrichment': enrichment_engine is not None,
            'scoring': SCORING_AVAILABLE,
            'cadence': auto_sequence_engine is not None,
            'database': 'PostgreSQL' if IS_PRODUCTION else 'SQLite'
        }
    })

# ================================================================
# CONTACT ENDPOINTS
# ================================================================

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get contacts with optional enrichment_status filter."""
    try:
        conn = get_db()
        cursor = dict_cursor(conn)
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)

        query = "SELECT * FROM contacts"
        params = []
        if status:
            if IS_PRODUCTION:
                query += " WHERE enrichment_status = %s"
            else:
                query += " WHERE enrichment_status = ?"
            params.append(status)

        if IS_PRODUCTION:
            query += " ORDER BY id DESC LIMIT %s"
        else:
            query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        if IS_PRODUCTION:
            contacts = rows
        else:
            contacts = [dict(r) for r in rows]

        conn.close()
        return jsonify(contacts)
    except Exception as e:
        logger.error(f"Get contacts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id: int):
    """Get a single contact."""
    try:
        conn = get_db()
        cursor = dict_cursor(conn)
        param = '%s' if IS_PRODUCTION else '?'
        cursor.execute(f"SELECT * FROM contacts WHERE id = {param}", (contact_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Contact not found'}), 404
        contact = row if IS_PRODUCTION else dict(row)
        conn.close()
        return jsonify(contact)
    except Exception as e:
        logger.error(f"Get contact error: {e}")
        return jsonify({'error': str(e)}), 500

# ================================================================
# ENRICHMENT PIPELINE (Perplexity + GPT-4)
# ================================================================

@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id: int):
    """
    3-Stage Enrichment:
    1) Perplexity sonar-pro research
    2) GPT-4 structured profile
    3) Save to DB + optional unified scoring
    """
    try:
        if not PERPLEXITY_API_KEY or not OPENAI_API_KEY:
            return jsonify({'success': False, 'error': 'API keys missing'}), 503

        # Load contact
        conn = get_db()
        cursor = dict_cursor(conn)
        param = '%s' if IS_PRODUCTION else '?'
        cursor.execute(f"SELECT * FROM contacts WHERE id = {param}", (contact_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        contact = row if IS_PRODUCTION else dict(row)
        conn.close()

        # Stage 0: seed data
        seed = prepare_enrichment_data(contact)
        logger.info(f"🔍 Enriching {seed['name']} at {seed['company']}")

        # Stage 1: Perplexity
        research_prompt = build_enrichment_prompt(seed)
        p_resp = requests.post(
            'https://api.perplexity.ai/chat/completions',
            headers={
                'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'sonar-pro',
                'messages': [{'role': 'user', 'content': research_prompt}],
                'max_tokens': 2000,
                'temperature': 0.4
            },
            timeout=60
        )
        if p_resp.status_code != 200:
            logger.error(f"Perplexity error {p_resp.status_code}: {p_resp.text}")
            return jsonify({'error': f'Perplexity failed: {p_resp.status_code}'}), 500
        research_content = p_resp.json()['choices'][0]['message']['content']
        logger.info(f"✅ Stage 1 complete ({len(research_content)} chars)")

        # Stage 2: GPT-4 profile synthesis
        gpt_prompt = f"""Based on this research about {seed['name']}:

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

Format as rich, readable text."""
        g_resp = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-4',
                'messages': [{'role': 'user', 'content': gpt_prompt}],
                'max_tokens': 3000,
                'temperature': 0.7
            },
            timeout=60
        )
        if g_resp.status_code != 200:
            logger.error(f"GPT-4 error {g_resp.status_code}: {g_resp.text}")
            return jsonify({'error': f'GPT-4 failed: {g_resp.status_code}'}), 500
        profile_content = g_resp.json()['choices'][0]['message']['content']
        logger.info(f"✅ Stage 2 complete ({len(profile_content)} chars)")

        # Stage 3: Save + score
        ts = datetime.now().isoformat()
        conn = get_db()
        cursor = dict_cursor(conn)
        if IS_PRODUCTION:
            cursor.execute(
                """
                UPDATE contacts
                SET profile_content = %s,
                    enrichment_status = %s,
                    enrichment_date = %s
                WHERE id = %s
                """,
                (profile_content, 'completed', ts, contact_id)
            )
        else:
            cursor.execute(
                """
                UPDATE contacts
                SET profile_content = ?,
                    enrichment_status = ?,
                    enrichment_date = ?
                WHERE id = ?
                """,
                (profile_content, 'completed', ts, contact_id)
            )
        conn.commit()

        scores = None
        if SCORING_AVAILABLE and SCORING_DB_PATH:
            try:
                scorer = UnifiedApexScorer(db_path=SCORING_DB_PATH)
                scores = scorer.score_contact_unified(contact_id, save_to_db=True)
            except Exception as se:
                logger.warning(f"Scoring failed: {se}")

        conn.close()
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'contact_name': seed['name'],
            'status': 'enriched',
            'profile_length': len(profile_content),
            'seed_data': seed,
            'scores': scores,
            'timestamp': ts
        })
    except Exception as e:
        logger.error(f"Enrich error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Enrichment failed', 'details': str(e)}), 500

# ================================================================
# PERSONA CLASSIFICATION ENDPOINT
# ================================================================

@app.route('/api/contacts/<int:contact_id>/classify-persona', methods=['POST'])
def classify_persona(contact_id: int):
    """Classify contact into one of 8 personas."""
    if not PERSONA_AVAILABLE:
        return jsonify({'success': False, 'error': 'Persona engine unavailable'}), 503
    try:
        conn = get_db()
        cursor = dict_cursor(conn)
        param = '%s' if IS_PRODUCTION else '?'
        cursor.execute(f"SELECT * FROM contacts WHERE id = {param}", (contact_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        contact = row if IS_PRODUCTION else dict(row)
        conn.close()

        result = persona_engine.classify_contact(contact)
        conn = get_db()
        cursor = dict_cursor(conn)
        criteria_json = json.dumps(result.get('criteria', []))
        persona = result.get('persona')
        confidence = result.get('confidence_score', 0)
        multiplier = result.get('multiplier', 1.0)
        ts = datetime.now().isoformat()

        if IS_PRODUCTION:
            cursor.execute(
                """
                UPDATE contacts
                SET persona = %s,
                    persona_confidence = %s,
                    persona_multiplier = %s,
                    persona_criteria = %s,
                    persona_date = %s
                WHERE id = %s
                """,
                (persona, confidence, multiplier, criteria_json, ts, contact_id)
            )
        else:
            cursor.execute(
                """
                UPDATE contacts
                SET persona = ?,
                    persona_confidence = ?,
                    persona_multiplier = ?,
                    persona_criteria = ?,
                    persona_date = ?
                WHERE id = ?
                """,
                (persona, confidence, multiplier, criteria_json, ts, contact_id)
            )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'persona': persona,
            'confidence': confidence,
            'multiplier': multiplier,
            'criteria': result.get('criteria', []),
            'timestamp': ts
        })
    except Exception as e:
        logger.error(f"Persona classify error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ================================================================
# DASHBOARD_v1: /api/todays-board (for TodaysBoard.tsx)
# ================================================================

@app.route('/api/todays-board', methods=['GET'])
def todays_board():
    """
    Returns data shaped exactly as TodaysBoardData in TodaysBoard.tsx:
    {
      success, date, time, total_actions, recommendation,
      relationships: { total, urgent_count, warm_count, nurture_count, stable_count, tiers{...} },
      new_prospects: { total, hot_count, qualified_count, potential_count, tiers{...} }
    }
    """
    try:
        conn = get_db()
        cursor = dict_cursor(conn)

        now = datetime.now()
        date_str = now.strftime('%B %d, %Y')
        time_str = now.strftime('%I:%M %p')

        # RELATIONSHIPS: banker / sba_banker / loan_broker / sales_broker / referral_network_other
        cursor.execute("""
            SELECT id, name, email, phone, phone_mobile, company, title,
                   mdcp_score, priority_score, persona, persona_confidence,
                   profile_content, enrichment_status
            FROM contacts
            WHERE persona IN ('banker','sba_banker','loan_broker','sales_broker','referral_network_other')
            ORDER BY COALESCE(mdcp_score, priority_score, 0) DESC
            LIMIT 50
        """)
        rel_rows = cursor.fetchall()
        if IS_PRODUCTION:
            rel_contacts_raw = rel_rows
        else:
            rel_contacts_raw = [dict(r) for r in rel_rows]

        rel_tiers = {'urgent': [], 'warm': [], 'nurture': [], 'stable': []}
        rel_counts = {'urgent': 0, 'warm': 0, 'nurture': 0, 'stable': 0}

        for r in rel_contacts_raw:
            c = dict(r)
            phone = c.get('phone') or c.get('phone_mobile') or ''
            c['phone'] = phone
            score = float(c.get('mdcp_score') or c.get('priority_score') or 0)
            if score >= 80:
                tier = 'urgent'
            elif score >= 60:
                tier = 'warm'
            elif score >= 40:
                tier = 'nurture'
            else:
                tier = 'stable'
            rel_counts[tier] += 1

            c['mdcp_score'] = score
            c['urgency_tier'] = tier
            c['urgency_label'] = tier.capitalize()
            c['urgency_message'] = f"Score {score:.0f} – {c.get('persona', 'Relationship')}"
            c['why_now'] = "High-value relationship; stay top-of-mind."
            c['days_since_contact'] = 7  # stub; later from contact_activities
            c['contact_type'] = 'relationship'
            c['apex_urgency'] = score

            # Only keep top 5 per tier for UI
            if len(rel_tiers[tier]) < 5:
                rel_tiers[tier].append(c)

        relationships = {
            'total': len(rel_contacts_raw),
            'urgent_count': rel_counts['urgent'],
            'warm_count': rel_counts['warm'],
            'nurture_count': rel_counts['nurture'],
            'stable_count': rel_counts['stable'],
            'tiers': rel_tiers
        }

        # NEW PROSPECTS: borrower / past_borrower / NULL persona
        cursor.execute("""
            SELECT id, name, email, phone, phone_mobile, company, title,
                   mdcp_score, priority_score, persona, persona_confidence
            FROM contacts
            WHERE persona IN ('borrower','past_borrower') OR persona IS NULL
            ORDER BY COALESCE(mdcp_score, priority_score, 0) DESC
            LIMIT 50
        """)
        p_rows = cursor.fetchall()
        if IS_PRODUCTION:
            prospects_raw = p_rows
        else:
            prospects_raw = [dict(r) for r in p_rows]

        prospect_tiers = {'hot': [], 'qualified': [], 'potential': []}
        prospect_counts = {'hot': 0, 'qualified': 0, 'potential': 0}

        for r in prospects_raw:
            c = dict(r)
            phone = c.get('phone') or c.get('phone_mobile') or ''
            c['phone'] = phone
            score = float(c.get('mdcp_score') or c.get('priority_score') or 0)
            if score >= 80:
                tier = 'hot'
            elif score >= 60:
                tier = 'qualified'
            else:
                tier = 'potential'
            prospect_counts[tier] += 1

            c['mdcp_score'] = score
            c['urgency_tier'] = {
                'hot': 'hot_prospect',
                'qualified': 'qualified_prospect',
                'potential': 'potential_prospect'
            }[tier]
            c['urgency_label'] = tier.capitalize()
            c['urgency_message'] = f"Score {score:.0f} – {c.get('persona') or 'Prospect'}"
            c['why_now'] = "High-intent borrower opportunity."
            c['days_since_contact'] = 999
            c['contact_type'] = 'prospect'
            c['apex_urgency'] = score

            if len(prospect_tiers[tier]) < 5:
                prospect_tiers[tier].append(c)

        new_prospects = {
            'total': len(prospects_raw),
            'hot_count': prospect_counts['hot'],
            'qualified_count': prospect_counts['qualified'],
            'potential_count': prospect_counts['potential'],
            'tiers': prospect_tiers
        }

        total_actions = (
            relationships['urgent_count'] +
            relationships['warm_count'] +
            new_prospects['hot_count'] +
            new_prospects['qualified_count']
        ) or 0

        recommendation = (
            "Start with urgent relationship bankers and SBA partners, then move to hot and qualified borrower prospects."
        )

        conn.close()
        return jsonify({
            'success': True,
            'date': date_str,
            'time': time_str,
            'total_actions': total_actions,
            'recommendation': recommendation,
            'relationships': relationships,
            'new_prospects': new_prospects
        })
    except Exception as e:
        logger.error(f"/api/todays-board error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ================================================================
# RUN SERVER
# ================================================================

if __name__ == '__main__':
    ensure_schema()
    port = int(os.getenv('PORT', PORT))
    logger.info(f'🚀 Server starting on port {port}')
    logger.info(f'🔧 Environment: {ENVIRONMENT}')
    logger.info(f'✅ Enrichment engine: {enrichment_engine is not None}')
    logger.info(f'✅ Scoring available: {SCORING_AVAILABLE}')
    app.run(host='0.0.0.0', port=port, debug=True)
  