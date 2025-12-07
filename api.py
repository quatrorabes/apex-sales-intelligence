#!/usr/bin/env python3
"""
APEX Sales Intelligence - Production API
Railway-deployable Flask backend with PostgreSQL
Version: 2.1.0 | December 7, 2025
Schema-matched to 140-column contacts table
"""

import os
import json
import re
from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import logging
import traceback

# ============================================================================
# CONFIGURATION
# ============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')
PORT = int(os.environ.get('PORT', 8000))
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

logger.info(f"Database: {'Connected' if DATABASE_URL else 'Missing DATABASE_URL'}")
logger.info(f"Perplexity: {'Yes' if PERPLEXITY_API_KEY else 'No'}")
logger.info(f"OpenAI: {'Yes' if OPENAI_API_KEY else 'No'}")

# ============================================================================
# DATABASE
# ============================================================================
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = RealDictCursor
    return conn

def safe_dict(row):
    """Convert RealDictRow to dict, handling any problematic types."""
    if row is None:
        return None
    result = {}
    for key, value in dict(row).items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif hasattr(value, '__str__'):
            result[key] = str(value) if value is not None else None
        else:
            result[key] = value
    return result

# Core columns we always select (safe subset of 140 columns)
CONTACT_COLUMNS = """
    id, name, firstname, lastname, email, phone, phone_mobile, company, title,
    match_score, match_tier, mdcp_score, mdcp_tier, lead_tier, icp_score, icp_tier,
    fit_score, relevance_score, timing_score, enrichment_status, enrichment_data,
    enriched, enriched_at, created_at, updated_at, notes, lead_status,
    cadence_id, cadence_status, cadence_started_at, times_contacted, last_contacted,
    persona, persona_type, persona_tier, persona_confidence,
    linkedin_url, industry, location, source
"""

def ensure_tables():
    """Ensure supporting tables exist."""
    try:
        conn = get_db()
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Cadences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cadences (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                steps TEXT,
                duration_days INTEGER DEFAULT 7,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        # Cadence enrollments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cadence_enrollments (
                id SERIAL PRIMARY KEY,
                contact_id INTEGER NOT NULL,
                cadence_id INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                current_step INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT NOW(),
                next_action_date DATE,
                completed_at TIMESTAMP
            )
        ''')
        
        # Cold call queue
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cold_call_queue (
                id SERIAL PRIMARY KEY,
                contact_id INTEGER,
                name TEXT,
                phone TEXT,
                mobile TEXT,
                email TEXT,
                company TEXT,
                title TEXT,
                source TEXT,
                notes TEXT,
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'new',
                attempts INTEGER DEFAULT 0,
                last_attempt TIMESTAMP,
                outcome TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        # Contact match / Why Me
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_match (
                id SERIAL PRIMARY KEY,
                contact_id INTEGER UNIQUE NOT NULL,
                user_id TEXT DEFAULT 'default',
                match_score REAL,
                hook TEXT,
                why_now TEXT,
                suggested_opening TEXT,
                talking_points TEXT,
                generated_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        # User profile
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id SERIAL PRIMARY KEY,
                user_id TEXT UNIQUE DEFAULT 'default',
                full_name TEXT,
                role TEXT,
                company TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        # Activities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id SERIAL PRIMARY KEY,
                contact_id INTEGER NOT NULL,
                activity_type TEXT,
                activity_date TIMESTAMP DEFAULT NOW(),
                notes TEXT,
                outcome TEXT
            )
        ''')
        
        # Insert default cadences if empty
        cursor.execute('SELECT COUNT(*) as count FROM cadences')
        if cursor.fetchone()['count'] == 0:
            cadences = [
                ('New Lead Intro', 'Initial outreach sequence', 
                 json.dumps([
                     {"day": 1, "channel": "email", "template": "intro", "title": "Introduction"},
                     {"day": 3, "channel": "linkedin", "template": "connection", "title": "LinkedIn"},
                     {"day": 5, "channel": "email", "template": "value_add", "title": "Value-Add"},
                     {"day": 7, "channel": "call", "template": "discovery", "title": "Call"}
                 ]), 7),
                ('Re-engagement', 'Wake up cold leads',
                 json.dumps([
                     {"day": 1, "channel": "email", "template": "breakup", "title": "Break-up"},
                     {"day": 4, "channel": "email", "template": "insight", "title": "Insight"}
                 ]), 5)
            ]
            for name, desc, steps, days in cadences:
                cursor.execute(
                    'INSERT INTO cadences (name, description, steps, duration_days) VALUES (%s, %s, %s, %s)',
                    (name, desc, steps, days)
                )
        
        conn.close()
        logger.info("Tables verified")
    except Exception as e:
        logger.error(f"Table setup error: {e}")

try:
    ensure_tables()
except:
    pass

# ============================================================================
# FLASK APP
# ============================================================================
app = Flask(__name__)
CORS(app)

# ============================================================================
# HEALTH & DEBUG
# ============================================================================
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'service': 'Apex Sales Intelligence API',
        'version': '2.1.0',
        'status': 'running'
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected' if DATABASE_URL else 'not configured',
        'perplexity': 'configured' if PERPLEXITY_API_KEY else 'not configured',
        'openai': 'configured' if OPENAI_API_KEY else 'not configured'
    })

@app.route('/api/debug/routes', methods=['GET'])
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
            'path': str(rule)
        })
    return jsonify({'total': len(routes), 'routes': sorted(routes, key=lambda x: x['path'])})

# ============================================================================
# CONTACTS
# ============================================================================
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    try:
        conn = get_db()
        cursor = conn.cursor()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        search = request.args.get('search', '')
        tier = request.args.get('tier', '')
        
        query = f"SELECT {CONTACT_COLUMNS} FROM contacts WHERE 1=1"
        params = []
        
        if search:
            query += " AND (name ILIKE %s OR email ILIKE %s OR company ILIKE %s)"
            params.extend([f"%{search}%"] * 3)
        
        if tier:
            query += " AND (match_tier = %s OR lead_tier = %s OR mdcp_tier = %s)"
            params.extend([tier] * 3)
        
        query += " ORDER BY match_score DESC NULLS LAST, id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        contacts = [safe_dict(row) for row in cursor.fetchall()]
        
        cursor.execute('SELECT COUNT(*) as count FROM contacts')
        total = cursor.fetchone()['count']
        
        conn.close()
        return jsonify({'contacts': contacts, 'total': total})
    except Exception as e:
        logger.error(f"get_contacts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {CONTACT_COLUMNS} FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if contact:
            return jsonify(safe_dict(contact))
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        logger.error(f"get_contact error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contacts (name, email, company, title, phone, source, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        ''', (
            data.get('name'),
            data.get('email'),
            data.get('company'),
            data.get('title'),
            data.get('phone'),
            data.get('source', 'manual')
        ))
        
        new_id = cursor.fetchone()['id']
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        logger.error(f"create_contact error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key in ['name', 'email', 'company', 'title', 'phone', 'notes', 'lead_status']:
            if key in data:
                fields.append(f'{key} = %s')
                values.append(data[key])
        
        if fields:
            values.append(contact_id)
            cursor.execute(f"UPDATE contacts SET {', '.join(fields)}, updated_at = NOW() WHERE id = %s", values)
            conn.commit()
        
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"update_contact error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM contacts WHERE id = %s', (contact_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/import', methods=['POST'])
def import_contacts():
    try:
        data = request.json
        contacts = data.get('contacts', [])
        
        conn = get_db()
        cursor = conn.cursor()
        success, failed = 0, 0
        
        for c in contacts:
            try:
                cursor.execute('''
                    INSERT INTO contacts (name, email, company, title, phone, source, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (email) DO UPDATE SET
                        name = EXCLUDED.name, company = EXCLUDED.company, title = EXCLUDED.title
                ''', (c.get('name'), c.get('email'), c.get('company'), c.get('title'), c.get('phone'), 'import'))
                success += 1
            except:
                failed += 1
        
        conn.commit()
        conn.close()
        return jsonify({'success': success, 'failed': failed})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import/status', methods=['GET'])
def import_status():
    return jsonify({'status': 'complete'})

# ============================================================================
# ICP MATCH (with data wrapper for frontend)
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/icp-match', methods=['GET'])
def get_icp_match(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, company, title, match_score, match_tier, mdcp_score, mdcp_tier,
                   fit_score, relevance_score, timing_score, icp_score, icp_tier, match_reasons
            FROM contacts WHERE id = %s
        ''', (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Not found'}), 404
        
        score = float(contact.get('match_score') or contact.get('icp_score') or contact.get('mdcp_score') or 0)
        tier = contact.get('match_tier') or contact.get('icp_tier') or contact.get('mdcp_tier') or 'UNSCORED'
        
        reasons = []
        if contact.get('match_reasons'):
            try:
                reasons = json.loads(contact['match_reasons']) if isinstance(contact['match_reasons'], str) else contact['match_reasons']
            except:
                reasons = [str(contact['match_reasons'])]
        
        if not reasons:
            if (contact.get('fit_score') or 0) > 70:
                reasons.append('Strong company/role fit')
            title = str(contact.get('title') or '').lower()
            if any(kw in title for kw in ['director', 'vp', 'chief', 'head', 'owner', 'president', 'ceo']):
                reasons.append('Decision-maker title')
            if not reasons:
                reasons = ['Matches ICP criteria']
        
        match_level = 'PERFECT' if score >= 80 else 'GOOD' if score >= 60 else 'OKAY' if score >= 40 else 'LOW'
        
        return jsonify({
            'data': {
                'contact_id': contact_id,
                'icp_match': {
                    'score': score,
                    'reasons': reasons,
                    'match_level': match_level
                },
                'why_us_fit': {
                    'summary': f'{match_level.capitalize()} fit based on profile analysis.',
                    'points': [
                        {'type': 'valueprop', 'title': 'Decision Maker Access', 
                         'detail': f"{contact.get('name')} - {contact.get('title')}", 'impact': 'Direct path to buyer'},
                        {'type': 'painpoint', 'title': 'Company Profile Match',
                         'detail': f"{contact.get('company')} fits target profile", 'impact': 'High solution need'}
                    ]
                },
                'playbook_configured': True
            }
        })
    except Exception as e:
        logger.error(f"icp_match error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ACTIVITIES (with data wrapper for frontend)
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/activities', methods=['GET'])
def get_contact_activities(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Check activities table
        cursor.execute('''
            SELECT id, activity_type as type, activity_date as timestamp, notes, outcome
            FROM activities WHERE contact_id = %s ORDER BY activity_date DESC
        ''', (contact_id,))
        activities = [safe_dict(row) for row in cursor.fetchall()]
        
        # Build from contact metadata if no activities
        if not activities:
            cursor.execute('''
                SELECT created_at, enriched_at, last_scored, last_contacted, times_contacted,
                       cadence_started_at, cadence_status
                FROM contacts WHERE id = %s
            ''', (contact_id,))
            contact = cursor.fetchone()
            
            if contact:
                if contact.get('created_at'):
                    activities.append({'type': 'created', 'timestamp': str(contact['created_at']), 'description': 'Contact added'})
                if contact.get('enriched_at'):
                    activities.append({'type': 'enrichment', 'timestamp': str(contact['enriched_at']), 'description': 'Profile enriched'})
                if contact.get('last_contacted'):
                    activities.append({'type': 'contact', 'timestamp': str(contact['last_contacted']), 
                                      'description': f"Contacted {contact.get('times_contacted', 0)}x"})
                if contact.get('cadence_started_at'):
                    activities.append({'type': 'cadence', 'timestamp': str(contact['cadence_started_at']),
                                      'description': f"Enrolled in cadence"})
        
        conn.close()
        return jsonify({'data': activities})
    except Exception as e:
        logger.error(f"activities error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENRICHMENT
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {CONTACT_COLUMNS} FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return jsonify({'error': 'Not found'}), 404
        
        cursor.execute("UPDATE contacts SET enrichment_status = 'processing' WHERE id = %s", (contact_id,))
        conn.commit()
        
        if not PERPLEXITY_API_KEY:
            cursor.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s", (contact_id,))
            conn.commit()
            conn.close()
            return jsonify({'error': 'Perplexity API not configured'}), 503
        
        name = contact.get('name') or ''
        title = contact.get('title') or ''
        company = contact.get('company') or ''
        
        # Research
        profile_text = ""
        try:
            person_result = call_perplexity(f"Research {name}, {title} at {company}. Career history, achievements, LinkedIn activity.")
            company_result = call_perplexity(f"Research {company}. Overview, employees, products, competitors, news.")
            
            profile_text = f"""=== PERSON RESEARCH: {name} ===
{person_result or 'No data'}

=== COMPANY RESEARCH: {company} ===
{company_result or 'No data'}
"""
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
        
        scores = calculate_scores(contact, profile_text)
        
        cursor.execute('''
            UPDATE contacts SET
                enrichment_data = %s, enriched = 1, enriched_at = NOW(),
                enrichment_status = 'completed', match_score = %s, match_tier = %s,
                fit_score = %s, relevance_score = %s, timing_score = %s, last_scored = NOW()
            WHERE id = %s
        ''', (profile_text, scores['match_score'], scores['match_tier'],
              scores['fit_score'], scores['relevance_score'], scores['timing_score'], contact_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'contact_id': contact_id, 'scores': scores})
    except Exception as e:
        logger.error(f"enrich error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/enrichment-status', methods=['GET'])
def get_enrichment_status(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT enrichment_status, enriched_at FROM contacts WHERE id = %s', (contact_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'status': row.get('enrichment_status') or 'pending', 'last_enriched': str(row.get('enriched_at') or '')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def call_perplexity(query):
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}", "Content-Type": "application/json"},
            json={"model": "sonar", "messages": [
                {"role": "system", "content": "Professional research analyst."},
                {"role": "user", "content": query}
            ], "temperature": 0.1},
            timeout=90
        )
        if response.status_code == 200:
            return response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        return None
    except:
        return None

def calculate_scores(contact, enrichment_data):
    score = 50
    title = str(contact.get('title') or '').lower()
    enrichment = str(enrichment_data).lower()
    
    if any(t in title for t in ['ceo', 'chief', 'president', 'owner']):
        score += 25
    elif any(t in title for t in ['vp', 'vice president', 'director']):
        score += 20
    elif any(t in title for t in ['manager', 'head']):
        score += 15
    
    if any(w in enrichment for w in ['growing', 'expansion', 'funding', 'hiring']):
        score += 10
    if any(w in enrichment for w in ['challenge', 'struggle', 'need']):
        score += 10
    
    score = min(100, score)
    tier = 'HIGH' if score >= 80 else 'MEDIUM' if score >= 60 else 'LOW' if score >= 40 else 'MINIMAL'
    
    return {
        'match_score': score, 'match_tier': tier,
        'fit_score': score * 0.9, 'relevance_score': score * 0.85, 'timing_score': score * 0.7
    }

# ============================================================================
# SCORING
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/score', methods=['POST'])
def score_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {CONTACT_COLUMNS} FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return jsonify({'error': 'Not found'}), 404
        
        scores = calculate_scores(contact, contact.get('enrichment_data') or '')
        
        cursor.execute('''
            UPDATE contacts SET match_score = %s, match_tier = %s,
                fit_score = %s, relevance_score = %s, timing_score = %s, last_scored = NOW()
            WHERE id = %s
        ''', (scores['match_score'], scores['match_tier'], scores['fit_score'],
              scores['relevance_score'], scores['timing_score'], contact_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'scores': scores})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch/rescore', methods=['POST'])
def batch_rescore():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, title, company, enrichment_data FROM contacts")
        
        updated = 0
        for contact in cursor.fetchall():
            scores = calculate_scores(contact, contact.get('enrichment_data') or '')
            cursor.execute('UPDATE contacts SET match_score = %s, match_tier = %s WHERE id = %s',
                          (scores['match_score'], scores['match_tier'], contact['id']))
            updated += 1
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'updated': updated})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# CADENCES
# ============================================================================
@app.route('/api/cadences', methods=['GET'])
def get_cadences():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cadences ORDER BY id')
        cadences = []
        for row in cursor.fetchall():
            c = safe_dict(row)
            if c.get('steps'):
                try:
                    c['steps'] = json.loads(c['steps'])
                except:
                    pass
            cadences.append(c)
        conn.close()
        return jsonify({'cadences': cadences})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cadences/<int:cadence_id>', methods=['GET'])
def get_cadence(cadence_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cadences WHERE id = %s', (cadence_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            c = safe_dict(row)
            if c.get('steps'):
                try:
                    c['steps'] = json.loads(c['steps'])
                except:
                    pass
            return jsonify(c)
        return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/enroll', methods=['POST'])
def enroll_contact(contact_id):
    try:
        data = request.json
        cadence_id = data.get('cadence_id')
        
        if not cadence_id:
            return jsonify({'error': 'cadence_id required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, status FROM cadence_enrollments WHERE contact_id = %s AND cadence_id = %s',
                      (contact_id, cadence_id))
        existing = cursor.fetchone()
        
        if existing and existing['status'] == 'active':
            conn.close()
            return jsonify({'error': 'Already enrolled'}), 400
        
        if existing:
            cursor.execute('''UPDATE cadence_enrollments SET status = 'active', current_step = 0, 
                             started_at = NOW(), next_action_date = CURRENT_DATE WHERE id = %s''', (existing['id'],))
            enrollment_id = existing['id']
        else:
            cursor.execute('''INSERT INTO cadence_enrollments (contact_id, cadence_id, next_action_date)
                             VALUES (%s, %s, CURRENT_DATE) RETURNING id''', (contact_id, cadence_id))
            enrollment_id = cursor.fetchone()['id']
        
        cursor.execute('''UPDATE contacts SET cadence_id = %s, cadence_status = 'active', 
                         cadence_started_at = NOW() WHERE id = %s''', (cadence_id, contact_id))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'enrollment_id': enrollment_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/enrollments', methods=['GET'])
def get_contact_enrollments(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.*, c.name as cadence_name, c.steps as cadence_steps
            FROM cadence_enrollments e JOIN cadences c ON e.cadence_id = c.id
            WHERE e.contact_id = %s ORDER BY e.started_at DESC
        ''', (contact_id,))
        
        enrollments = []
        for row in cursor.fetchall():
            e = safe_dict(row)
            if e.get('cadence_steps'):
                try:
                    e['cadence_steps'] = json.loads(e['cadence_steps'])
                except:
                    pass
            enrollments.append(e)
        
        conn.close()
        return jsonify({'enrollments': enrollments})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enrollments/<int:enrollment_id>/advance', methods=['POST'])
def advance_enrollment(enrollment_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT e.*, c.steps FROM cadence_enrollments e
                         JOIN cadences c ON e.cadence_id = c.id WHERE e.id = %s''', (enrollment_id,))
        enrollment = cursor.fetchone()
        
        if not enrollment:
            conn.close()
            return jsonify({'error': 'Not found'}), 404
        
        steps = json.loads(enrollment['steps']) if enrollment.get('steps') else []
        current = enrollment['current_step']
        
        if current >= len(steps) - 1:
            cursor.execute('UPDATE cadence_enrollments SET status = %s, completed_at = NOW() WHERE id = %s',
                          ('completed', enrollment_id))
        else:
            cursor.execute('UPDATE cadence_enrollments SET current_step = %s WHERE id = %s',
                          (current + 1, enrollment_id))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cadence-queue', methods=['GET'])
def get_cadence_queue():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.id as enrollment_id, e.contact_id, e.current_step, e.next_action_date,
                   c.name as cadence_name, c.steps as cadence_steps,
                   ct.name as contact_name, ct.email, ct.company, ct.title, ct.match_score
            FROM cadence_enrollments e
            JOIN cadences c ON e.cadence_id = c.id
            JOIN contacts ct ON e.contact_id = ct.id
            WHERE e.status = 'active'
            ORDER BY e.next_action_date ASC NULLS LAST
        ''')
        
        queue = []
        for row in cursor.fetchall():
            item = safe_dict(row)
            if item.get('cadence_steps'):
                try:
                    steps = json.loads(item['cadence_steps'])
                    idx = item.get('current_step', 0)
                    if idx < len(steps):
                        item['current_action'] = steps[idx]
                    item['total_steps'] = len(steps)
                except:
                    pass
            if 'cadence_steps' in item:
                del item['cadence_steps']
            queue.append(item)
        
        conn.close()
        return jsonify({'queue': queue})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# COLD CALL QUEUE
# ============================================================================
@app.route('/api/cold-call/queue', methods=['GET'])
def get_cold_queue():
    try:
        conn = get_db()
        cursor = conn.cursor()
        limit = request.args.get('limit', 50, type=int)
        
        cursor.execute('SELECT * FROM cold_call_queue ORDER BY priority DESC, created_at DESC LIMIT %s', (limit,))
        queue = [safe_dict(row) for row in cursor.fetchall()]
        
        cursor.execute('''SELECT COUNT(*) as total,
            SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new,
            SUM(CASE WHEN status = 'attempted' THEN 1 ELSE 0 END) as attempted,
            SUM(CASE WHEN status = 'connected' THEN 1 ELSE 0 END) as connected
            FROM cold_call_queue''')
        stats = safe_dict(cursor.fetchone()) or {}
        
        conn.close()
        return jsonify({'queue': queue, 'stats': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cold-call/queue', methods=['POST'])
def add_to_cold_queue():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''INSERT INTO cold_call_queue (name, phone, mobile, email, company, title, source, notes, priority)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                      (data.get('name'), data.get('phone'), data.get('mobile'), data.get('email'),
                       data.get('company'), data.get('title'), data.get('source', 'manual'),
                       data.get('notes'), data.get('priority', 0)))
        
        new_id = cursor.fetchone()['id']
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': new_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cold-call/queue/<int:queue_id>/attempt', methods=['POST'])
def log_cold_attempt(queue_id):
    try:
        data = request.json or {}
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''UPDATE cold_call_queue SET attempts = attempts + 1, last_attempt = NOW(),
                         outcome = %s, status = 'attempted' WHERE id = %s''', (data.get('outcome'), queue_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cold-call/queue/<int:queue_id>/status', methods=['PUT'])
def update_cold_status(queue_id):
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE cold_call_queue SET status = %s WHERE id = %s', (data.get('status'), queue_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cold-call/queue/<int:queue_id>/promote', methods=['POST'])
def promote_cold_contact(queue_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cold_call_queue WHERE id = %s', (queue_id,))
        item = cursor.fetchone()
        
        if not item:
            conn.close()
            return jsonify({'error': 'Not found'}), 404
        
        cursor.execute('''INSERT INTO contacts (name, email, phone, company, title, source, created_at)
                         VALUES (%s, %s, %s, %s, %s, 'cold_call', NOW()) RETURNING id''',
                      (item['name'], item['email'], item['phone'] or item['mobile'], item['company'], item['title']))
        contact_id = cursor.fetchone()['id']
        
        cursor.execute('UPDATE cold_call_queue SET contact_id = %s, status = %s WHERE id = %s',
                      (contact_id, 'promoted', queue_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'contact_id': contact_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# WHY ME
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/why-me', methods=['GET'])
def get_why_me(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contact_match WHERE contact_id = %s', (contact_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return jsonify(safe_dict(row))
        return jsonify({'error': 'Not generated yet'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/why-me', methods=['POST'])
def generate_why_me(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name, title, company FROM contacts WHERE id = %s', (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return jsonify({'error': 'Not found'}), 404
        
        why_me = {
            'hook': f"Your expertise as {contact.get('title')} at {contact.get('company')} aligns perfectly.",
            'why_now': "Current market conditions make this ideal timing.",
            'suggested_opening': f"Hi {(contact.get('name') or '').split()[0] or 'there'}, I noticed your work at {contact.get('company')}...",
            'talking_points': json.dumps(["Industry challenges we solve", "Recent success stories", "Time-sensitive opportunity"])
        }
        
        cursor.execute('''INSERT INTO contact_match (contact_id, hook, why_now, suggested_opening, talking_points)
                         VALUES (%s, %s, %s, %s, %s)
                         ON CONFLICT (contact_id) DO UPDATE SET
                         hook = EXCLUDED.hook, why_now = EXCLUDED.why_now,
                         suggested_opening = EXCLUDED.suggested_opening, talking_points = EXCLUDED.talking_points,
                         generated_at = NOW()''',
                      (contact_id, why_me['hook'], why_me['why_now'], why_me['suggested_opening'], why_me['talking_points']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'why_me': why_me})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MEETING PREP
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/meeting-prep', methods=['GET'])
def get_meeting_prep(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name, title, company, enrichment_data FROM contacts WHERE id = %s', (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Not found'}), 404
        
        name = contact.get('name') or 'Contact'
        company = contact.get('company') or 'their company'
        title = contact.get('title') or ''
        
        prep = {
            'contact_summary': {'name': name, 'title': title, 'company': company},
            'key_talking_points': [
                f"Discuss {name}'s priorities as {title}",
                f"Explore challenges at {company}",
                "Share relevant case studies"
            ],
            'questions_to_ask': [
                f"What's your top priority at {company} this quarter?",
                "What challenges are you facing?",
                "How are you currently addressing those?"
            ],
            'recommended_duration': '30 minutes'
        }
        return jsonify({'prep': prep})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# AI GENERATION
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/generate-outreach', methods=['POST'])
def generate_outreach(contact_id):
    try:
        data = request.json or {}
        channel = data.get('channel', 'email')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name, title, company FROM contacts WHERE id = %s', (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Not found'}), 404
        
        name = contact.get('name') or 'there'
        company = contact.get('company') or 'your company'
        first = name.split()[0] if name else 'there'
        
        if channel == 'email':
            outreach = {
                'subject': f"Quick question about {company}",
                'opening': f"Hi {first},",
                'body': f"I noticed your work at {company} and thought there might be synergy to discuss.",
                'cta': "Would you be open to a 15-minute call this week?"
            }
        else:
            outreach = {
                'message': f"Hi {first}, noticed your work at {company}. Would love to connect!",
                'cta': "Open to connecting?"
            }
        
        return jsonify({'success': True, 'outreach': outreach, 'meta': {'channel': channel, 'generated_at': datetime.now().isoformat()}})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/generate-email', methods=['POST'])
def generate_email(contact_id):
    if not request.json:
        request.json = {}
    request.json['channel'] = 'email'
    return generate_outreach(contact_id)

@app.route('/api/contacts/<int:contact_id>/generate-linkedin', methods=['POST'])
def generate_linkedin(contact_id):
    if not request.json:
        request.json = {}
    request.json['channel'] = 'linkedin'
    return generate_outreach(contact_id)

@app.route('/api/contacts/<int:contact_id>/generate-sequence', methods=['POST'])
def generate_sequence(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name, company FROM contacts WHERE id = %s', (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Not found'}), 404
        
        name = contact.get('name') or 'there'
        company = contact.get('company') or 'your company'
        first = name.split()[0] if name else 'there'
        
        sequence = [
            {'subject': f"Quick idea for {company}", 'body': f"Hi {first}, noticed {company} and thought of a fit.", 'cta': "Worth a chat?", 'send_day': "Day 1"},
            {'subject': "Following up", 'body': f"Hi {first}, wanted to follow up. Happy to share how we've helped similar companies.", 'cta': "15 minutes?", 'send_day': "Day 4"},
            {'subject': "Should I close the loop?", 'body': f"Hi {first}, I'll assume timing isn't right if I don't hear back.", 'cta': "Let me know?", 'send_day': "Day 7"}
        ]
        
        return jsonify({'success': True, 'sequence': sequence})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/generate-call-script', methods=['POST'])
def generate_call_script(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT name, title, company FROM contacts WHERE id = %s', (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Not found'}), 404
        
        name = contact.get('name') or 'there'
        company = contact.get('company') or 'your company'
        first = name.split()[0] if name else 'there'
        
        script = {
            'opener': f"Hi {first}, this is [Name] from [Company]. Did I catch you at a good time?",
            'value_statement': f"We help companies like {company} with [key benefit].",
            'discovery_questions': [
                f"What's your biggest challenge at {company}?",
                "How are you currently addressing that?",
                "What would success look like?"
            ],
            'objection_handlers': {
                'no_time': "When would be better for a 10-minute call?",
                'not_interested': "Fair enough. Mind if I ask what you're currently using?",
                'send_info': "Happy to. What's most relevant to you?"
            },
            'meeting_ask': "Would 15 minutes next week work to explore this?"
        }
        
        return jsonify({'success': True, 'script': script})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# AI COMMAND
# ============================================================================
@app.route('/api/ai/command', methods=['POST'])
def ai_command():
    data = request.json or {}
    command = data.get('command', '').lower()
    
    if 'enrich' in command:
        return jsonify({'type': 'action', 'message': 'Select contacts and click Enrich.', 'data': {'action': 'enrich'}})
    elif 'score' in command:
        return jsonify({'type': 'action', 'message': 'Ensure contacts are enriched, then Score.', 'data': {'action': 'score'}})
    elif 'find' in command or 'search' in command:
        return jsonify({'type': 'search', 'message': f'Searching: {command}', 'data': {'query': command}})
    else:
        return jsonify({'type': 'info', 'message': f'Try: "enrich contacts", "find decision makers"', 'data': {}})

# ============================================================================
# ANALYTICS
# ============================================================================
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM contacts')
        total = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
        enriched = cursor.fetchone()['count']
        
        cursor.execute('''SELECT 
            SUM(CASE WHEN match_tier = 'HIGH' THEN 1 ELSE 0 END) as high,
            SUM(CASE WHEN match_tier = 'MEDIUM' THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN match_tier = 'LOW' THEN 1 ELSE 0 END) as low
            FROM contacts''')
        tiers = safe_dict(cursor.fetchone()) or {}
        
        cursor.execute('SELECT AVG(match_score) as avg FROM contacts WHERE match_score IS NOT NULL')
        avg_score = cursor.fetchone()['avg'] or 0
        
        conn.close()
        
        return jsonify({
            'total_contacts': total,
            'enriched_contacts': enriched,
            'tier_distribution': tiers,
            'avg_scores': {'match': float(avg_score)},
            'enrichment_rate': (enriched / total * 100) if total > 0 else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    return get_analytics()

# ============================================================================
# PLAYBOOK
# ============================================================================
@app.route('/api/playbook', methods=['GET'])
def get_playbook():
    try:
        playbook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playbook.json')
        if os.path.exists(playbook_path):
            with open(playbook_path, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({'companyName': 'Your Company', 'tagline': '', 'valueProps': [], 'painPoints': []})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playbook', methods=['POST'])
def save_playbook():
    try:
        data = request.json
        playbook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playbook.json')
        with open(playbook_path, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# USER PROFILE
# ============================================================================
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profile WHERE user_id = 'default'")
        row = cursor.fetchone()
        conn.close()
        return jsonify(safe_dict(row)) if row else jsonify({'user_id': 'default', 'exists': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/profile', methods=['POST', 'PUT'])
def save_user_profile():
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO user_profile (user_id, full_name, role, company)
                         VALUES ('default', %s, %s, %s)
                         ON CONFLICT (user_id) DO UPDATE SET
                         full_name = EXCLUDED.full_name, role = EXCLUDED.role, company = EXCLUDED.company''',
                      (data.get('full_name'), data.get('role'), data.get('company')))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/proof-points', methods=['GET'])
def get_proof_points():
    return jsonify({'user_id': 'default', 'exists': False})

# ============================================================================
# FILTERS & MISC
# ============================================================================
@app.route('/api/filters', methods=['GET'])
def get_filters():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT company FROM contacts WHERE company IS NOT NULL AND company != %s ORDER BY company LIMIT 100', ('',))
        companies = [r['company'] for r in cursor.fetchall()]
        
        cursor.execute('SELECT DISTINCT title FROM contacts WHERE title IS NOT NULL AND title != %s ORDER BY title LIMIT 100', ('',))
        titles = [r['title'] for r in cursor.fetchall()]
        
        cursor.execute('SELECT DISTINCT match_tier FROM contacts WHERE match_tier IS NOT NULL')
        tiers = [r['match_tier'] for r in cursor.fetchall()]
        
        conn.close()
        return jsonify({'companies': companies, 'titles': titles, 'tiers': tiers})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/smart-lists', methods=['GET'])
def get_smart_lists():
    return jsonify({'lists': [
        {'id': 1, 'name': 'High Priority', 'filter': {'tier': 'HIGH'}},
        {'id': 2, 'name': 'Needs Enrichment', 'filter': {'status': 'pending'}},
        {'id': 3, 'name': 'Recently Added', 'filter': {'days': 7}}
    ]})

@app.route('/api/smart-lists/<int:list_id>/contacts', methods=['GET'])
def get_smart_list_contacts(list_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        if list_id == 1:
            cursor.execute(f"SELECT {CONTACT_COLUMNS} FROM contacts WHERE match_tier = 'HIGH' LIMIT 50")
        elif list_id == 2:
            cursor.execute(f"SELECT {CONTACT_COLUMNS} FROM contacts WHERE enrichment_status IS NULL LIMIT 50")
        else:
            cursor.execute(f"SELECT {CONTACT_COLUMNS} FROM contacts ORDER BY created_at DESC NULLS LAST LIMIT 50")
        
        contacts = [safe_dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'contacts': contacts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MAIN - MUST BE LAST
# ============================================================================
if __name__ == '__main__':
    logger.info(f"Starting Apex API on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
