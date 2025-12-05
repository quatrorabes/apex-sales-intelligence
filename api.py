"""
APEX Sales Intelligence API
Railway-compatible deployment
"""
import os
import sys

# Get port from environment (Railway sets this)
PORT = int(os.environ.get('PORT', 8000))

- Cold Call Queue
- User Profile Management
=============================================================================
"""

import os
import sys
import json
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import sqlite3
from dotenv import load_dotenv
import requests
import logging
import traceback
from openai import OpenAI

# ============= SETUP =============
load_dotenv('/Users/chrisrabenold/projects/apex/.env')

# Add paths for modules
sys.path.insert(0, '/Users/chrisrabenold/projects/apex/apps/backend/intelligence/scoring')
sys.path.insert(0, '/Users/chrisrabenold/projects/apex/apps/backend/intelligence/why_me')
sys.path.insert(0, '/Users/chrisrabenold/projects/apex/apps/backend/intelligence/cold_call')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logger.info(f"Perplexity Key: {'✅' if PERPLEXITY_API_KEY else '❌'}")
logger.info(f"OpenAI Key: {'✅' if OPENAI_API_KEY else '❌'}")

DATABASE = '/Users/chrisrabenold/projects/apex/apex.db'
PORT = 8000

# ============= IMPORT MODULES =============
try:
    from scoring_engine import ApexScoringEngine
    SCORING_AVAILABLE = True
    logger.info("✅ Scoring Engine loaded")
except Exception as e:
    logger.warning(f"⚠️ Scoring Engine not available: {e}")
    SCORING_AVAILABLE = False

try:
    from why_me_engine import WhyMeEngine
    WHY_ME_AVAILABLE = True
    logger.info("✅ Why Me Engine loaded")
except Exception as e:
    logger.warning(f"⚠️ Why Me Engine not available: {e}")
    WHY_ME_AVAILABLE = False

try:
    from cold_call_engine import ColdCallEngine
    COLD_CALL_AVAILABLE = True
    logger.info("✅ Cold Call Engine loaded")
except Exception as e:
    logger.warning(f"⚠️ Cold Call Engine not available: {e}")
    COLD_CALL_AVAILABLE = False


# ============= DATABASE =============
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables():
    """Ensure all required tables and columns exist."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Contact columns
    contact_cols = [
        ('mdcp_score', 'REAL'), ('mdcp_tier', 'TEXT'),
        ('match_score', 'REAL'), ('match_tier', 'TEXT'),
        ('fit_score', 'REAL'), ('relevance_score', 'REAL'), ('timing_score', 'REAL'),
        ('enrichment_status', 'TEXT'), ('enrichment_data', 'TEXT'),
        ('enriched', 'INTEGER'), ('enriched_at', 'TEXT'), ('last_scored', 'TEXT'),
        ('why_me_data', 'TEXT'), ('why_me_generated_at', 'TEXT'),
    ]
    for col, typ in contact_cols:
        try:
            cursor.execute(f'ALTER TABLE contacts ADD COLUMN {col} {typ}')
        except:
            pass
    
    # User profile table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL DEFAULT 'default',
            full_name TEXT,
            role TEXT,
            company TEXT,
            years_experience INTEGER,
            geographic_markets TEXT,
            primary_product TEXT,
            products_services TEXT,
            sweet_spot_min INTEGER,
            sweet_spot_max INTEGER,
            asset_types TEXT,
            loan_types TEXT,
            differentiators TEXT,
            speed_advantage TEXT,
            relationship_advantage TEXT,
            specialization TEXT,
            ideal_titles TEXT,
            ideal_company_types TEXT,
            ideal_deal_triggers TEXT,
            avoid_titles TEXT,
            avoid_company_types TEXT,
            weight_title_match INTEGER DEFAULT 30,
            weight_company_match INTEGER DEFAULT 25,
            weight_deal_size_match INTEGER DEFAULT 20,
            weight_geography_match INTEGER DEFAULT 15,
            weight_timing INTEGER DEFAULT 10,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Proof points table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proof_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'default',
            deals_closed_12mo INTEGER,
            total_volume_12mo REAL,
            avg_close_days INTEGER,
            approval_rate REAL,
            notable_deals TEXT,
            testimonials TEXT,
            awards TEXT,
            certifications TEXT,
            lender_relationships TEXT,
            exclusive_programs TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Cold call queue table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cold_call_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'default',
            name TEXT NOT NULL,
            phone TEXT,
            mobile TEXT,
            email TEXT,
            linkedin_url TEXT,
            company TEXT,
            title TEXT,
            source TEXT,
            source_context TEXT,
            notes TEXT,
            quick_fit_score REAL,
            quick_fit_reason TEXT,
            priority INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',
            attempts INTEGER DEFAULT 0,
            last_attempt TEXT,
            outcome TEXT,
            contact_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Contact match table (for Why Me data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_match (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            user_id TEXT NOT NULL DEFAULT 'default',
            match_score REAL,
            fit_score REAL,
            relevance_score REAL,
            timing_score REAL,
            match_tier TEXT,
            hook TEXT,
            proof_points_matched TEXT,
            why_now TEXT,
            suggested_opening TEXT,
            talking_points TEXT,
            objection_handlers TEXT,
            connection_angles TEXT,
            generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(contact_id, user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

ensure_tables()


# ============= ENRICHMENT ENGINE =============
class EnhancedEnrichment:
    def __init__(self):
        self.perplexity_key = PERPLEXITY_API_KEY
        self.openai_key = OPENAI_API_KEY
        self.output_dir = '/Users/chrisrabenold/projects/apex/enrichment_profiles'
        if not self.perplexity_key:
            raise ValueError("Missing Perplexity API key")
        os.makedirs(self.output_dir, exist_ok=True)

    def enrich_contact(self, contact: dict) -> dict:
        try:
            return self.build_profile(contact)
        except Exception as e:
            logger.error(f"❌ Enrichment failed: {e}")
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def build_profile(self, contact: dict) -> dict:
        name = contact.get('name') or f"{contact.get('firstname', '')} {contact.get('lastname', '')}".strip()
        title = contact.get('title', '')
        company = contact.get('company', '')

        logger.info(f"🔍 ENRICHING: {name} at {company}")

        # PERSON RESEARCH
        person_query = f"""Research {name}, {title} at {company}.
Find: Current role, career history, education, achievements, LinkedIn activity, speaking engagements, board positions, management style."""
        person = self.call_perplexity(person_query)

        # COMPANY RESEARCH
        company_query = f"""Research {company} as a business.
Find: Overview, founding, HQ, employees, revenue, business model, products/services, target markets, competitors, recent news, culture, leadership."""
        company_res = self.call_perplexity(company_query)

        # SALES INTELLIGENCE
        sales_query = f"""Sales opportunity analysis for {name}, {title} at {company}.
Find: Industry trends, pain points, regulatory challenges, technology trends, buying triggers, budget cycles, competitive pressures."""
        sales = self.call_perplexity(sales_query)

        combined = f"""=== PERSON RESEARCH: {name} ===

{person or 'No data available'}

=== COMPANY RESEARCH: {company} ===

{company_res or 'No data available'}

=== SALES INTELLIGENCE ===

{sales or 'No data available'}
"""

        # PERSONALITY ANALYSIS
        personality = self.get_personality_analysis(combined, name, title, company)
        final = combined + "\n\n" + (personality or '')

        # Save
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.output_dir}/profile_{contact.get('id', 'unknown')}_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"# Profile: {name}\n# Generated: {timestamp}\n")
                f.write("=" * 80 + "\n\n")
                f.write(final)
        except:
            pass

        return {'success': True, 'profile_text': final, 'character_count': len(final)}

    def call_perplexity(self, query: str) -> str:
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={"Authorization": f"Bearer {self.perplexity_key}", "Content-Type": "application/json"},
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "system", "content": "Professional research analyst. Be thorough and factual."},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.1
                },
                timeout=90
            )
            if response.status_code == 200:
                return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
            return None
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            return None

    def get_personality_analysis(self, research: str, name: str, title: str, company: str) -> str:
        if not self.openai_key:
            return None
        prompt = f"""Based on research about {name}, {title} at {company}, provide personality analysis:

RESEARCH:
{research[:8000]}

Provide:
=== PERSONALITY ANALYSIS ===

## Myers-Briggs (MBTI) Assessment
**Inferred Type:** [XXXX]
**Confidence:** [High/Medium/Low]

## DISC Profile Assessment
**Primary Style:** [D/I/S/C] - [Name]
**Secondary Style:** [D/I/S/C] - [Name]

## Communication Playbook
### ✅ DO: How to Engage
### ❌ DON'T: What to Avoid
### 🎯 Best Opening Approach"""

        try:
            client = OpenAI(api_key=self.openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Expert personality analyst."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GPT error: {e}")
            return None


# ============= FLASK APP =============
app = Flask(__name__)
CORS(app)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'modules': {
            'scoring': SCORING_AVAILABLE,
            'why_me': WHY_ME_AVAILABLE,
            'cold_call': COLD_CALL_AVAILABLE,
        }
    })


# ============= CONTACTS =============
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    conn = get_db()
    cursor = conn.cursor()
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    cursor.execute('SELECT * FROM contacts ORDER BY match_score DESC NULLS LAST, id DESC LIMIT ? OFFSET ?', (limit, offset))
    contacts = [dict(row) for row in cursor.fetchall()]
    cursor.execute('SELECT COUNT(*) FROM contacts')
    total = cursor.fetchone()[0]
    conn.close()
    return jsonify({'contacts': contacts, 'total': total})


@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
    contact = cursor.fetchone()
    conn.close()
    if contact:
        return jsonify(dict(contact))
    return jsonify({'error': 'Not found'}), 404


# ============= ENRICHMENT =============
@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "Not found"}), 404

        contact = dict(row)
        cursor.execute("UPDATE contacts SET enrichment_status = 'processing' WHERE id = ?", (contact_id,))
        conn.commit()
        conn.close()

        enricher = EnhancedEnrichment()
        result = enricher.enrich_contact(contact)

        if result and result.get('success'):
            profile_text = result['profile_text']

            # Score with new engine
            scores = {}
            if SCORING_AVAILABLE:
                engine = ApexScoringEngine()
                scores = engine.score_contact(contact, profile_text)

            conn = get_db()
            conn.execute("""
                UPDATE contacts SET
                    enrichment_data = ?,
                    enriched = 1,
                    enriched_at = ?,
                    enrichment_status = 'completed',
                    match_score = ?,
                    match_tier = ?,
                    fit_score = ?,
                    relevance_score = ?,
                    timing_score = ?,
                    last_scored = ?
                WHERE id = ?
            """, (
                profile_text,
                datetime.now().isoformat(),
                scores.get('match_score'),
                scores.get('match_tier'),
                scores.get('fit_score'),
                scores.get('relevance_score'),
                scores.get('timing_score'),
                datetime.now().isoformat(),
                contact_id
            ))
            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'contact_id': contact_id,
                'profile_length': result['character_count'],
                'scores': scores
            })
        else:
            conn = get_db()
            conn.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = ?", (contact_id,))
            conn.commit()
            conn.close()
            return jsonify({'error': result.get('error', 'Failed')}), 500

    except Exception as e:
        logger.error(f"Enrichment error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>/enrichment-status', methods=['GET'])
def get_enrichment_status(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT enrichment_status, enriched_at FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'status': row['enrichment_status'] or 'pending', 'last_enriched': row['enriched_at']})


# ============= SCORING =============
@app.route('/api/contacts/<int:contact_id>/score', methods=['POST'])
def score_contact(contact_id):
    if not SCORING_AVAILABLE:
        return jsonify({'error': 'Scoring not available'}), 503

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404

    contact = dict(row)
    enrichment = contact.get('enrichment_data') or ''

    engine = ApexScoringEngine()
    scores = engine.score_contact(contact, enrichment)

    conn.execute("""
        UPDATE contacts SET
            match_score = ?, match_tier = ?,
            fit_score = ?, relevance_score = ?, timing_score = ?,
            last_scored = ?
        WHERE id = ?
    """, (
        scores.get('match_score'), scores.get('match_tier'),
        scores.get('fit_score'), scores.get('relevance_score'), scores.get('timing_score'),
        datetime.now().isoformat(), contact_id
    ))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'scores': scores})


# ============= WHY ME =============
@app.route('/api/contacts/<int:contact_id>/why-me', methods=['GET'])
def get_why_me(contact_id):
    """Get existing Why Me data for a contact."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contact_match WHERE contact_id = ?", (contact_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Not generated yet'}), 404


@app.route('/api/contacts/<int:contact_id>/why-me', methods=['POST'])
def generate_why_me(contact_id):
    """Generate Why Me content for a contact."""
    if not WHY_ME_AVAILABLE:
        return jsonify({'error': 'Why Me engine not available'}), 503

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Not found'}), 404

    contact = dict(row)
    enrichment = contact.get('enrichment_data') or ''
    conn.close()

    engine = WhyMeEngine()
    result = engine.generate(contact, enrichment)
    engine.save_to_db(contact_id, result)

    return jsonify({'success': True, 'why_me': result})


# ============= COLD CALL QUEUE =============
@app.route('/api/cold-call/queue', methods=['GET'])
def get_cold_queue():
    if not COLD_CALL_AVAILABLE:
        return jsonify({'error': 'Cold call engine not available'}), 503

    limit = request.args.get('limit', 50, type=int)
    status = request.args.get('status')

    engine = ColdCallEngine()
    queue = engine.get_prioritized_queue(limit=limit, status=status)
    stats = engine.get_queue_stats()

    return jsonify({'queue': queue, 'stats': stats})


@app.route('/api/cold-call/queue', methods=['POST'])
def add_to_cold_queue():
    if not COLD_CALL_AVAILABLE:
        return jsonify({'error': 'Cold call engine not available'}), 503

    data = request.json
    engine = ColdCallEngine()

    # Single or batch add
    if isinstance(data, list):
        result = engine.add_batch(data)
    else:
        result = engine.add_to_queue(
            name=data.get('name'),
            phone=data.get('phone'),
            mobile=data.get('mobile'),
            email=data.get('email'),
            linkedin_url=data.get('linkedin_url'),
            company=data.get('company'),
            title=data.get('title'),
            source=data.get('source', 'manual'),
            source_context=data.get('source_context'),
            notes=data.get('notes')
        )

    return jsonify(result)


@app.route('/api/cold-call/queue/<int:queue_id>/attempt', methods=['POST'])
def log_cold_attempt(queue_id):
    if not COLD_CALL_AVAILABLE:
        return jsonify({'error': 'Cold call engine not available'}), 503

    data = request.json or {}
    engine = ColdCallEngine()
    engine.log_attempt(queue_id, outcome=data.get('outcome'), notes=data.get('notes'))

    return jsonify({'success': True})


@app.route('/api/cold-call/queue/<int:queue_id>/status', methods=['PUT'])
def update_cold_status(queue_id):
    if not COLD_CALL_AVAILABLE:
        return jsonify({'error': 'Cold call engine not available'}), 503

    data = request.json
    engine = ColdCallEngine()
    engine.update_status(queue_id, data.get('status'), notes=data.get('notes'))

    return jsonify({'success': True})


@app.route('/api/cold-call/queue/<int:queue_id>/promote', methods=['POST'])
def promote_cold_contact(queue_id):
    if not COLD_CALL_AVAILABLE:
        return jsonify({'error': 'Cold call engine not available'}), 503

    engine = ColdCallEngine()
    result = engine.promote_to_contact(queue_id)

    return jsonify(result)


# ============= USER PROFILE =============
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    user_id = request.args.get('user_id', 'default')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify(dict(row))
    return jsonify({'user_id': user_id, 'exists': False})


@app.route('/api/user/profile', methods=['POST', 'PUT'])
def save_user_profile():
    data = request.json
    user_id = data.get('user_id', 'default')

    conn = get_db()
    cursor = conn.cursor()

    # Convert lists to JSON strings
    json_fields = ['geographic_markets', 'products_services', 'asset_types', 'loan_types',
                   'ideal_titles', 'ideal_company_types', 'ideal_deal_triggers',
                   'avoid_titles', 'avoid_company_types']

    for field in json_fields:
        if field in data and isinstance(data[field], list):
            data[field] = json.dumps(data[field])

    cursor.execute('''
        INSERT OR REPLACE INTO user_profile 
        (user_id, full_name, role, company, years_experience, geographic_markets,
         primary_product, products_services, sweet_spot_min, sweet_spot_max,
         asset_types, loan_types, differentiators, speed_advantage, 
         relationship_advantage, specialization, ideal_titles, ideal_company_types,
         ideal_deal_triggers, avoid_titles, avoid_company_types,
         weight_title_match, weight_company_match, weight_deal_size_match,
         weight_geography_match, weight_timing, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data.get('full_name'),
        data.get('role'),
        data.get('company'),
        data.get('years_experience'),
        data.get('geographic_markets'),
        data.get('primary_product'),
        data.get('products_services'),
        data.get('sweet_spot_min'),
        data.get('sweet_spot_max'),
        data.get('asset_types'),
        data.get('loan_types'),
        data.get('differentiators'),
        data.get('speed_advantage'),
        data.get('relationship_advantage'),
        data.get('specialization'),
        data.get('ideal_titles'),
        data.get('ideal_company_types'),
        data.get('ideal_deal_triggers'),
        data.get('avoid_titles'),
        data.get('avoid_company_types'),
        data.get('weight_title_match', 30),
        data.get('weight_company_match', 25),
        data.get('weight_deal_size_match', 20),
        data.get('weight_geography_match', 15),
        data.get('weight_timing', 10),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'user_id': user_id})


@app.route('/api/user/proof-points', methods=['GET'])
def get_proof_points():
    user_id = request.args.get('user_id', 'default')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proof_points WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify(dict(row))
    return jsonify({'user_id': user_id, 'exists': False})


@app.route('/api/user/proof-points', methods=['POST', 'PUT'])
def save_proof_points():
    data = request.json
    user_id = data.get('user_id', 'default')

    # Convert lists to JSON
    json_fields = ['notable_deals', 'testimonials', 'awards', 'certifications',
                   'lender_relationships', 'exclusive_programs']
    for field in json_fields:
        if field in data and isinstance(data[field], list):
            data[field] = json.dumps(data[field])

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO proof_points
        (user_id, deals_closed_12mo, total_volume_12mo, avg_close_days, approval_rate,
         notable_deals, testimonials, awards, certifications, lender_relationships,
         exclusive_programs, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data.get('deals_closed_12mo'),
        data.get('total_volume_12mo'),
        data.get('avg_close_days'),
        data.get('approval_rate'),
        data.get('notable_deals'),
        data.get('testimonials'),
        data.get('awards'),
        data.get('certifications'),
        data.get('lender_relationships'),
        data.get('exclusive_programs'),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'user_id': user_id})


# ============= TODAY'S BOARD =============
@app.route('/api/todays-board', methods=['GET'])
def get_todays_board():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, phone, company, title,
               match_score, match_tier, fit_score, relevance_score, timing_score,
               enrichment_status, enriched_at
        FROM contacts
        WHERE match_score IS NOT NULL OR enrichment_status = 'completed'
        ORDER BY match_score DESC NULLS LAST
        LIMIT 100
    """)
    contacts = [dict(row) for row in cursor.fetchall()]

    # Stats
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'completed'")
    enriched = cursor.fetchone()[0]

    # Cold call stats
    cold_stats = {}
    if COLD_CALL_AVAILABLE:
        engine = ColdCallEngine()
        cold_stats = engine.get_queue_stats()

    conn.close()

    high = [c for c in contacts if c.get('match_tier') == 'HIGH']
    medium = [c for c in contacts if c.get('match_tier') == 'MEDIUM']
    low = [c for c in contacts if c.get('match_tier') == 'LOW']

    return jsonify({
        'success': True,
        'date': datetime.now().strftime('%B %d, %Y'),
        'time': datetime.now().strftime('%I:%M %p'),
        'stats': {
            'total_contacts': total,
            'enriched': enriched,
            'high_match': len(high),
            'medium_match': len(medium),
            'low_match': len(low),
            'cold_call_queue': cold_stats.get('total', 0),
        },
        'segments': {
            'high': high[:12],
            'medium': medium[:12],
            'low': low[:12],
        },
        'top_priority': contacts[:20],
        'cold_call_stats': cold_stats,
    })


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 APEX API SERVER v4.0")
    logger.info("=" * 60)
    logger.info(f"📊 Database: {DATABASE}")
    logger.info(f"🔌 Port: {PORT}")
    logger.info(f"🧠 Modules: Scoring={SCORING_AVAILABLE}, WhyMe={WHY_ME_AVAILABLE}, ColdCall={COLD_CALL_AVAILABLE}")
    logger.info("=" * 60)


# ============= EMAIL GENERATION =============
try:
    sys.path.insert(0, '/Users/chrisrabenold/projects/apex/apps/backend/intelligence/outreach')
    from email_generator import EmailGenerator
    EMAIL_AVAILABLE = True
    logger.info("✅ Email Generator loaded")
except Exception as e:
    logger.warning(f"⚠️ Email Generator not available: {e}")
    EMAIL_AVAILABLE = False


@app.route('/api/contacts/<int:contact_id>/generate-email', methods=['POST'])
def generate_email_endpoint(contact_id):
    """Generate personalized email draft."""
    if not EMAIL_AVAILABLE:
        return jsonify({'error': 'Email generator not available'}), 503
    
    data = request.json or {}
    template = data.get('template', 'intro')
    custom_context = data.get('context', '')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Contact not found'}), 404
    
    contact = dict(row)
    enrichment = contact.get('enrichment_data') or ''
    
    # Get Why Me data if exists
    cursor.execute("SELECT * FROM contact_match WHERE contact_id = ?", (contact_id,))
    match_row = cursor.fetchone()
    conn.close()
    
    why_me_data = dict(match_row) if match_row else None
    
    generator = EmailGenerator()
    result = generator.generate_email(contact, enrichment, why_me_data, template, custom_context)
    
    return jsonify({'success': True, 'email': result})


@app.route('/api/contacts/<int:contact_id>/generate-sequence', methods=['POST'])
def generate_sequence_endpoint(contact_id):
    """Generate 3-email sequence."""
    if not EMAIL_AVAILABLE:
        return jsonify({'error': 'Email generator not available'}), 503
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Contact not found'}), 404
    
    contact = dict(row)
    enrichment = contact.get('enrichment_data') or ''
    
    cursor.execute("SELECT * FROM contact_match WHERE contact_id = ?", (contact_id,))
    match_row = cursor.fetchone()
    conn.close()
    
    why_me_data = dict(match_row) if match_row else None
    
    generator = EmailGenerator()
    sequence = generator.generate_sequence(contact, enrichment, why_me_data)
    
    return jsonify({'success': True, 'sequence': sequence})


@app.route('/api/email-templates', methods=['GET'])
def get_email_templates():
    """Get available email templates."""
    if not EMAIL_AVAILABLE:
        return jsonify({'error': 'Email generator not available'}), 503
    
    return jsonify({'templates': EmailGenerator.TEMPLATES})


# ============= ANALYTICS =============
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get pipeline analytics."""
    time_range = request.args.get('range', 'all')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Total contacts
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total_contacts = cursor.fetchone()[0]
    
    # Enriched contacts
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'completed'")
    enriched_contacts = cursor.fetchone()[0]
    
    # Scored contacts
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE match_score IS NOT NULL")
    scored_contacts = cursor.fetchone()[0]
    
    # Tier distribution
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN match_tier = 'HIGH' THEN 1 ELSE 0 END) as high,
            SUM(CASE WHEN match_tier = 'MEDIUM' THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN match_tier = 'LOW' THEN 1 ELSE 0 END) as low,
            SUM(CASE WHEN match_tier = 'MINIMAL' OR match_tier IS NULL THEN 1 ELSE 0 END) as minimal
        FROM contacts WHERE match_score IS NOT NULL
    """)
    tier_row = cursor.fetchone()
    tier_distribution = {
        'HIGH': tier_row[0] or 0,
        'MEDIUM': tier_row[1] or 0,
        'LOW': tier_row[2] or 0,
        'MINIMAL': tier_row[3] or 0,
    }
    
    # Average scores
    cursor.execute("""
        SELECT 
            AVG(match_score) as match,
            AVG(fit_score) as fit,
            AVG(relevance_score) as relevance,
            AVG(timing_score) as timing
        FROM contacts WHERE match_score IS NOT NULL
    """)
    avg_row = cursor.fetchone()
    avg_scores = {
        'match': avg_row[0] or 0,
        'fit': avg_row[1] or 0,
        'relevance': avg_row[2] or 0,
        'timing': avg_row[3] or 0,
    }
    
    # Top companies
    cursor.execute("""
        SELECT company, COUNT(*) as cnt, AVG(match_score) as avg_score
        FROM contacts 
        WHERE company IS NOT NULL AND company != ''
        GROUP BY company 
        ORDER BY cnt DESC 
        LIMIT 10
    """)
    top_companies = [{'company': r[0], 'count': r[1], 'avg_score': r[2]} for r in cursor.fetchall()]
    
    # Cold call stats
    cold_stats = {'total': 0, 'new': 0, 'attempted': 0, 'connected': 0, 'meeting_set': 0, 'conversion_rate': 0}
    try:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new,
                SUM(CASE WHEN status = 'attempted' THEN 1 ELSE 0 END) as attempted,
                SUM(CASE WHEN status = 'connected' THEN 1 ELSE 0 END) as connected,
                SUM(CASE WHEN status = 'meeting_set' THEN 1 ELSE 0 END) as meeting_set
            FROM cold_call_queue
        """)
        cc_row = cursor.fetchone()
        if cc_row:
            cold_stats = {
                'total': cc_row[0] or 0,
                'new': cc_row[1] or 0,
                'attempted': cc_row[2] or 0,
                'connected': cc_row[3] or 0,
                'meeting_set': cc_row[4] or 0,
            }
            attempted = cold_stats['attempted'] + cold_stats['connected'] + cold_stats['meeting_set']
            cold_stats['conversion_rate'] = (cold_stats['meeting_set'] / attempted * 100) if attempted > 0 else 0
    except:
        pass
    
    conn.close()
    
    enrichment_rate = (enriched_contacts / total_contacts * 100) if total_contacts > 0 else 0
    
    return jsonify({
        'total_contacts': total_contacts,
        'enriched_contacts': enriched_contacts,
        'scored_contacts': scored_contacts,
        'tier_distribution': tier_distribution,
        'avg_scores': avg_scores,
        'enrichment_rate': enrichment_rate,
        'top_companies': top_companies,
        'cold_call_stats': cold_stats,
        'recent_activity': [],
    })


# ============= LINKEDIN MESSAGES =============
try:
    from linkedin_generator import LinkedInGenerator
    LINKEDIN_AVAILABLE = True
    logger.info("✅ LinkedIn Generator loaded")
except Exception as e:
    logger.warning(f"⚠️ LinkedIn Generator not available: {e}")
    LINKEDIN_AVAILABLE = False


@app.route('/api/contacts/<int:contact_id>/generate-linkedin', methods=['POST'])
def generate_linkedin_endpoint(contact_id):
    """Generate LinkedIn message."""
    if not LINKEDIN_AVAILABLE:
        return jsonify({'error': 'LinkedIn generator not available'}), 503
    
    data = request.json or {}
    template = data.get('template', 'connection')
    custom_context = data.get('context', '')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Contact not found'}), 404
    
    contact = dict(row)
    enrichment = contact.get('enrichment_data') or ''
    
    cursor.execute("SELECT * FROM contact_match WHERE contact_id = ?", (contact_id,))
    match_row = cursor.fetchone()
    conn.close()
    
    why_me_data = dict(match_row) if match_row else None
    
    generator = LinkedInGenerator()
    result = generator.generate(contact, enrichment, why_me_data, template, custom_context)
    
    return jsonify({'success': True, 'linkedin': result})


@app.route('/api/linkedin-templates', methods=['GET'])
def get_linkedin_templates():
    """Get available LinkedIn templates."""
    return jsonify({'templates': LinkedInGenerator.TEMPLATES if LINKEDIN_AVAILABLE else {}})


# ============= SMART LISTS =============
@app.route('/api/smart-lists', methods=['GET'])
def get_smart_lists():
    """Get smart list definitions and counts."""
    conn = get_db()
    cursor = conn.cursor()
    
    lists = []
    
    # Hot Leads (HIGH tier, enriched recently)
    cursor.execute("""
        SELECT COUNT(*) FROM contacts 
        WHERE match_tier = 'HIGH' AND enrichment_status = 'completed'
    """)
    lists.append({
        'id': 'hot_leads',
        'name': 'Hot Leads',
        'description': 'High match score, enriched and ready',
        'icon': 'flame',
        'color': 'red',
        'count': cursor.fetchone()[0],
        'filter': {'match_tier': 'HIGH', 'enrichment_status': 'completed'}
    })
    
    # Ready to Contact (enriched, has phone or email)
    cursor.execute("""
        SELECT COUNT(*) FROM contacts 
        WHERE enrichment_status = 'completed' 
        AND (phone IS NOT NULL OR email IS NOT NULL)
        AND match_score >= 50
    """)
    lists.append({
        'id': 'ready_to_contact',
        'name': 'Ready to Contact',
        'description': 'Has contact info, scored 50+',
        'icon': 'phone',
        'color': 'green',
        'count': cursor.fetchone()[0],
        'filter': {'enrichment_status': 'completed', 'min_score': 50, 'has_contact': True}
    })
    
    # Needs Enrichment (not enriched yet)
    cursor.execute("""
        SELECT COUNT(*) FROM contacts 
        WHERE enrichment_status IS NULL OR enrichment_status = 'pending'
    """)
    lists.append({
        'id': 'needs_enrichment',
        'name': 'Needs Enrichment',
        'description': 'Not yet enriched',
        'icon': 'zap',
        'color': 'yellow',
        'count': cursor.fetchone()[0],
        'filter': {'enrichment_status': ['pending', None]}
    })
    
    # High Fit Low Timing (good fit but no urgency)
    cursor.execute("""
        SELECT COUNT(*) FROM contacts 
        WHERE fit_score >= 70 AND timing_score < 30
    """)
    lists.append({
        'id': 'nurture_list',
        'name': 'Nurture List',
        'description': 'Great fit, needs nurturing (low timing)',
        'icon': 'clock',
        'color': 'blue',
        'count': cursor.fetchone()[0],
        'filter': {'min_fit': 70, 'max_timing': 30}
    })
    
    # Decision Makers (title-based)
    cursor.execute("""
        SELECT COUNT(*) FROM contacts 
        WHERE (lower(title) LIKE '%ceo%' OR lower(title) LIKE '%president%' 
               OR lower(title) LIKE '%owner%' OR lower(title) LIKE '%principal%'
               OR lower(title) LIKE '%managing director%')
        AND enrichment_status = 'completed'
    """)
    lists.append({
        'id': 'decision_makers',
        'name': 'Decision Makers',
        'description': 'C-suite and principals',
        'icon': 'crown',
        'color': 'purple',
        'count': cursor.fetchone()[0],
        'filter': {'title_contains': ['ceo', 'president', 'owner', 'principal', 'managing director']}
    })
    
    # Recently Enriched (last 7 days)
    cursor.execute("""
        SELECT COUNT(*) FROM contacts 
        WHERE enriched_at >= datetime('now', '-7 days')
    """)
    lists.append({
        'id': 'recently_enriched',
        'name': 'Recently Enriched',
        'description': 'Enriched in last 7 days',
        'icon': 'sparkles',
        'color': 'cyan',
        'count': cursor.fetchone()[0],
        'filter': {'enriched_since': '7d'}
    })
    
    conn.close()
    
    return jsonify({'lists': lists})


@app.route('/api/smart-lists/<list_id>/contacts', methods=['GET'])
def get_smart_list_contacts(list_id):
    """Get contacts for a smart list."""
    conn = get_db()
    cursor = conn.cursor()
    limit = request.args.get('limit', 50, type=int)
    
    if list_id == 'hot_leads':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE match_tier = 'HIGH' AND enrichment_status = 'completed'
            ORDER BY match_score DESC LIMIT ?
        """, (limit,))
    elif list_id == 'ready_to_contact':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE enrichment_status = 'completed' 
            AND (phone IS NOT NULL OR email IS NOT NULL)
            AND match_score >= 50
            ORDER BY match_score DESC LIMIT ?
        """, (limit,))
    elif list_id == 'needs_enrichment':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE enrichment_status IS NULL OR enrichment_status = 'pending'
            LIMIT ?
        """, (limit,))
    elif list_id == 'nurture_list':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE fit_score >= 70 AND timing_score < 30
            ORDER BY fit_score DESC LIMIT ?
        """, (limit,))
    elif list_id == 'decision_makers':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE (lower(title) LIKE '%ceo%' OR lower(title) LIKE '%president%' 
                   OR lower(title) LIKE '%owner%' OR lower(title) LIKE '%principal%'
                   OR lower(title) LIKE '%managing director%')
            AND enrichment_status = 'completed'
            ORDER BY match_score DESC LIMIT ?
        """, (limit,))
    elif list_id == 'recently_enriched':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE enriched_at >= datetime('now', '-7 days')
            ORDER BY enriched_at DESC LIMIT ?
        """, (limit,))
    else:
        conn.close()
        return jsonify({'error': 'Unknown list'}), 404
    
    contacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'contacts': contacts, 'list_id': list_id, 'count': len(contacts)})


# ============= CONTACT TIER UPDATE =============
@app.route('/api/contacts/<int:contact_id>/tier', methods=['PUT'])
def update_contact_tier(contact_id):
    """Update contact match tier (for drag-drop)."""
    data = request.json or {}
    new_tier = data.get('tier')
    
    if new_tier not in ['HIGH', 'MEDIUM', 'LOW', 'MINIMAL']:
        return jsonify({'error': 'Invalid tier'}), 400
    
    conn = get_db()
    conn.execute("UPDATE contacts SET match_tier = ? WHERE id = ?", (new_tier, contact_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'tier': new_tier})


# ============= AI COMMAND BAR =============
@app.route('/api/ai/command', methods=['POST'])
def ai_command():
    """Process natural language commands."""
    data = request.json or {}
    command = data.get('command', '').lower()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Parse command and execute
    result = {'type': 'insight', 'message': 'Command processed'}
    
    # Contact searches
    if any(word in command for word in ['show', 'find', 'get', 'list']):
        query = "SELECT * FROM contacts WHERE 1=1"
        params = []
        
        # Title filters
        if 'ceo' in command:
            query += " AND lower(title) LIKE '%ceo%'"
        elif 'president' in command:
            query += " AND lower(title) LIKE '%president%'"
        elif 'director' in command:
            query += " AND lower(title) LIKE '%director%'"
        elif 'manager' in command:
            query += " AND lower(title) LIKE '%manager%'"
        elif 'decision maker' in command:
            query += " AND (lower(title) LIKE '%ceo%' OR lower(title) LIKE '%president%' OR lower(title) LIKE '%owner%')"
        
        # Tier filters
        if 'high priority' in command or 'high score' in command:
            query += " AND match_tier = 'HIGH'"
        elif 'top' in command:
            query += " AND match_score IS NOT NULL ORDER BY match_score DESC LIMIT 10"
        
        # Industry/company filters
        if 'bank' in command:
            query += " AND (lower(company) LIKE '%bank%' OR lower(company) LIKE '%capital%')"
        elif 'real estate' in command:
            query += " AND (lower(company) LIKE '%real%' OR lower(company) LIKE '%property%' OR lower(company) LIKE '%realty%')"
        elif 'tech' in command:
            query += " AND (lower(company) LIKE '%tech%' OR lower(company) LIKE '%software%' OR lower(company) LIKE '%digital%')"
        
        if 'ORDER BY' not in query:
            query += " ORDER BY match_score DESC LIMIT 20"
        
        cursor.execute(query, params)
        contacts = [dict(row) for row in cursor.fetchall()]
        
        result = {
            'type': 'contacts',
            'message': f"Found {len(contacts)} matching contacts",
            'data': contacts
        }
    
    # Pipeline health
    elif 'pipeline' in command or 'health' in command:
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN match_tier = 'HIGH' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN enrichment_status = 'completed' THEN 1 ELSE 0 END) as enriched,
                AVG(match_score) as avg_score
            FROM contacts
        """)
        row = cursor.fetchone()
        result = {
            'type': 'insight',
            'message': f"Pipeline: {row['total']} contacts, {row['high']} high priority, {row['enriched']} enriched",
            'data': dict(row)
        }
    
    # Who to call
    elif 'call' in command and ('who' in command or 'should' in command):
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE phone IS NOT NULL AND match_tier = 'HIGH'
            ORDER BY match_score DESC LIMIT 5
        """)
        contacts = [dict(row) for row in cursor.fetchall()]
        result = {
            'type': 'contacts',
            'message': f"Here are your top {len(contacts)} contacts to call today:",
            'data': contacts
        }
    
    conn.close()
    return jsonify(result)


# ============= ACTIVITIES =============
@app.route('/api/contacts/<int:contact_id>/activities', methods=['GET'])
def get_contact_activities(contact_id):
    """Get activity timeline for a contact."""
    conn = get_db()
    cursor = conn.cursor()
    
    activities = []
    
    # Get contact for basic info
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    contact = cursor.fetchone()
    
    if contact:
        contact = dict(contact)
        
        # Enrichment activity
        if contact.get('enriched_at'):
            activities.append({
                'type': 'enrichment',
                'title': 'Contact Enriched',
                'description': 'AI research completed',
                'timestamp': contact['enriched_at'],
            })
        
        # Score activity
        if contact.get('last_scored'):
            activities.append({
                'type': 'score',
                'title': 'Match Score Updated',
                'description': f"Scored {contact.get('match_score', 0):.0f} ({contact.get('match_tier', 'N/A')})",
                'timestamp': contact['last_scored'],
                'metadata': {
                    'score': contact.get('match_score'),
                    'tier': contact.get('match_tier'),
                }
            })
        
        # Created activity
        if contact.get('created_at'):
            activities.append({
                'type': 'status_change',
                'title': 'Contact Added',
                'description': 'Added to pipeline',
                'timestamp': contact['created_at'],
            })
    
    # Sort by timestamp desc
    activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
    
    conn.close()
    return jsonify({'activities': activities})


# ============= MEETING PREP =============
@app.route('/api/contacts/<int:contact_id>/meeting-prep', methods=['POST'])
def generate_meeting_prep(contact_id):
    """Generate meeting prep document."""
    data = request.json or {}
    meeting_type = data.get('meeting_type', 'discovery')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': 'Contact not found'}), 404
    
    contact = dict(row)
    name = contact.get('name') or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
    enrichment = contact.get('enrichment_data') or ''
    
    # If no OpenAI, return structured fallback
    if not os.getenv('OPENAI_API_KEY'):
        return jsonify({'prep': {
            'contact_summary': f"{name} is {contact.get('title', 'a professional')} at {contact.get('company', 'their company')}.",
            'company_overview': f"{contact.get('company', 'The company')} operates in their industry.",
            'talking_points': [
                "Discuss their current challenges",
                "Understand their goals for this year",
                "Share relevant case studies",
            ],
            'questions_to_ask': [
                "What's your biggest priority right now?",
                "How are you currently handling this?",
                "What would success look like?",
            ],
            'potential_objections': [
                {'objection': "We're not looking right now", 'response': "I understand. What would need to change for this to become a priority?"},
                {'objection': "We already have a solution", 'response': "Great! How's that working for you? Any gaps?"},
            ],
            'ice_breakers': ["Recent company news", "Industry trends", "Mutual connections"],
            'goal': f"Schedule a follow-up meeting with {name}",
            'next_steps': ["Send recap email", "Schedule follow-up", "Share relevant materials"],
            'generated_at': datetime.now().isoformat(),
        }})
    
    try:
        from openai import OpenAI
        client = OpenAI()
        
        prompt = f"""Generate a comprehensive meeting prep document for a {meeting_type} call.

CONTACT:
- Name: {name}
- Title: {contact.get('title', '')}
- Company: {contact.get('company', '')}

ENRICHMENT DATA:
{enrichment[:4000]}

Return JSON with these exact keys:
- contact_summary (2-3 sentences about the person)
- company_overview (2-3 sentences about the company)
- talking_points (array of 4-5 key points to discuss)
- questions_to_ask (array of 5-6 discovery questions)
- potential_objections (array of objects with 'objection' and 'response' keys)
- ice_breakers (array of 3-4 conversation starters)
- goal (single sentence meeting objective)
- next_steps (array of 3-4 recommended actions)"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sales meeting prep expert. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        
        prep = json.loads(response.choices[0].message.content)
        prep['generated_at'] = datetime.now().isoformat()
        
        return jsonify({'prep': prep})
        
    except Exception as e:
        logger.error(f"Meeting prep error: {e}")
        return jsonify({'error': str(e)}), 500


# ============= CONTACT IMPORT =============
@app.route('/api/contacts/import', methods=['POST'])
def import_contacts():
    """Bulk import contacts."""
    data = request.json or {}
    contacts = data.get('contacts', [])
    
    if not contacts:
        return jsonify({'error': 'No contacts provided'}), 400
    
    conn = get_db()
    success = 0
    failed = 0
    
    for c in contacts:
        try:
            # Handle name field
            name = c.get('name', '')
            first_name = c.get('first_name', '')
            last_name = c.get('last_name', '')
            
            if not name and not first_name:
                failed += 1
                continue
            
            conn.execute("""
                INSERT INTO contacts (name, first_name, last_name, email, phone, company, title, linkedin_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, first_name, last_name,
                c.get('email'), c.get('phone'), c.get('company'),
                c.get('title'), c.get('linkedin_url'),
                datetime.now().isoformat()
            ))
            success += 1
        except Exception as e:
            logger.error(f"Import error: {e}")
            failed += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': success, 'failed': failed})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    print(f"🚀 Starting APEX API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)


# ============= CRM IMPORT ENDPOINTS =============

@app.route('/api/import/hubspot', methods=['POST'])
def import_hubspot():
    """Import contacts from HubSpot."""
    from apps.backend.integrations.crm_import import HubSpotImporter, ImportManager
    
    data = request.json or {}
    api_key = data.get('api_key') or os.getenv('HUBSPOT_API_KEY')
    access_token = data.get('access_token') or os.getenv('HUBSPOT_ACCESS_TOKEN')
    max_contacts = data.get('limit', 500)
    
    if not api_key and not access_token:
        return jsonify({'error': 'HubSpot API key or access token required'}), 400
    
    try:
        importer = HubSpotImporter(api_key=api_key, access_token=access_token)
        raw_contacts = importer.fetch_all_contacts(max_contacts=max_contacts)
        
        # Normalize contacts
        normalized = [importer.normalize_contact(c) for c in raw_contacts]
        
        # Save to database
        conn = get_db()
        manager = ImportManager(conn)
        result = manager.save_contacts(normalized)
        conn.close()
        
        return jsonify({
            'source': 'hubspot',
            'fetched': len(raw_contacts),
            **result
        })
        
    except Exception as e:
        logger.error(f"HubSpot import error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/import/salesforce', methods=['POST'])
def import_salesforce():
    """Import contacts from Salesforce."""
    from apps.backend.integrations.crm_import import SalesforceImporter, ImportManager
    
    data = request.json or {}
    username = data.get('username') or os.getenv('SALESFORCE_USERNAME')
    password = data.get('password') or os.getenv('SALESFORCE_PASSWORD')
    security_token = data.get('security_token') or os.getenv('SALESFORCE_SECURITY_TOKEN')
    max_contacts = data.get('limit', 500)
    
    if not username or not password:
        return jsonify({'error': 'Salesforce credentials required'}), 400
    
    try:
        importer = SalesforceImporter(
            username=username,
            password=password,
            security_token=security_token
        )
        raw_contacts = importer.fetch_contacts(limit=max_contacts)
        
        # Normalize contacts
        normalized = [importer.normalize_contact(c) for c in raw_contacts]
        
        # Save to database
        conn = get_db()
        manager = ImportManager(conn)
        result = manager.save_contacts(normalized)
        conn.close()
        
        return jsonify({
            'source': 'salesforce',
            'fetched': len(raw_contacts),
            **result
        })
        
    except Exception as e:
        logger.error(f"Salesforce import error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/import/pipedrive', methods=['POST'])
def import_pipedrive():
    """Import contacts from Pipedrive."""
    from apps.backend.integrations.crm_import import PipedriveImporter, ImportManager
    
    data = request.json or {}
    api_token = data.get('api_token') or os.getenv('PIPEDRIVE_API_TOKEN')
    max_contacts = data.get('limit', 500)
    
    if not api_token:
        return jsonify({'error': 'Pipedrive API token required'}), 400
    
    try:
        importer = PipedriveImporter(api_token=api_token)
        raw_contacts = importer.fetch_all_contacts(max_contacts=max_contacts)
        
        # Normalize contacts
        normalized = [importer.normalize_contact(c) for c in raw_contacts]
        
        # Save to database
        conn = get_db()
        manager = ImportManager(conn)
        result = manager.save_contacts(normalized)
        conn.close()
        
        return jsonify({
            'source': 'pipedrive',
            'fetched': len(raw_contacts),
            **result
        })
        
    except Exception as e:
        logger.error(f"Pipedrive import error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/import/csv', methods=['POST'])
def import_csv():
    """Import contacts from CSV."""
    from apps.backend.integrations.crm_import import CSVImporter, ImportManager
    
    data = request.json or {}
    csv_content = data.get('csv_content', '')
    field_mapping = data.get('field_mapping')
    
    if not csv_content:
        return jsonify({'error': 'CSV content required'}), 400
    
    try:
        importer = CSVImporter()
        normalized = importer.parse_csv(csv_content, custom_mapping=field_mapping)
        
        # Save to database
        conn = get_db()
        manager = ImportManager(conn)
        result = manager.save_contacts(normalized)
        conn.close()
        
        return jsonify({
            'source': 'csv',
            'field_mapping': importer.field_mapping,
            **result,
            **importer.get_result()
        })
        
    except Exception as e:
        logger.error(f"CSV import error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/import/status', methods=['GET'])
def import_status():
    """Get import connection status for all CRMs."""
    status = {
        'hubspot': {
            'configured': bool(os.getenv('HUBSPOT_API_KEY') or os.getenv('HUBSPOT_ACCESS_TOKEN')),
            'type': 'oauth' if os.getenv('HUBSPOT_ACCESS_TOKEN') else 'api_key'
        },
        'salesforce': {
            'configured': bool(os.getenv('SALESFORCE_USERNAME') and os.getenv('SALESFORCE_PASSWORD')),
            'type': 'credentials'
        },
        'pipedrive': {
            'configured': bool(os.getenv('PIPEDRIVE_API_TOKEN')),
            'type': 'api_token'
        },
        'csv': {
            'configured': True,
            'type': 'file_upload'
        }
    }
    return jsonify(status)
