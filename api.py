

import os
import sys
import json
import re
from flask import Flask, jsonify, request, send_file

from flask_cors import CORS
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import requests
import logging
import traceback
from openai import OpenAI
# Playbook API
from playbook_api import register_playbook_routes



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

DATABASE_URL = os.environ.get('DATABASE_URL')
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
    """Get PostgreSQL database connection with RealDictCursor"""
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = RealDictCursor
    return conn

# Initialize database (safely)
def ensure_tables():
    """Ensure all required tables and columns exist."""
    conn = get_db()
    conn.autocommit = True  # Each statement is its own transaction - prevents cascade failures
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
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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
            id SERIAL PRIMARY KEY,
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

    def standardize_enrichment_output(self, raw_text: str) -> str:
        """
        Ensure consistent section markers for reliable frontend parsing.
        Converts various markdown header formats to === SECTION === format.
        """
        import re
    
        if not raw_text:
            return raw_text
    
        # Standardize section headers to === FORMAT ===
        replacements = [
            (r'#{2,4}\s*PERSON RESEARCH[^\n]*', '=== PERSON RESEARCH ==='),
            (r'#{2,4}\s*COMPANY RESEARCH[^\n]*', '=== COMPANY RESEARCH ==='),
            (r'#{2,4}\s*SALES INTELLIGENCE[^\n]*', '=== SALES INTELLIGENCE ==='),
            (r'#{2,4}\s*PERSONALITY ANALYSIS[^\n]*', '=== PERSONALITY ANALYSIS ==='),
            # Also catch if already has === but missing ===
            (r'===\s*PERSON RESEARCH\s*(?!===)', '=== PERSON RESEARCH ==='),
            (r'===\s*COMPANY RESEARCH\s*(?!===)', '=== COMPANY RESEARCH ==='),
            (r'===\s*SALES INTELLIGENCE\s*(?!===)', '=== SALES INTELLIGENCE ==='),
            (r'===\s*PERSONALITY ANALYSIS\s*(?!===)', '=== PERSONALITY ANALYSIS ==='),
        ]
    
        result = raw_text
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            
        return result


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

# DEBUG: Route registration checker

# Initialize database tables
try:
    ensure_tables()
except Exception as e:
    logger.warning(f"DB init: {e}")

@app.route('/api/debug/routes', methods=['GET'])
def debug_routes():
    """List all registered routes"""
    from flask import jsonify
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'})),
            'path': str(rule.rule)
        })
    return jsonify({
        'total': len(routes),
        'routes': sorted(routes, key=lambda x: x['path'])
    })


# DEBUG: Route registration checker
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
    cursor.execute('SELECT * FROM contacts ORDER BY match_score DESC NULLS LAST, id DESC LIMIT %s OFFSET %s', (limit, offset))
    contacts = [dict(row) for row in cursor.fetchall()]
    cursor.execute('SELECT COUNT(*) as count FROM contacts')
    total = cursor.fetchone()["count"]
    conn.close()
    return jsonify({'contacts': contacts, 'total': total})


@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = %s', (contact_id,))
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
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({"error": "Not found"}), 404
        
        contact = dict(row)
        cursor.execute("UPDATE contacts SET enrichment_status = 'processing' WHERE id = %s", (contact_id,))
        conn.commit()
        conn.close()
        
        enricher = EnhancedEnrichment()
        result = enricher.enrich_contact(contact)
        
        if result and result.get('success'):
            # =====================================================
            # STANDARDIZE OUTPUT BEFORE SAVING
            # Ensures consistent === SECTION === markers for parser
            # =====================================================
            profile_text = enricher.standardize_enrichment_output(result['profile_text'])
            
            # Score with new engine
            scores = {}
            if SCORING_AVAILABLE:
                engine = ApexScoringEngine()
                scores = engine.score_contact(contact, profile_text)
                
            conn = get_db()
            conn.execute("""
                UPDATE contacts SET
                    enrichment_data = %s,
                    enriched = 1,
                    enriched_at = %s,
                    enrichment_status = 'completed',
                    match_score = %s,
                    match_tier = %s,
                    fit_score = %s,
                    relevance_score = %s,
                    timing_score = %s,
                    last_scored = %s
                WHERE id = %s
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
                'profile_length': len(profile_text),  # Updated to use standardized length
                'scores': scores
            })
        else:
            conn = get_db()
            conn.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s", (contact_id,))
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
    cursor.execute("SELECT enrichment_status, enriched_at FROM contacts WHERE id = %s", (contact_id,))
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
    cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
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
            match_score = %s, match_tier = %s,
            fit_score = %s, relevance_score = %s, timing_score = %s,
            last_scored = %s
        WHERE id = %s
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
    cursor.execute("SELECT * FROM contact_match WHERE contact_id = %s", (contact_id,))
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
    cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
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
    cursor.execute("SELECT * FROM user_profile WHERE user_id = %s", (user_id,))
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
    cursor.execute("SELECT * FROM proof_points WHERE user_id = %s", (user_id,))
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
    cursor.execute("SELECT COUNT(*) as count FROM contacts")
    total = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
    enriched = cursor.fetchone()["count"]

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



# Register playbook routes
register_playbook_routes(app, get_db)


# =============================================================================
# AI OUTREACH GENERATION - Powered by Playbook + Enrichment + ICP
# =============================================================================

@app.route('/api/contacts/<int:contact_id>/generate-outreach', methods=['POST'])
def generate_outreach(contact_id):
    """Generate AI-powered personalized outreach using Playbook + Enrichment + ICP"""
    try:
        data = request.json or {}
        template = data.get('template', 'intro')  # intro, follow_up, value_add, meeting_request
        tone = data.get('tone', 'professional')   # professional, casual, executive, challenger
        channel = data.get('channel', 'email')    # email, linkedin
        custom_context = data.get('context', '')
        
        # Load contact
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Contact not found'}), 404
        
        contact = dict(row)
        enrichment = contact.get('enrichment_data', '') or ''
        
        # Load playbook
        playbook = {}
        playbook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playbook.json')
        if os.path.exists(playbook_path):
            with open(playbook_path, 'r') as f:
                playbook = json.load(f)
        
        # Get ICP match data
        from playbook_api import calculate_icp_match, generate_why_us_fit
        icp_match = calculate_icp_match(contact, enrichment, playbook)
        why_us = generate_why_us_fit(playbook)
        
        # Extract personality insights if available
        personality = extract_personality_for_outreach(enrichment)
        
        # Get user profile for signature
        cursor.execute("SELECT * FROM user_profile WHERE user_id = %s", ('default',))
        user_row = cursor.fetchone()
        user_profile = dict(user_row) if user_row else {}
        conn.close()
        
        # Build the prompt
        prompt = build_outreach_prompt(
            contact=contact,
            enrichment=enrichment,
            playbook=playbook,
            icp_match=icp_match,
            why_us=why_us,
            personality=personality,
            user_profile=user_profile,
            template=template,
            tone=tone,
            channel=channel,
            custom_context=custom_context
        )
        
        # Generate with GPT-4
        try:
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": get_outreach_system_prompt(channel, tone)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            generated = response.choices[0].message.content
            
            # Parse the response
            result = parse_outreach_response(generated, channel)
            result['icp_score'] = icp_match.get('score', 0)
            result['match_reasons'] = icp_match.get('reasons', [])
            result['personality_adapted'] = bool(personality.get('mbti') or personality.get('disc'))
            
            return jsonify({
                'success': True,
                'outreach': result,
                'meta': {
                    'template': template,
                    'tone': tone,
                    'channel': channel,
                    'contact_name': contact.get('name') or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip(),
                    'company': contact.get('company', ''),
                    'generated_at': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            # Fallback to template-based generation
            result = generate_fallback_outreach(contact, playbook, template, tone, channel)
            return jsonify({
                'success': True,
                'outreach': result,
                'meta': {
                    'template': template,
                    'tone': tone,
                    'channel': channel,
                    'fallback': True
                }
            })
            
    except Exception as e:
        logger.error(f"Outreach generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>/generate-sequence', methods=['POST'])
def generate_outreach_sequence(contact_id):
    """Generate a 3-email drip sequence"""
    try:
        data = request.json or {}
        tone = data.get('tone', 'professional')
        
        # Load contact and playbook
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Contact not found'}), 404
        
        contact = dict(row)
        enrichment = contact.get('enrichment_data', '') or ''
        
        # Load playbook
        playbook = {}
        playbook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playbook.json')
        if os.path.exists(playbook_path):
            with open(playbook_path, 'r') as f:
                playbook = json.load(f)
        
        # Generate sequence with GPT-4
        try:
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            contact_name = contact.get('name') or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
            company = contact.get('company', '')
            title = contact.get('title', '')
            company_name = playbook.get('companyName', 'our company')
            tagline = playbook.get('tagline', '')
            
            value_props = [vp.get('headline', '') for vp in playbook.get('valueProps', [])[:3]]
            pain_points = [pp.get('problem', '') for pp in playbook.get('painPoints', [])[:3]]
            
            prompt = f"""Generate a 3-email outreach sequence for:
            
Contact: {contact_name}
Title: {title}
Company: {company}

Our Company: {company_name}
What We Do: {tagline}
Value Props: {', '.join(value_props)}
Problems We Solve: {', '.join(pain_points)}

Generate exactly 3 emails:
1. INTRO: First touch, focus on relevance and one key value prop
2. VALUE: Share a specific insight or case study, build credibility  
3. BREAK-UP: Final attempt, create urgency, easy call-to-action

Tone: {tone}

For each email provide:
    - subject: Subject line
    - body: Email body (no greeting, just the content)
    - cta: Clear call-to-action
    - send_day: Recommended day to send (Day 1, Day 4, Day 7)

Return as JSON array with 3 objects."""

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert B2B sales copywriter. Generate compelling, personalized email sequences. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )
            
            result = json.loads(response.choices[0].message.content)
            sequence = result.get('sequence', result.get('emails', [result]))
            if not isinstance(sequence, list):
                sequence = [sequence]
            
            return jsonify({
                'success': True,
                'sequence': sequence,
                'contact': {
                    'name': contact_name,
                    'company': company,
                    'title': title
                }
            })
            
        except Exception as e:
            logger.error(f"Sequence generation error: {e}")
            # Return fallback sequence
            return jsonify({
                'success': True,
                'sequence': generate_fallback_sequence(contact, playbook, tone),
                'fallback': True
            })
            
    except Exception as e:
        logger.error(f"Sequence error: {e}")
        return jsonify({'error': str(e)}), 500


def extract_personality_for_outreach(enrichment: str) -> dict:
    """Extract MBTI/DISC insights to adapt communication style"""
    result = {'mbti': None, 'disc': None, 'style_tips': []}
    
    if not enrichment:
        return result
    
    # Extract MBTI
    mbti_match = re.search(r'(?:MBTI|Type)[:\s]*([IEFSNTJP]{4})', enrichment, re.IGNORECASE)
    if mbti_match:
        result['mbti'] = mbti_match.group(1).upper()
        
        # Add style tips based on MBTI
        mbti = result['mbti']
        if mbti[0] == 'I':
            result['style_tips'].append("Give them time to process; avoid pressure")
        if mbti[1] == 'N':
            result['style_tips'].append("Focus on big picture and possibilities")
        if mbti[2] == 'T':
            result['style_tips'].append("Lead with data and logic")
        if mbti[3] == 'J':
            result['style_tips'].append("Be structured and respect their time")
    
    # Extract DISC
    disc_match = re.search(r'Primary[:\s]*([DISC])\s*[-–]\s*(\w+)', enrichment, re.IGNORECASE)
    if disc_match:
        result['disc'] = f"{disc_match.group(1).upper()} - {disc_match.group(2)}"
        
        disc_type = disc_match.group(1).upper()
        if disc_type == 'D':
            result['style_tips'].append("Be direct and get to the point quickly")
        elif disc_type == 'I':
            result['style_tips'].append("Be enthusiastic and build rapport")
        elif disc_type == 'S':
            result['style_tips'].append("Be patient and emphasize stability")
        elif disc_type == 'C':
            result['style_tips'].append("Provide detailed information and proof")
    
    return result


def get_outreach_system_prompt(channel: str, tone: str) -> str:
    """Get system prompt based on channel and tone"""
    
    tone_guide = {
        'professional': "Write in a polished, business-appropriate tone. Be respectful and credible.",
        'casual': "Write in a friendly, conversational tone. Be approachable but still professional.",
        'executive': "Write in a concise, high-level tone. Respect their time, lead with impact.",
        'challenger': "Write in a thought-provoking tone. Challenge their assumptions, provide insights."
    }
    
    if channel == 'linkedin':
        return f"""You are an expert B2B LinkedIn outreach writer. 
{tone_guide.get(tone, tone_guide['professional'])}

Rules:
    - Keep messages under 300 characters for connection requests
    - Keep InMails under 500 characters
    - Be personalized and relevant
    - No generic templates
    - Include ONE clear call-to-action
    - Sound human, not salesy"""
    
    else:  # email
        return f"""You are an expert B2B cold email copywriter.
{tone_guide.get(tone, tone_guide['professional'])}

Rules:
    - Subject lines under 50 characters, curiosity-driven
    - Emails under 150 words
    - Personalized opening line (not "I hope this finds you well")
    - ONE clear value proposition
    - ONE clear call-to-action
    - No attachments or heavy formatting
    - Sound human and relevant"""


def build_outreach_prompt(contact, enrichment, playbook, icp_match, why_us, personality, user_profile, template, tone, channel, custom_context):
    """Build the generation prompt with all context"""
    
    contact_name = contact.get('name') or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
    
    # Template-specific instructions
    template_instructions = {
        'intro': "Write a first-touch outreach. Focus on relevance and ONE compelling hook.",
        'follow_up': "Write a follow-up to a previous message. Reference the first touch, add new value.",
        'value_add': "Write a value-add message. Share an insight, article, or case study relevant to them.",
        'meeting_request': "Write a meeting request. Be direct about wanting 15 minutes, make it easy to say yes.",
        'referral': "Write asking for a referral or introduction. Be specific about who you'd like to meet.",
        'event': "Write an event-based outreach. Reference a trigger event (funding, hire, news)."
    }
    
    # Build context sections
    prompt_parts = [
        f"Generate a {channel} {template.replace('_', ' ')} message.",
        "",
        f"=== RECIPIENT ===",
        f"Name: {contact_name}",
        f"Title: {contact.get('title', 'Unknown')}",
        f"Company: {contact.get('company', 'Unknown')}",
    ]
    
    # Add ICP match context
    if icp_match.get('reasons'):
        prompt_parts.append(f"Why They're a Fit: {', '.join(icp_match['reasons'])}")
    
    # Add personality adaptation
    if personality.get('style_tips'):
        prompt_parts.append(f"Communication Style Tips: {'; '.join(personality['style_tips'])}")
    
    # Add enrichment highlights
    if enrichment:
        # Extract key points from enrichment
        highlights = []
        if 'linkedin' in enrichment.lower():
            highlights.append("Active on LinkedIn")
        if any(word in enrichment.lower() for word in ['growth', 'scaling', 'expanding']):
            highlights.append("Company in growth mode")
        if any(word in enrichment.lower() for word in ['challenge', 'pain', 'struggle']):
            highlights.append("Facing business challenges")
        if highlights:
            prompt_parts.append(f"Intel: {', '.join(highlights)}")
    
    # Add our company context
    prompt_parts.extend([
        "",
        f"=== OUR COMPANY ===",
        f"Company: {playbook.get('companyName', 'Our Company')}",
        f"What We Do: {playbook.get('tagline', '')}",
    ])
    
    # Add value props
    value_props = playbook.get('valueProps', [])
    if value_props:
        vp_list = [vp.get('headline', '') for vp in value_props[:3] if vp.get('headline')]
        if vp_list:
            prompt_parts.append(f"Key Value Props: {' | '.join(vp_list)}")
    
    # Add proof points
    proof_points = playbook.get('proofPoints', [])
    if proof_points:
        proof_list = [pp.get('title', '') for pp in proof_points[:2] if pp.get('title')]
        if proof_list:
            prompt_parts.append(f"Proof Points: {', '.join(proof_list)}")
    
    # Add sender context
    sender_name = user_profile.get('full_name', '')
    sender_role = user_profile.get('role', '')
    if sender_name:
        prompt_parts.extend([
            "",
            f"=== SENDER ===",
            f"Name: {sender_name}",
            f"Role: {sender_role}" if sender_role else ""
        ])
    
    # Add instructions
    prompt_parts.extend([
        "",
        f"=== INSTRUCTIONS ===",
        template_instructions.get(template, template_instructions['intro']),
        f"Tone: {tone}",
    ])
    
    if custom_context:
        prompt_parts.append(f"Additional Context: {custom_context}")
    
    if channel == 'email':
        prompt_parts.extend([
            "",
            "Return JSON with: subject, opening, body, cta, signature_note"
        ])
    else:
        prompt_parts.extend([
            "",
            "Return JSON with: message, cta"
        ])
    
    return '\n'.join(prompt_parts)


def parse_outreach_response(response: str, channel: str) -> dict:
    """Parse GPT response into structured format"""
    try:
        # Try to parse as JSON
        if '{' in response:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
    except:
        pass
    
    # Fallback: return as plain text
    if channel == 'email':
        return {
            'subject': 'Quick question',
            'opening': '',
            'body': response,
            'cta': '',
            'signature_note': ''
        }
    else:
        return {
            'message': response,
            'cta': ''
        }


def generate_fallback_outreach(contact, playbook, template, tone, channel):
    """Generate template-based fallback when AI unavailable"""
    contact_name = contact.get('name') or contact.get('first_name', 'there')
    company = contact.get('company', 'your company')
    our_company = playbook.get('companyName', 'our company')
    tagline = playbook.get('tagline', 'help businesses grow')
    
    if channel == 'email':
        return {
            'subject': f"Quick question about {company}",
            'opening': f"Hi {contact_name},",
            'body': f"I came across {company} and thought there might be some synergy. At {our_company}, we {tagline}. Would love to explore if we could help.",
            'cta': "Would you be open to a quick 15-minute call this week?",
            'signature_note': "Looking forward to connecting."
        }
    else:
        return {
            'message': f"Hi {contact_name}, I noticed your work at {company}. At {our_company}, we {tagline}. Would love to connect and share ideas.",
            'cta': "Open to connecting?"
        }


def generate_fallback_sequence(contact, playbook, tone):
    """Generate fallback email sequence"""
    contact_name = contact.get('name') or contact.get('first_name', 'there')
    company = contact.get('company', 'your company')
    our_company = playbook.get('companyName', 'our company')
    
    return [
        {
            'subject': f"Quick idea for {company}",
            'body': f"Hi {contact_name}, noticed {company} and thought of a potential fit with what we do at {our_company}.",
            'cta': "Worth a quick chat?",
            'send_day': "Day 1"
        },
        {
            'subject': f"Following up",
            'body': f"Hi {contact_name}, wanted to follow up on my last note. Happy to share how we've helped similar companies.",
            'cta': "15 minutes this week?",
            'send_day': "Day 4"
        },
        {
            'subject': f"Should I close the loop?",
            'body': f"Hi {contact_name}, I'll assume the timing isn't right if I don't hear back. No worries either way - just wanted to make sure this didn't slip through.",
            'cta': "Let me know either way?",
            'send_day': "Day 7"
        }
    ]


# =============================================================================
# CALL SCRIPT GENERATION
# =============================================================================

@app.route('/api/contacts/<int:contact_id>/generate-call-script', methods=['POST'])
def generate_call_script(contact_id):
    """Generate AI-powered call script with talking points, objection handlers, and discovery questions"""
    try:
        data = request.json or {}
        call_type = data.get('call_type', 'discovery')  # discovery, follow_up, demo_set, check_in
        
        # Load contact
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return jsonify({'error': 'Contact not found'}), 404
        
        contact = dict(row)
        enrichment = contact.get('enrichment_data', '') or ''
        
        # Load playbook
        playbook = {}
        playbook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playbook.json')
        if os.path.exists(playbook_path):
            with open(playbook_path, 'r') as f:
                playbook = json.load(f)
        
        # Get ICP match
        from playbook_api import calculate_icp_match
        icp_match = calculate_icp_match(contact, enrichment, playbook)
        
        # Extract personality for communication style
        personality = extract_personality_for_outreach(enrichment)
        
        conn.close()
        
        contact_name = contact.get('name') or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
        company = contact.get('company', '')
        title = contact.get('title', '')
        our_company = playbook.get('companyName', 'our company')
        tagline = playbook.get('tagline', '')
        
        # Build value props and pain points
        value_props = [vp.get('headline', '') for vp in playbook.get('valueProps', [])[:3]]
        pain_points = [pp.get('problem', '') for pp in playbook.get('painPoints', [])[:3]]
        proof_points = [pp.get('title', '') for pp in playbook.get('proofPoints', [])[:2]]
        
        # Build prompt
        prompt = f"""Generate a complete call script for a {call_type.replace('_', ' ')} call.

=== PROSPECT ===
Name: {contact_name}
Title: {title}
Company: {company}
ICP Match: {icp_match.get('score', 0)}% ({', '.join(icp_match.get('reasons', []))})

=== OUR COMPANY ===
Company: {our_company}
What We Do: {tagline}
Value Props: {' | '.join(value_props)}
Problems We Solve: {' | '.join(pain_points)}
Proof Points: {', '.join(proof_points)}

=== COMMUNICATION STYLE ===
{'; '.join(personality.get('style_tips', ['Be professional and direct']))}

Generate a JSON object with:
{{
  "opener": "15-second opening hook that grabs attention",
  "permission_ask": "Brief ask to continue the conversation",
  "value_statement": "30-second value prop tailored to their role",
  "discovery_questions": ["5 open-ended questions to uncover pain"],
  "talking_points": ["4 key points to make during the call"],
  "objection_handlers": {{
    "no_time": "Response to 'I don't have time'",
    "not_interested": "Response to 'Not interested'",
    "send_info": "Response to 'Just send me info'",
    "have_solution": "Response to 'We already have something'",
    "no_budget": "Response to 'No budget right now'"
  }},
  "meeting_ask": "Clear ask for next step/meeting",
  "voicemail_script": "30-second voicemail if they don't answer"
}}"""

        try:
            client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert B2B sales call coach. Generate natural, conversational call scripts that sound human - not robotic. Focus on building rapport and uncovering genuine needs. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=1500
            )
            
            script = json.loads(response.choices[0].message.content)
            
            return jsonify({
                'success': True,
                'script': script,
                'meta': {
                    'call_type': call_type,
                    'contact_name': contact_name,
                    'company': company,
                    'icp_score': icp_match.get('score', 0),
                    'generated_at': datetime.now().isoformat()
                }
            })
            
        except Exception as e:
            logger.error(f"OpenAI call script error: {e}")
            # Fallback script
            return jsonify({
                'success': True,
                'script': generate_fallback_call_script(contact, playbook, call_type),
                'fallback': True
            })
            
    except Exception as e:
        logger.error(f"Call script error: {e}")
        return jsonify({'error': str(e)}), 500


def generate_fallback_call_script(contact, playbook, call_type):
    """Generate template-based fallback call script"""
    contact_name = contact.get('name') or contact.get('first_name', 'there')
    company = contact.get('company', 'your company')
    our_company = playbook.get('companyName', 'our company')
    
    return {
        'opener': f"Hi {contact_name}, this is [Your Name] from {our_company}. Did I catch you at an okay time?",
        'permission_ask': "I'll be brief - I'm reaching out because we work with companies like yours and I wanted to see if it makes sense to talk.",
        'value_statement': f"We help companies like {company} streamline their operations and drive growth. Many of our clients see results within the first 90 days.",
        'discovery_questions': [
            "What's your biggest priority this quarter?",
            "How are you currently handling [relevant process]?",
            "What's working well? What could be better?",
            "If you could wave a magic wand and fix one thing, what would it be?",
            "What would success look like for you in the next 6 months?"
        ],
        'talking_points': [
            "We specialize in helping companies like yours",
            "Our clients typically see [specific result]",
            "We're different because [key differentiator]",
            "Here's a quick example of how we helped [similar company]"
        ],
        'objection_handlers': {
            'no_time': "I totally understand - you're busy. When would be a better time for a quick 10-minute call?",
            'not_interested': "I appreciate you being direct. Mind if I ask what solution you're currently using?",
            'send_info': "Happy to send info. What specifically would be most helpful for you to see?",
            'have_solution': "That's great you have something in place. How's it working for you? Any gaps?",
            'no_budget': "Understood. When does your planning cycle start for next year?"
        },
        'meeting_ask': "Based on what you've shared, I think a quick 15-minute call to show you [specific thing] would be valuable. How does Thursday at 2pm work?",
        'voicemail_script': f"Hi {contact_name}, this is [Your Name] from {our_company}. I'm reaching out because we help companies like {company} with [value prop]. I'd love to share how - give me a call back at [number] or I'll try you again soon."
    }



# CADENCE MANAGEMENT SYSTEM
# =============================================================================

@app.route('/api/cadences', methods=['GET'])
def get_cadences():
    """Get all cadence templates"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cadences WHERE is_active = 1 ORDER BY name')
    cadences = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Parse steps JSON
    for c in cadences:
        if c.get('steps'):
            c['steps'] = json.loads(c['steps'])
    
    return jsonify({'cadences': cadences})


@app.route('/api/cadences', methods=['POST'])
def create_cadence():
    """Create a new cadence template"""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO cadences (name, description, steps)
        VALUES (?, ?, ?)
    ''', (data.get('name'), data.get('description'), json.dumps(data.get('steps', []))))
    
    cadence_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cadence_id})


@app.route('/api/cadences/<int:cadence_id>', methods=['PUT'])
def update_cadence(cadence_id):
    """Update a cadence template"""
    data = request.json
    conn = get_db()
    
    conn.execute('''
        UPDATE cadences 
        SET name = %s, description = %s, steps = %s, updated_at = %s
        WHERE id = %s
    ''', (data.get('name'), data.get('description'), json.dumps(data.get('steps', [])), 
          datetime.now().isoformat(), cadence_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@app.route('/api/cadences/<int:cadence_id>', methods=['DELETE'])
def delete_cadence(cadence_id):
    """Soft delete a cadence"""
    conn = get_db()
    conn.execute('UPDATE cadences SET is_active = 0 WHERE id = %s', (cadence_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@app.route('/api/contacts/<int:contact_id>/enroll', methods=['POST'])
def enroll_in_cadence(contact_id):
    """Enroll a contact in a cadence"""
    data = request.json
    cadence_id = data.get('cadence_id')
    
    if not cadence_id:
        return jsonify({'error': 'cadence_id required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if already enrolled
    cursor.execute('''
        SELECT id, status FROM cadence_enrollments 
        WHERE contact_id = %s AND cadence_id = %s
    ''', (contact_id, cadence_id))
    existing = cursor.fetchone()
    
    if existing:
        if existing['status'] == 'active':
            conn.close()
            return jsonify({'error': 'Already enrolled in this cadence'}), 400
        else:
            # Re-enroll
            cursor.execute('''
                UPDATE cadence_enrollments 
                SET status = 'active', current_step = 0, started_at = %s, 
                    next_action_date = date('now'), completed_at = NULL
                WHERE id = %s
            ''', (datetime.now().isoformat(), existing['id']))
            enrollment_id = existing['id']
    else:
        cursor.execute('''
            INSERT INTO cadence_enrollments (contact_id, cadence_id, next_action_date)
            VALUES (?, ?, date('now'))
        ''', (contact_id, cadence_id))
        enrollment_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'enrollment_id': enrollment_id})


@app.route('/api/contacts/<int:contact_id>/enrollments', methods=['GET'])
def get_contact_enrollments(contact_id):
    """Get all cadence enrollments for a contact"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT e.*, c.name as cadence_name, c.steps as cadence_steps
        FROM cadence_enrollments e
        JOIN cadences c ON e.cadence_id = c.id
        WHERE e.contact_id = %s
        ORDER BY e.started_at DESC
    ''', (contact_id,))
    
    enrollments = []
    for row in cursor.fetchall():
        e = dict(row)
        e['cadence_steps'] = json.loads(e['cadence_steps']) if e.get('cadence_steps') else []
        enrollments.append(e)
    
    conn.close()
    return jsonify({'enrollments': enrollments})


@app.route('/api/enrollments/<int:enrollment_id>/advance', methods=['POST'])
def advance_enrollment(enrollment_id):
    """Mark current step complete and advance to next"""
    data = request.json
    action = data.get('action', 'completed')  # completed, skipped
    outcome = data.get('outcome')  # positive, neutral, negative
    notes = data.get('notes', '')
    content_used = data.get('content_used', '')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get current enrollment
    cursor.execute('''
        SELECT e.*, c.steps 
        FROM cadence_enrollments e
        JOIN cadences c ON e.cadence_id = c.id
        WHERE e.id = %s
    ''', (enrollment_id,))
    
    enrollment = cursor.fetchone()
    if not enrollment:
        conn.close()
        return jsonify({'error': 'Enrollment not found'}), 404
    
    enrollment = dict(enrollment)
    steps = json.loads(enrollment['steps'])
    current_step = enrollment['current_step']
    
    # Log the activity
    if current_step < len(steps):
        step = steps[current_step]
        cursor.execute('''
            INSERT INTO cadence_activities 
            (enrollment_id, step_index, channel, action, outcome, notes, content_used)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (enrollment_id, current_step, step['channel'], action, outcome, notes, content_used))
    
    # Advance to next step
    next_step = current_step + 1
    
    if next_step >= len(steps):
        # Cadence complete
        cursor.execute('''
            UPDATE cadence_enrollments 
            SET current_step = %s, status = 'completed', completed_at = %s
            WHERE id = %s
        ''', (next_step, datetime.now().isoformat(), enrollment_id))
        status = 'completed'
    else:
        # Calculate next action date
        days_until_next = steps[next_step]['day'] - steps[current_step]['day']
        cursor.execute('''
            UPDATE cadence_enrollments 
            SET current_step = %s, next_action_date = date('now', '+' || ? || ' days')
            WHERE id = %s
        ''', (next_step, days_until_next, enrollment_id))
        status = 'active'
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True, 
        'new_step': next_step, 
        'status': status,
        'is_complete': status == 'completed'
    })


@app.route('/api/enrollments/<int:enrollment_id>/status', methods=['PUT'])
def update_enrollment_status(enrollment_id):
    """Update enrollment status (pause, resume, mark replied, etc.)"""
    data = request.json
    new_status = data.get('status')
    notes = data.get('notes', '')
    
    if new_status not in ['active', 'paused', 'completed', 'replied', 'booked', 'not_interested']:
        return jsonify({'error': 'Invalid status'}), 400
    
    conn = get_db()
    
    update_fields = ['status = %s', 'notes = %s']
    params = [new_status, notes]
    
    if new_status == 'paused':
        update_fields.append('paused_at = %s')
        params.append(datetime.now().isoformat())
    elif new_status in ['completed', 'replied', 'booked', 'not_interested']:
        update_fields.append('completed_at = %s')
        params.append(datetime.now().isoformat())
    elif new_status == 'active':
        update_fields.append('paused_at = NULL')
    
    params.append(enrollment_id)
    
    conn.execute(f'''
        UPDATE cadence_enrollments SET {', '.join(update_fields)} WHERE id = %s
    ''', params)
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@app.route('/api/cadence-queue', methods=['GET'])
def get_cadence_queue():
    """Get today's action queue - all steps due today or overdue"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            e.id as enrollment_id,
            e.contact_id,
            e.current_step,
            e.next_action_date,
            e.started_at,
            c.id as cadence_id,
            c.name as cadence_name,
            c.steps as cadence_steps,
            ct.name as contact_name,
            ct.first_name,
            ct.last_name,
            ct.email,
            ct.phone,
            ct.company,
            ct.title,
            ct.match_score,
            ct.match_tier
        FROM cadence_enrollments e
        JOIN cadences c ON e.cadence_id = c.id
        JOIN contacts ct ON e.contact_id = ct.id
        WHERE e.status = 'active'
          AND e.next_action_date <= date('now')
        ORDER BY e.next_action_date ASC, ct.match_score DESC
    ''')
    
    queue = []
    for row in cursor.fetchall():
        item = dict(row)
        steps = json.loads(item['cadence_steps'])
        current_step_idx = item['current_step']
        
        if current_step_idx < len(steps):
            current_step = steps[current_step_idx]
            item['current_action'] = {
                'channel': current_step['channel'],
                'template': current_step.get('template', 'intro'),
                'title': current_step.get('title', f"Step {current_step_idx + 1}"),
                'day': current_step['day']
            }
            item['total_steps'] = len(steps)
            item['progress'] = f"{current_step_idx + 1}/{len(steps)}"
            
            # Contact display name
            item['contact_display'] = item['contact_name'] or f"{item['first_name'] or ''} {item['last_name'] or ''}".strip() or 'Unknown'
            
            del item['cadence_steps']  # Don't send full steps
            queue.append(item)
    
    conn.close()
    
    # Group by channel for easy filtering
    by_channel = {'email': [], 'call': [], 'linkedin': []}
    for item in queue:
        channel = item['current_action']['channel']
        if channel in by_channel:
            by_channel[channel].append(item)
    
    return jsonify({
        'queue': queue,
        'by_channel': by_channel,
        'summary': {
            'total': len(queue),
            'emails': len(by_channel['email']),
            'calls': len(by_channel['call']),
            'linkedin': len(by_channel['linkedin'])
        }
    })


@app.route('/api/cadence-stats', methods=['GET'])
def get_cadence_stats():
    """Get cadence performance statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Overall stats
    cursor.execute('''
        SELECT 
            COUNT(*) as total_enrollments,
            SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'replied' THEN 1 ELSE 0 END) as replied,
            SUM(CASE WHEN status = 'booked' THEN 1 ELSE 0 END) as booked,
            SUM(CASE WHEN status = 'paused' THEN 1 ELSE 0 END) as paused
        FROM cadence_enrollments
    ''')
    
    stats = dict(cursor.fetchone())
    
    # Calculate reply rate
    completed_or_replied = (stats['completed'] or 0) + (stats['replied'] or 0) + (stats['booked'] or 0)
    if completed_or_replied > 0:
        stats['reply_rate'] = round(((stats['replied'] or 0) + (stats['booked'] or 0)) / completed_or_replied * 100, 1)
    else:
        stats['reply_rate'] = 0
    
    # Activities today
    cursor.execute('''
        SELECT COUNT(*) as count FROM cadence_activities 
        WHERE date(completed_at) = date('now')
    ''')
    stats['activities_today'] = cursor.fetchone()["count"]
    
    # Due today
    cursor.execute('''
        SELECT COUNT(*) as count FROM cadence_enrollments 
        WHERE status = 'active' AND next_action_date <= date('now')
    ''')
    stats['due_today'] = cursor.fetchone()["count"]
    
    conn.close()
    
    return jsonify(stats)



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
    cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Contact not found'}), 404
    
    contact = dict(row)
    enrichment = contact.get('enrichment_data') or ''
    
    # Get Why Me data if exists
    cursor.execute("SELECT * FROM contact_match WHERE contact_id = %s", (contact_id,))
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
    cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Contact not found'}), 404
    
    contact = dict(row)
    enrichment = contact.get('enrichment_data') or ''
    
    cursor.execute("SELECT * FROM contact_match WHERE contact_id = %s", (contact_id,))
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
    cursor.execute("SELECT COUNT(*) as count FROM contacts")
    total_contacts = cursor.fetchone()["count"]
    
    # Enriched contacts
    cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
    enriched_contacts = cursor.fetchone()["count"]
    
    # Scored contacts
    cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_score IS NOT NULL")
    scored_contacts = cursor.fetchone()["count"]
    
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
    cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Contact not found'}), 404
    
    contact = dict(row)
    enrichment = contact.get('enrichment_data') or ''
    
    cursor.execute("SELECT * FROM contact_match WHERE contact_id = %s", (contact_id,))
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
        SELECT COUNT(*) as count FROM contacts 
        WHERE match_tier = 'HIGH' AND enrichment_status = 'completed'
    """)
    lists.append({
        'id': 'hot_leads',
        'name': 'Hot Leads',
        'description': 'High match score, enriched and ready',
        'icon': 'flame',
        'color': 'red',
        'count': cursor.fetchone()["count"],
        'filter': {'match_tier': 'HIGH', 'enrichment_status': 'completed'}
    })
    
    # Ready to Contact (enriched, has phone or email)
    cursor.execute("""
        SELECT COUNT(*) as count FROM contacts 
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
        'count': cursor.fetchone()["count"],
        'filter': {'enrichment_status': 'completed', 'min_score': 50, 'has_contact': True}
    })
    
    # Needs Enrichment (not enriched yet)
    cursor.execute("""
        SELECT COUNT(*) as count FROM contacts 
        WHERE enrichment_status IS NULL OR enrichment_status = 'pending'
    """)
    lists.append({
        'id': 'needs_enrichment',
        'name': 'Needs Enrichment',
        'description': 'Not yet enriched',
        'icon': 'zap',
        'color': 'yellow',
        'count': cursor.fetchone()["count"],
        'filter': {'enrichment_status': ['pending', None]}
    })
    
    # High Fit Low Timing (good fit but no urgency)
    cursor.execute("""
        SELECT COUNT(*) as count FROM contacts 
        WHERE fit_score >= 70 AND timing_score < 30
    """)
    lists.append({
        'id': 'nurture_list',
        'name': 'Nurture List',
        'description': 'Great fit, needs nurturing (low timing)',
        'icon': 'clock',
        'color': 'blue',
        'count': cursor.fetchone()["count"],
        'filter': {'min_fit': 70, 'max_timing': 30}
    })
    
    # Decision Makers (title-based)
    cursor.execute("""
        SELECT COUNT(*) as count FROM contacts 
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
        'count': cursor.fetchone()["count"],
        'filter': {'title_contains': ['ceo', 'president', 'owner', 'principal', 'managing director']}
    })
    
    # Recently Enriched (last 7 days)
    cursor.execute("""
        SELECT COUNT(*) as count FROM contacts 
        WHERE enriched_at >= datetime('now', '-7 days')
    """)
    lists.append({
        'id': 'recently_enriched',
        'name': 'Recently Enriched',
        'description': 'Enriched in last 7 days',
        'icon': 'sparkles',
        'color': 'cyan',
        'count': cursor.fetchone()["count"],
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
            ORDER BY match_score DESC LIMIT %s
        """, (limit,))
    elif list_id == 'ready_to_contact':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE enrichment_status = 'completed' 
            AND (phone IS NOT NULL OR email IS NOT NULL)
            AND match_score >= 50
            ORDER BY match_score DESC LIMIT %s
        """, (limit,))
    elif list_id == 'needs_enrichment':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE enrichment_status IS NULL OR enrichment_status = 'pending'
            LIMIT %s
        """, (limit,))
    elif list_id == 'nurture_list':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE fit_score >= 70 AND timing_score < 30
            ORDER BY fit_score DESC LIMIT %s
        """, (limit,))
    elif list_id == 'decision_makers':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE (lower(title) LIKE '%ceo%' OR lower(title) LIKE '%president%' 
                   OR lower(title) LIKE '%owner%' OR lower(title) LIKE '%principal%'
                   OR lower(title) LIKE '%managing director%')
            AND enrichment_status = 'completed'
            ORDER BY match_score DESC LIMIT %s
        """, (limit,))
    elif list_id == 'recently_enriched':
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE enriched_at >= datetime('now', '-7 days')
            ORDER BY enriched_at DESC LIMIT %s
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
    conn.execute("UPDATE contacts SET match_tier = %s WHERE id = %s", (new_tier, contact_id))
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
    cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
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
    cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
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




# =============================================================================
# RUN APP
# =============================================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
# Deployment timestamp: 1765078883
# Deployment timestamp: 1765079148
# Cache bust: 1765087404
