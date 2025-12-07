#!/usr/bin/env python3
"""
APEX Sales Intelligence - Production API
Railway-deployable Flask backend with PostgreSQL
Version: 2.0.0 | December 7, 2025
"""

import os
import sys
import json
import re
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import logging
import traceback

# ============================================================================
# CONFIGURATION - All environment-based, no hardcoded paths
# ============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL')
PORT = int(os.environ.get('PORT', 8000))
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

logger.info(f"🔧 Database: {'✅ Connected' if DATABASE_URL else '❌ Missing DATABASE_URL'}")
logger.info(f"🔧 Perplexity: {'✅' if PERPLEXITY_API_KEY else '❌'}")
logger.info(f"🔧 OpenAI: {'✅' if OPENAI_API_KEY else '❌'}")

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
def get_db():
    """Get PostgreSQL connection with RealDictCursor."""
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = RealDictCursor
    return conn

def ensure_tables():
    """Ensure all required tables and columns exist."""
    conn = get_db()
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Contact columns to add if missing
    contact_cols = [
        ('mdcp_score', 'REAL'), ('mdcp_tier', 'TEXT'),
        ('match_score', 'REAL'), ('match_tier', 'TEXT'),
        ('fit_score', 'REAL'), ('relevance_score', 'REAL'), ('timing_score', 'REAL'),
        ('enrichment_status', 'TEXT'), ('enrichment_data', 'TEXT'),
        ('enriched', 'INTEGER'), ('enriched_at', 'TEXT'), ('last_scored', 'TEXT'),
        ('why_me_data', 'TEXT'), ('why_me_generated_at', 'TEXT'),
        ('persona', 'TEXT'), ('persona_confidence', 'INTEGER'),
        ('cadence_id', 'INTEGER'), ('cadence_status', 'TEXT'), ('cadence_started_at', 'TEXT'),
        ('times_contacted', 'INTEGER'), ('last_contacted', 'TEXT'),
        ('call_script_1', 'TEXT'), ('call_script_2', 'TEXT'), ('call_script_3', 'TEXT'),
        ('email_1_body', 'TEXT'), ('email_2_body', 'TEXT'), ('email_3_body', 'TEXT'),
        ('icp_score', 'REAL'), ('icp_tier', 'TEXT'), ('match_reasons', 'TEXT'),
    ]
    
    for col, typ in contact_cols:
        try:
            cursor.execute(f'ALTER TABLE contacts ADD COLUMN {col} {typ}')
            logger.info(f"  Added column: {col}")
        except:
            pass
    
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
    
    # Contact match / Why Me data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_match (
            id SERIAL PRIMARY KEY,
            contact_id INTEGER UNIQUE NOT NULL,
            user_id TEXT DEFAULT 'default',
            match_score REAL,
            fit_score REAL,
            relevance_score REAL,
            timing_score REAL,
            match_tier TEXT,
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
    
    # Activities table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id SERIAL PRIMARY KEY,
            contact_id INTEGER NOT NULL,
            activity_type TEXT,
            activity_date TIMESTAMP DEFAULT NOW(),
            notes TEXT,
            outcome TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    # Insert default cadences if empty
    cursor.execute('SELECT COUNT(*) FROM cadences')
    if cursor.fetchone()[0] == 0:
        default_cadences = [
            ('New Lead Intro', 'Initial outreach sequence for new leads', 
             json.dumps([
                 {"day": 1, "channel": "email", "template": "intro", "title": "Introduction Email"},
                 {"day": 3, "channel": "linkedin", "template": "connection", "title": "LinkedIn Connect"},
                 {"day": 5, "channel": "email", "template": "value_add", "title": "Value-Add Email"},
                 {"day": 7, "channel": "call", "template": "discovery", "title": "Discovery Call"},
                 {"day": 10, "channel": "email", "template": "meeting_request", "title": "Meeting Request"}
             ]), 10),
            ('Re-engagement', 'Wake up cold leads',
             json.dumps([
                 {"day": 1, "channel": "email", "template": "breakup", "title": "Break-up Email"},
                 {"day": 4, "channel": "linkedin", "template": "insight", "title": "Share Insight"},
                 {"day": 7, "channel": "email", "template": "case_study", "title": "Case Study"}
             ]), 7),
            ('Meeting Follow-up', 'Post-meeting nurture',
             json.dumps([
                 {"day": 1, "channel": "email", "template": "thank_you", "title": "Thank You"},
                 {"day": 3, "channel": "email", "template": "resources", "title": "Helpful Resources"},
                 {"day": 5, "channel": "call", "template": "check_in", "title": "Check-in Call"}
             ]), 5)
        ]
        for name, desc, steps, days in default_cadences:
            cursor.execute(
                'INSERT INTO cadences (name, description, steps, duration_days) VALUES (%s, %s, %s, %s)',
                (name, desc, steps, days)
            )
    
    conn.close()
    logger.info("✅ Database tables verified")

# Initialize tables on startup
try:
    ensure_tables()
except Exception as e:
    logger.error(f"❌ Table setup error: {e}")

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
        'version': '2.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat()
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
# CONTACTS - CRUD
# ============================================================================
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    conn = get_db()
    cursor = conn.cursor()
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    search = request.args.get('search', '')
    tier = request.args.get('tier', '')
    
    query = 'SELECT * FROM contacts WHERE 1=1'
    params = []
    
    if search:
        query += ' AND (name ILIKE %s OR email ILIKE %s OR company ILIKE %s)'
        search_param = f'%{search}%'
        params.extend([search_param, search_param, search_param])
    
    if tier:
        query += ' AND match_tier = %s'
        params.append(tier)
    
    query += ' ORDER BY match_score DESC NULLS LAST, id DESC LIMIT %s OFFSET %s'
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    contacts = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('SELECT COUNT(*) FROM contacts')
    total = cursor.fetchone()[0]
    
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
    return jsonify({'error': 'Contact not found'}), 404

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO contacts (name, email, company, title, phone)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    ''', (
        data.get('name'),
        data.get('email'),
        data.get('company'),
        data.get('title'),
        data.get('phone')
    ))
    
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': new_id})

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    # Build dynamic update
    fields = []
    values = []
    for key in ['name', 'email', 'company', 'title', 'phone', 'notes']:
        if key in data:
            fields.append(f'{key} = %s')
            values.append(data[key])
    
    if fields:
        values.append(contact_id)
        cursor.execute(f"UPDATE contacts SET {', '.join(fields)} WHERE id = %s", values)
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM contacts WHERE id = %s', (contact_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ============================================================================
# CONTACTS - IMPORT
# ============================================================================
@app.route('/api/contacts/import', methods=['POST'])
def import_contacts():
    data = request.json
    contacts = data.get('contacts', [])
    
    conn = get_db()
    cursor = conn.cursor()
    
    success = 0
    failed = 0
    
    for c in contacts:
        try:
            cursor.execute('''
                INSERT INTO contacts (name, email, company, title, phone)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET
                    name = EXCLUDED.name,
                    company = EXCLUDED.company,
                    title = EXCLUDED.title
            ''', (
                c.get('name'),
                c.get('email'),
                c.get('company'),
                c.get('title'),
                c.get('phone')
            ))
            success += 1
        except Exception as e:
            logger.error(f"Import error: {e}")
            failed += 1
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': success, 'failed': failed})

@app.route('/api/import/status', methods=['GET'])
def import_status():
    return jsonify({'status': 'complete', 'message': 'No active import'})

# ============================================================================
# ICP MATCH - Frontend-compatible with data wrapper
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/icp-match', methods=['GET'])
def get_icp_match(contact_id):
    """Frontend-compatible ICP match - returns nested structure with data wrapper."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, company, title, match_score, match_tier, 
                   fit_score, relevance_score, timing_score, icp_score, icp_tier, match_reasons
            FROM contacts WHERE id = %s
        ''', (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        score = float(contact.get('match_score') or contact.get('icp_score') or 0)
        tier = contact.get('match_tier') or contact.get('icp_tier') or 'UNSCORED'
        
        # Build reasons
        reasons = []
        if contact.get('match_reasons'):
            try:
                reasons = json.loads(contact['match_reasons'])
            except:
                reasons = [contact['match_reasons']]
        
        if not reasons:
            if contact.get('fit_score', 0) and contact['fit_score'] > 70:
                reasons.append('Strong company/role fit')
            if contact.get('relevance_score', 0) and contact['relevance_score'] > 70:
                reasons.append('High service relevance')
            if contact.get('timing_score', 0) and contact['timing_score'] > 70:
                reasons.append('Positive timing signals')
            title_lower = str(contact.get('title', '')).lower()
            if any(kw in title_lower for kw in ['director', 'vp', 'chief', 'head', 'owner', 'president']):
                reasons.append('Decision-maker title')
            if not reasons:
                reasons = ['Matches basic ICP criteria']
        
        # Determine match level
        if score >= 80:
            match_level = 'PERFECT'
        elif score >= 60:
            match_level = 'GOOD'
        elif score >= 40:
            match_level = 'OKAY'
        else:
            match_level = 'LOW'
        
        # Return with data wrapper (frontend expects this)
        return jsonify({
            'data': {
                'contact_id': contact_id,
                'icp_match': {
                    'score': score,
                    'reasons': reasons,
                    'match_level': match_level
                },
                'why_us_fit': {
                    'summary': f'{match_level.lower().capitalize()} fit based on profile analysis.',
                    'points': [
                        {'type': 'valueprop', 'title': 'Decision Maker Access', 
                         'detail': f"{contact.get('name')} holds {contact.get('title')}", 'impact': 'Direct path to buyer'},
                        {'type': 'painpoint', 'title': 'Company Profile Match',
                         'detail': f"{contact.get('company')} fits target profile", 'impact': 'High solution need'}
                    ]
                },
                'playbook_configured': True
            }
        })
    except Exception as e:
        logger.error(f"ICP match error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ACTIVITIES - Frontend-compatible with data wrapper
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/activities', methods=['GET'])
def get_contact_activities(contact_id):
    """Frontend-compatible activities endpoint with data wrapper."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get activities from activities table
        cursor.execute('''
            SELECT id, activity_type as type, activity_date as timestamp, notes, outcome
            FROM activities 
            WHERE contact_id = %s 
            ORDER BY activity_date DESC
        ''', (contact_id,))
        activities = [dict(row) for row in cursor.fetchall()]
        
        # Also build from contact metadata if no activities
        if not activities:
            cursor.execute('''
                SELECT created_at, enriched_at, last_scored, last_contacted, 
                       times_contacted, cadence_started_at, cadence_status
                FROM contacts WHERE id = %s
            ''', (contact_id,))
            contact = cursor.fetchone()
            
            if contact:
                if contact.get('created_at'):
                    activities.append({
                        'type': 'created',
                        'timestamp': str(contact['created_at']),
                        'description': 'Contact added to system'
                    })
                if contact.get('enriched_at'):
                    activities.append({
                        'type': 'enrichment',
                        'timestamp': str(contact['enriched_at']),
                        'description': 'Profile enriched with AI'
                    })
                if contact.get('last_scored'):
                    activities.append({
                        'type': 'scoring',
                        'timestamp': str(contact['last_scored']),
                        'description': 'Contact scored and tiered'
                    })
                if contact.get('last_contacted'):
                    times = contact.get('times_contacted', 0)
                    activities.append({
                        'type': 'contact',
                        'timestamp': str(contact['last_contacted']),
                        'description': f'Contacted {times}x total'
                    })
                if contact.get('cadence_started_at'):
                    activities.append({
                        'type': 'cadence',
                        'timestamp': str(contact['cadence_started_at']),
                        'description': f"Enrolled in cadence ({contact.get('cadence_status', 'active')})"
                    })
        
        conn.close()
        
        # Return with data wrapper (frontend expects this)
        return jsonify({'data': activities})
        
    except Exception as e:
        logger.error(f"Activities error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENRICHMENT
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    """Enrich contact with Perplexity AI research."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = %s', (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return jsonify({'error': 'Contact not found'}), 404
        
        # Mark as processing
        cursor.execute("UPDATE contacts SET enrichment_status = 'processing' WHERE id = %s", (contact_id,))
        conn.commit()
        
        if not PERPLEXITY_API_KEY:
            cursor.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s", (contact_id,))
            conn.commit()
            conn.close()
            return jsonify({'error': 'Perplexity API key not configured'}), 503
        
        # Build enrichment queries
        name = contact.get('name', '')
        title = contact.get('title', '')
        company = contact.get('company', '')
        
        # Research the person
        try:
            person_query = f"Research {name}, {title} at {company}. Find: career history, education, achievements, LinkedIn activity."
            person_result = call_perplexity(person_query)
            
            company_query = f"Research {company} as a business. Find: overview, employees, revenue, products, competitors."
            company_result = call_perplexity(company_query)
            
            profile_text = f"""=== PERSON RESEARCH: {name} ===
{person_result or 'No data available'}

=== COMPANY RESEARCH: {company} ===
{company_result or 'No data available'}
"""
            
            # Score the contact
            scores = calculate_scores(contact, profile_text)
            
            # Update database
            cursor.execute('''
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
            ''', (
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
                'profile_length': len(profile_text),
                'scores': scores
            })
            
        except Exception as e:
            cursor.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s", (contact_id,))
            conn.commit()
            conn.close()
            raise e
            
    except Exception as e:
        logger.error(f"Enrichment error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/enrichment-status', methods=['GET'])
def get_enrichment_status(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT enrichment_status, enriched_at FROM contacts WHERE id = %s', (contact_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': 'Not found'}), 404
    return jsonify({'status': row.get('enrichment_status') or 'pending', 'last_enriched': row.get('enriched_at')})

def call_perplexity(query):
    """Call Perplexity API for research."""
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json"
            },
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

def calculate_scores(contact, enrichment_data):
    """Calculate ICP match scores."""
    score = 50  # Base score
    
    title = str(contact.get('title', '')).lower()
    company = str(contact.get('company', '')).lower()
    enrichment = str(enrichment_data).lower()
    
    # Title scoring
    if any(t in title for t in ['ceo', 'chief', 'president', 'owner']):
        score += 25
    elif any(t in title for t in ['vp', 'vice president', 'director']):
        score += 20
    elif any(t in title for t in ['manager', 'head']):
        score += 15
    
    # Company signals
    if any(w in enrichment for w in ['growing', 'expansion', 'funding', 'hiring']):
        score += 10
    
    # Pain point signals
    if any(w in enrichment for w in ['challenge', 'struggle', 'need', 'looking for']):
        score += 10
    
    score = min(100, score)
    
    # Determine tier
    if score >= 80:
        tier = 'HIGH'
    elif score >= 60:
        tier = 'MEDIUM'
    elif score >= 40:
        tier = 'LOW'
    else:
        tier = 'MINIMAL'
    
    return {
        'match_score': score,
        'match_tier': tier,
        'fit_score': score * 0.9,
        'relevance_score': score * 0.85,
        'timing_score': score * 0.7
    }

# ============================================================================
# SCORING
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/score', methods=['POST'])
def score_contact(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = %s', (contact_id,))
    contact = cursor.fetchone()
    
    if not contact:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    
    enrichment = contact.get('enrichment_data', '') or ''
    scores = calculate_scores(contact, enrichment)
    
    cursor.execute('''
        UPDATE contacts SET
            match_score = %s, match_tier = %s,
            fit_score = %s, relevance_score = %s, timing_score = %s,
            last_scored = %s
        WHERE id = %s
    ''', (
        scores['match_score'], scores['match_tier'],
        scores['fit_score'], scores['relevance_score'], scores['timing_score'],
        datetime.now().isoformat(), contact_id
    ))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'scores': scores})

@app.route('/api/batch/rescore', methods=['POST'])
def batch_rescore():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, company, enrichment_data FROM contacts')
    contacts = cursor.fetchall()
    
    updated = 0
    for contact in contacts:
        scores = calculate_scores(contact, contact.get('enrichment_data', ''))
        cursor.execute('''
            UPDATE contacts SET match_score = %s, match_tier = %s, last_scored = %s WHERE id = %s
        ''', (scores['match_score'], scores['match_tier'], datetime.now().isoformat(), contact['id']))
        updated += 1
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'updated': updated})

# ============================================================================
# CADENCES
# ============================================================================
@app.route('/api/cadences', methods=['GET'])
def get_cadences():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cadences ORDER BY id')
    cadences = []
    for row in cursor.fetchall():
        c = dict(row)
        if c.get('steps'):
            try:
                c['steps'] = json.loads(c['steps'])
            except:
                pass
        cadences.append(c)
    conn.close()
    return jsonify({'cadences': cadences})

@app.route('/api/cadences/<int:cadence_id>', methods=['GET'])
def get_cadence(cadence_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cadences WHERE id = %s', (cadence_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        c = dict(row)
        if c.get('steps'):
            try:
                c['steps'] = json.loads(c['steps'])
            except:
                pass
        return jsonify(c)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/contacts/<int:contact_id>/enroll', methods=['POST'])
def enroll_contact(contact_id):
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
    
    if existing and existing['status'] == 'active':
        conn.close()
        return jsonify({'error': 'Already enrolled in this cadence'}), 400
    
    if existing:
        cursor.execute('''
            UPDATE cadence_enrollments 
            SET status = 'active', current_step = 0, started_at = NOW(), next_action_date = CURRENT_DATE
            WHERE id = %s
        ''', (existing['id'],))
        enrollment_id = existing['id']
    else:
        cursor.execute('''
            INSERT INTO cadence_enrollments (contact_id, cadence_id, next_action_date)
            VALUES (%s, %s, CURRENT_DATE)
            RETURNING id
        ''', (contact_id, cadence_id))
        enrollment_id = cursor.fetchone()[0]
    
    # Update contact
    cursor.execute('''
        UPDATE contacts SET cadence_id = %s, cadence_status = 'active', cadence_started_at = %s
        WHERE id = %s
    ''', (cadence_id, datetime.now().isoformat(), contact_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'enrollment_id': enrollment_id})

@app.route('/api/contacts/<int:contact_id>/enrollments', methods=['GET'])
def get_contact_enrollments(contact_id):
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
        if e.get('cadence_steps'):
            try:
                e['cadence_steps'] = json.loads(e['cadence_steps'])
            except:
                pass
        enrollments.append(e)
    
    conn.close()
    return jsonify({'enrollments': enrollments})

@app.route('/api/enrollments/<int:enrollment_id>/advance', methods=['POST'])
def advance_enrollment(enrollment_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT e.*, c.steps FROM cadence_enrollments e
        JOIN cadences c ON e.cadence_id = c.id
        WHERE e.id = %s
    ''', (enrollment_id,))
    enrollment = cursor.fetchone()
    
    if not enrollment:
        conn.close()
        return jsonify({'error': 'Enrollment not found'}), 404
    
    steps = json.loads(enrollment['steps']) if enrollment.get('steps') else []
    current_step = enrollment['current_step']
    
    if current_step >= len(steps) - 1:
        cursor.execute('''
            UPDATE cadence_enrollments SET status = 'completed', completed_at = NOW() WHERE id = %s
        ''', (enrollment_id,))
    else:
        next_step = steps[current_step + 1]
        next_date = datetime.now() + timedelta(days=next_step.get('day', 1) - steps[current_step].get('day', 0))
        cursor.execute('''
            UPDATE cadence_enrollments SET current_step = %s, next_action_date = %s WHERE id = %s
        ''', (current_step + 1, next_date.date(), enrollment_id))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/cadence-queue', methods=['GET'])
def get_cadence_queue():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id as enrollment_id, e.contact_id, e.current_step, e.next_action_date,
               c.name as cadence_name, c.steps as cadence_steps,
               ct.name as contact_name, ct.email, ct.company, ct.title, ct.match_score
        FROM cadence_enrollments e
        JOIN cadences c ON e.cadence_id = c.id
        JOIN contacts ct ON e.contact_id = ct.id
        WHERE e.status = 'active' AND e.next_action_date <= CURRENT_DATE
        ORDER BY e.next_action_date ASC, ct.match_score DESC
    ''')
    
    queue = []
    for row in cursor.fetchall():
        item = dict(row)
        if item.get('cadence_steps'):
            try:
                steps = json.loads(item['cadence_steps'])
                current_idx = item['current_step']
                if current_idx < len(steps):
                    item['current_action'] = steps[current_idx]
                item['total_steps'] = len(steps)
                del item['cadence_steps']
            except:
                pass
        queue.append(item)
    
    conn.close()
    return jsonify({'queue': queue})

# ============================================================================
# COLD CALL QUEUE
# ============================================================================
@app.route('/api/cold-call/queue', methods=['GET'])
def get_cold_queue():
    conn = get_db()
    cursor = conn.cursor()
    limit = request.args.get('limit', 50, type=int)
    status = request.args.get('status')
    
    query = 'SELECT * FROM cold_call_queue'
    params = []
    
    if status:
        query += ' WHERE status = %s'
        params.append(status)
    
    query += ' ORDER BY priority DESC, created_at DESC LIMIT %s'
    params.append(limit)
    
    cursor.execute(query, params)
    queue = [dict(row) for row in cursor.fetchall()]
    
    # Stats
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) as new,
            SUM(CASE WHEN status = 'attempted' THEN 1 ELSE 0 END) as attempted,
            SUM(CASE WHEN status = 'connected' THEN 1 ELSE 0 END) as connected,
            SUM(CASE WHEN status = 'meeting_set' THEN 1 ELSE 0 END) as meeting_set
        FROM cold_call_queue
    ''')
    stats_row = cursor.fetchone()
    stats = dict(stats_row) if stats_row else {}
    
    conn.close()
    return jsonify({'queue': queue, 'stats': stats})

@app.route('/api/cold-call/queue', methods=['POST'])
def add_to_cold_queue():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO cold_call_queue (name, phone, mobile, email, company, title, source, notes, priority)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    ''', (
        data.get('name'),
        data.get('phone'),
        data.get('mobile'),
        data.get('email'),
        data.get('company'),
        data.get('title'),
        data.get('source', 'manual'),
        data.get('notes'),
        data.get('priority', 0)
    ))
    
    new_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': new_id})

@app.route('/api/cold-call/queue/<int:queue_id>/attempt', methods=['POST'])
def log_cold_attempt(queue_id):
    data = request.json or {}
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE cold_call_queue 
        SET attempts = attempts + 1, last_attempt = NOW(), 
            outcome = %s, status = 'attempted'
        WHERE id = %s
    ''', (data.get('outcome'), queue_id))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/cold-call/queue/<int:queue_id>/status', methods=['PUT'])
def update_cold_status(queue_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE cold_call_queue SET status = %s WHERE id = %s', 
                   (data.get('status'), queue_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/cold-call/queue/<int:queue_id>/promote', methods=['POST'])
def promote_cold_contact(queue_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM cold_call_queue WHERE id = %s', (queue_id,))
    item = cursor.fetchone()
    
    if not item:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    
    cursor.execute('''
        INSERT INTO contacts (name, email, phone, company, title)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    ''', (item['name'], item['email'], item['phone'] or item['mobile'], 
          item['company'], item['title']))
    
    contact_id = cursor.fetchone()[0]
    
    cursor.execute('UPDATE cold_call_queue SET contact_id = %s, status = %s WHERE id = %s',
                   (contact_id, 'promoted', queue_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'contact_id': contact_id})

# ============================================================================
# WHY ME
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/why-me', methods=['GET'])
def get_why_me(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contact_match WHERE contact_id = %s', (contact_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Not generated yet'}), 404

@app.route('/api/contacts/<int:contact_id>/why-me', methods=['POST'])
def generate_why_me(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = %s', (contact_id,))
    contact = cursor.fetchone()
    
    if not contact:
        conn.close()
        return jsonify({'error': 'Not found'}), 404
    
    # Generate Why Me content
    name = contact.get('name', '')
    title = contact.get('title', '')
    company = contact.get('company', '')
    
    why_me = {
        'hook': f"Your expertise in {title} at {company} aligns with our focus on helping leaders like you.",
        'why_now': "Current market conditions make this an ideal time to explore efficiency improvements.",
        'suggested_opening': f"Hi {name.split()[0] if name else 'there'}, I noticed your work at {company}...",
        'talking_points': json.dumps([
            "Industry-specific challenges we solve",
            "Recent success with similar companies", 
            "Time-sensitive opportunity"
        ])
    }
    
    # Save to database
    cursor.execute('''
        INSERT INTO contact_match (contact_id, hook, why_now, suggested_opening, talking_points, generated_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        ON CONFLICT (contact_id) DO UPDATE SET
            hook = EXCLUDED.hook,
            why_now = EXCLUDED.why_now,
            suggested_opening = EXCLUDED.suggested_opening,
            talking_points = EXCLUDED.talking_points,
            generated_at = NOW()
    ''', (contact_id, why_me['hook'], why_me['why_now'], 
          why_me['suggested_opening'], why_me['talking_points']))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'why_me': why_me})

# ============================================================================
# MEETING PREP
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/meeting-prep', methods=['GET'])
def get_meeting_prep(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = %s', (contact_id,))
    contact = cursor.fetchone()
    conn.close()
    
    if not contact:
        return jsonify({'error': 'Not found'}), 404
    
    name = contact.get('name', 'Contact')
    company = contact.get('company', 'their company')
    title = contact.get('title', 'their role')
    enrichment = contact.get('enrichment_data', '')
    
    prep = {
        'contact_summary': {
            'name': name,
            'title': title,
            'company': company
        },
        'key_talking_points': [
            f"Discuss {name}'s priorities as {title}",
            f"Explore challenges at {company}",
            "Share relevant case studies",
            "Identify next steps"
        ],
        'questions_to_ask': [
            f"What's your top priority at {company} this quarter?",
            "What challenges are you facing in achieving those goals?",
            "How are you currently addressing those challenges?",
            "What would success look like for you?"
        ],
        'company_intel': enrichment[:500] if enrichment else f"Research {company} before the meeting.",
        'recommended_duration': '30 minutes',
        'follow_up_actions': [
            'Send recap email within 24 hours',
            'Share promised resources',
            'Schedule follow-up if interested'
        ]
    }
    
    return jsonify({'prep': prep})

# ============================================================================
# AI GENERATION - Outreach, Email, LinkedIn, Call Scripts
# ============================================================================
@app.route('/api/contacts/<int:contact_id>/generate-outreach', methods=['POST'])
def generate_outreach(contact_id):
    data = request.json or {}
    template = data.get('template', 'intro')
    tone = data.get('tone', 'professional')
    channel = data.get('channel', 'email')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = %s', (contact_id,))
    contact = cursor.fetchone()
    conn.close()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    name = contact.get('name', 'there')
    company = contact.get('company', 'your company')
    title = contact.get('title', '')
    
    # Generate based on channel
    if channel == 'email':
        outreach = {
            'subject': f"Quick question about {company}",
            'opening': f"Hi {name.split()[0] if name else 'there'},",
            'body': f"I came across {company} and noticed your work as {title}. I'd love to share how we've helped similar companies achieve their goals.",
            'cta': "Would you be open to a quick 15-minute call this week?",
            'signature_note': "Looking forward to connecting."
        }
    else:  # linkedin
        outreach = {
            'message': f"Hi {name.split()[0] if name else 'there'}, I noticed your work at {company} and thought we might have some synergy to discuss. Would love to connect!",
            'cta': "Open to connecting?"
        }
    
    return jsonify({
        'success': True,
        'outreach': outreach,
        'meta': {
            'template': template,
            'tone': tone,
            'channel': channel,
            'contact_name': name,
            'company': company,
            'generated_at': datetime.now().isoformat()
        }
    })

@app.route('/api/contacts/<int:contact_id>/generate-email', methods=['POST'])
def generate_email(contact_id):
    return generate_outreach(contact_id)

@app.route('/api/contacts/<int:contact_id>/generate-linkedin', methods=['POST'])
def generate_linkedin(contact_id):
    # Set channel to linkedin and forward
    if request.json is None:
        request.json = {}
    request.json['channel'] = 'linkedin'
    return generate_outreach(contact_id)

@app.route('/api/contacts/<int:contact_id>/generate-sequence', methods=['POST'])
def generate_sequence(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = %s', (contact_id,))
    contact = cursor.fetchone()
    conn.close()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    name = contact.get('name', 'there')
    company = contact.get('company', 'your company')
    
    sequence = [
        {
            'subject': f"Quick idea for {company}",
            'body': f"Hi {name.split()[0] if name else 'there'}, noticed {company} and thought of a potential fit.",
            'cta': "Worth a quick chat?",
            'send_day': "Day 1"
        },
        {
            'subject': "Following up",
            'body': f"Hi {name.split()[0] if name else 'there'}, wanted to follow up on my last note. Happy to share how we've helped similar companies.",
            'cta': "15 minutes this week?",
            'send_day': "Day 4"
        },
        {
            'subject': "Should I close the loop?",
            'body': f"Hi {name.split()[0] if name else 'there'}, I'll assume the timing isn't right if I don't hear back. No worries either way.",
            'cta': "Let me know either way?",
            'send_day': "Day 7"
        }
    ]
    
    return jsonify({
        'success': True,
        'sequence': sequence,
        'contact': {'name': name, 'company': company}
    })

@app.route('/api/contacts/<int:contact_id>/generate-call-script', methods=['POST'])
def generate_call_script(contact_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = %s', (contact_id,))
    contact = cursor.fetchone()
    conn.close()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    name = contact.get('name', 'there')
    company = contact.get('company', 'your company')
    title = contact.get('title', '')
    
    script = {
        'opener': f"Hi {name.split()[0] if name else 'there'}, this is [Your Name] from [Company]. Did I catch you at a good time?",
        'permission_ask': "I'll be brief - I noticed your work at {company} and had a quick question.",
        'value_statement': f"We help {title}s like yourself [key benefit]. I was curious if that's something on your radar.",
        'discovery_questions': [
            f"What's your biggest challenge at {company} right now?",
            "How are you currently addressing that?",
            "What would an ideal solution look like?",
            "Who else would be involved in evaluating something like this?",
            "What's your timeline for making improvements?"
        ],
        'talking_points': [
            "Our unique approach",
            "Relevant case study",
            "ROI metrics",
            "Implementation timeline"
        ],
        'objection_handlers': {
            'no_time': "I understand you're busy. When would be a better time for a 10-minute call?",
            'not_interested': "Fair enough. Mind if I ask what solution you're currently using?",
            'send_info': "Happy to. What specific aspects would be most relevant to you?",
            'have_solution': "Good to hear. How's that working out? Any gaps you've noticed?",
            'no_budget': "Understood. When does your next budget cycle start?"
        },
        'meeting_ask': "Would you be open to a 15-minute call next week to explore this further?",
        'voicemail_script': f"Hi {name.split()[0] if name else 'there'}, this is [Your Name] from [Company]. I was hoping to connect about [value prop]. I'll try you again, but feel free to reach me at [phone]. Thanks!"
    }
    
    return jsonify({
        'success': True,
        'script': script,
        'meta': {
            'contact_name': name,
            'company': company,
            'generated_at': datetime.now().isoformat()
        }
    })

# ============================================================================
# AI COMMAND
# ============================================================================
@app.route('/api/ai/command', methods=['POST'])
def ai_command():
    data = request.json or {}
    command = data.get('command', '')
    
    # Parse command intent
    command_lower = command.lower()
    
    if 'enrich' in command_lower:
        return jsonify({
            'type': 'action',
            'message': 'To enrich contacts, select them and click the Enrich button.',
            'data': {'action': 'enrich'}
        })
    elif 'score' in command_lower:
        return jsonify({
            'type': 'action', 
            'message': 'To score contacts, ensure they are enriched first, then use the Score action.',
            'data': {'action': 'score'}
        })
    elif 'find' in command_lower or 'search' in command_lower:
        return jsonify({
            'type': 'search',
            'message': f'Searching for: {command}',
            'data': {'query': command}
        })
    else:
        return jsonify({
            'type': 'info',
            'message': f'Command received: {command}. Try: "enrich contacts", "find decision makers", "score all"',
            'data': {}
        })

# ============================================================================
# ANALYTICS
# ============================================================================
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    time_range = request.args.get('range', 'all')
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Total contacts
    cursor.execute('SELECT COUNT(*) FROM contacts')
    total_contacts = cursor.fetchone()[0]
    
    # Enriched contacts
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'completed'")
    enriched_contacts = cursor.fetchone()[0]
    
    # Tier distribution
    cursor.execute('''
        SELECT 
            SUM(CASE WHEN match_tier = 'HIGH' THEN 1 ELSE 0 END) as high,
            SUM(CASE WHEN match_tier = 'MEDIUM' THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN match_tier = 'LOW' THEN 1 ELSE 0 END) as low,
            SUM(CASE WHEN match_tier = 'MINIMAL' OR match_tier IS NULL THEN 1 ELSE 0 END) as minimal
        FROM contacts WHERE match_score IS NOT NULL
    ''')
    tier_row = cursor.fetchone()
    tier_distribution = dict(tier_row) if tier_row else {}
    
    # Average scores
    cursor.execute('''
        SELECT AVG(match_score), AVG(fit_score), AVG(relevance_score), AVG(timing_score)
        FROM contacts WHERE match_score IS NOT NULL
    ''')
    avg_row = cursor.fetchone()
    avg_scores = {
        'match': float(avg_row[0] or 0),
        'fit': float(avg_row[1] or 0),
        'relevance': float(avg_row[2] or 0),
        'timing': float(avg_row[3] or 0)
    }
    
    # Top companies
    cursor.execute('''
        SELECT company, COUNT(*) as cnt, AVG(match_score) as avg_score
        FROM contacts WHERE company IS NOT NULL AND company != ''
        GROUP BY company ORDER BY cnt DESC LIMIT 10
    ''')
    top_companies = [{'company': r[0], 'count': r[1], 'avg_score': r[2]} for r in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'total_contacts': total_contacts,
        'enriched_contacts': enriched_contacts,
        'tier_distribution': tier_distribution,
        'avg_scores': avg_scores,
        'top_companies': top_companies,
        'enrichment_rate': (enriched_contacts / total_contacts * 100) if total_contacts > 0 else 0
    })

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    return get_analytics()

# ============================================================================
# PLAYBOOK
# ============================================================================
@app.route('/api/playbook', methods=['GET'])
def get_playbook():
    playbook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playbook.json')
    if os.path.exists(playbook_path):
        with open(playbook_path, 'r') as f:
            return jsonify(json.load(f))
    return jsonify({
        'companyName': 'Your Company',
        'tagline': 'Your value proposition',
        'valueProps': [],
        'painPoints': [],
        'proofPoints': []
    })

@app.route('/api/playbook', methods=['POST'])
def save_playbook():
    data = request.json
    playbook_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playbook.json')
    with open(playbook_path, 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({'success': True})

# ============================================================================
# USER PROFILE
# ============================================================================
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    user_id = request.args.get('user_id', 'default')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_profile WHERE user_id = %s', (user_id,))
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
    
    cursor.execute('''
        INSERT INTO user_profile (user_id, full_name, role, company)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            role = EXCLUDED.role,
            company = EXCLUDED.company
    ''', (user_id, data.get('full_name'), data.get('role'), data.get('company')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'user_id': user_id})

@app.route('/api/user/proof-points', methods=['GET'])
def get_proof_points():
    return jsonify({'user_id': 'default', 'exists': False})

# ============================================================================
# FILTERS & MISC
# ============================================================================
@app.route('/api/filters', methods=['GET'])
def get_filters():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT company FROM contacts WHERE company IS NOT NULL ORDER BY company')
    companies = [r[0] for r in cursor.fetchall()]
    
    cursor.execute('SELECT DISTINCT title FROM contacts WHERE title IS NOT NULL ORDER BY title')
    titles = [r[0] for r in cursor.fetchall()]
    
    cursor.execute('SELECT DISTINCT match_tier FROM contacts WHERE match_tier IS NOT NULL')
    tiers = [r[0] for r in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'companies': companies[:100],
        'titles': titles[:100],
        'tiers': tiers,
        'statuses': ['new', 'enriched', 'scored', 'contacted']
    })

@app.route('/api/smart-lists', methods=['GET'])
def get_smart_lists():
    return jsonify({
        'lists': [
            {'id': 1, 'name': 'High Priority', 'filter': {'tier': 'HIGH'}, 'count': 0},
            {'id': 2, 'name': 'Needs Enrichment', 'filter': {'status': 'pending'}, 'count': 0},
            {'id': 3, 'name': 'Recently Added', 'filter': {'days': 7}, 'count': 0}
        ]
    })

@app.route('/api/smart-lists/<int:list_id>/contacts', methods=['GET'])
def get_smart_list_contacts(list_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if list_id == 1:  # High Priority
        cursor.execute("SELECT * FROM contacts WHERE match_tier = 'HIGH' LIMIT 50")
    elif list_id == 2:  # Needs Enrichment
        cursor.execute("SELECT * FROM contacts WHERE enrichment_status IS NULL OR enrichment_status = 'pending' LIMIT 50")
    else:  # Recently Added
        cursor.execute("SELECT * FROM contacts ORDER BY created_at DESC LIMIT 50")
    
    contacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'contacts': contacts})

# ============================================================================
# MAIN - MUST BE LAST
# ============================================================================
if __name__ == '__main__':
    logger.info(f"🚀 Starting Apex API on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
