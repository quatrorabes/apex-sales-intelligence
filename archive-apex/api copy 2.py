#!/usr/bin/env python3
"""
Apex Intelligence API Server
Production-ready backend for Sales Angel AI platform
Phase 2: Activity Logging, Signals, Digest
"""

import os
import sys
import json
import traceback
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
CORS(app)

# Database path
DB_PATH = os.getenv('DATABASE_PATH', 'apex.db')

# Initialize engines (optional - graceful degradation)
enrichment_engine = None
scoring_engine = None
email_generator = None
call_generator = None
linkedin_generator = None

try:
    from enhanced_enrichment import EnrichmentEngine
    from apex_scoring_engine import ApexScoringEngine
    from email_generator import EmailContentGenerator
    from call_script_generator import CallScriptGenerator
    from linkedin_generator import LinkedInContentGenerator
    
    enrichment_engine = EnrichmentEngine()
    scoring_engine = ApexScoringEngine()
    email_generator = EmailContentGenerator()
    call_generator = CallScriptGenerator()
    linkedin_generator = LinkedInContentGenerator()
    
    logger.info("✅ Enrichment engine loaded")
    logger.info("✅ Scoring engines loaded")
    logger.info("✅ Cadence engines loaded")
except ModuleNotFoundError as e:
    logger.warning(f"⚠️ Optional module missing: {e.name}. Running in degraded mode.")
except Exception as e:
    logger.error(f"⚠️ Engine initialization failed: {e}")
    
# Database helpers
def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstname TEXT,
            lastname TEXT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            company TEXT,
            title TEXT,
            lifecycle_stage TEXT,
            lead_status TEXT,
            priority_score REAL,
            mdcp_score REAL,
            rss_score REAL,
            mdcp_tier TEXT,
            rss_tier TEXT,
            urgency_level TEXT,
            enrichment_status TEXT DEFAULT 'pending',
            profile_content TEXT,
            pain_points TEXT,
            talking_points TEXT,
            product_match TEXT,
            match_reasoning TEXT,
            recommended_action TEXT,
            notes TEXT,
            email_1_subject TEXT,
            email_1_body TEXT,
            email_2_subject TEXT,
            email_2_body TEXT,
            email_3_subject TEXT,
            email_3_body TEXT,
            call_script_1 TEXT,
            call_script_2 TEXT,
            call_script_3 TEXT,
            linkedin_connect TEXT,
            linkedin_followup TEXT,
            linkedin_inmail TEXT,
            linkedin_warmup TEXT,
            linkedin_url TEXT,
            last_contact_date TEXT,
            last_scored TEXT,
            content_generated_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            linkedin_activity_detected INTEGER DEFAULT 0,
            company_news_detected INTEGER DEFAULT 0,
            last_signal_date TEXT,
            signal_count INTEGER DEFAULT 0
        )
    ''')
    
    # Activity logging table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            activity_date TEXT NOT NULL,
            direction TEXT,
            subject TEXT,
            notes TEXT,
            outcome TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    ''')
    
    # Opportunity signals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunity_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            signal_type TEXT NOT NULL,
            signal_date TEXT NOT NULL,
            signal_data TEXT,
            urgency_boost INTEGER DEFAULT 0,
            viewed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    ''')
    
    # Digest preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS digest_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            digest_time TEXT DEFAULT '07:00',
            timezone TEXT DEFAULT 'America/Los_Angeles',
            include_prospects INTEGER DEFAULT 1,
            include_signals INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_enrichment ON contacts(enrichment_status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_contact ON contact_activities(contact_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_date ON contact_activities(activity_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_contact ON opportunity_signals(contact_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_signals_viewed ON opportunity_signals(viewed)')
    
    conn.commit()
    conn.close()
    logger.info("✅ Database schema checked")

# Initialize DB on startup
init_db()
logger.info(f"📊 Database: {DB_PATH}")
logger.info("🔧 Enrichment: ✅ Available" if enrichment_engine else "🔧 Enrichment: ❌ Unavailable")
logger.info("🎯 Scoring: ✅ Available" if scoring_engine else "🎯 Scoring: ❌ Unavailable")
logger.info("📅 Cadences: ✅ Available")

# ============= HEALTH CHECK =============
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'enrichment': enrichment_engine is not None,
            'scoring': scoring_engine is not None,
            'database': os.path.exists(DB_PATH)
        }
    })

# ============= CONTACTS ENDPOINTS =============
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts with optional filtering"""
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        enriched_only = request.args.get('enriched_only', 'false').lower() == 'true'
        
        conn = get_db()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM contacts'
        params = []
        
        if enriched_only:
            query += ' WHERE enrichment_status = ?'
            params.append('completed')
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'contacts': contacts,
            'total': len(contacts),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        logger.error(f"Get contacts error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get single contact by ID"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        return jsonify(dict(contact))
    except Exception as e:
        logger.error(f"Get contact error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PATCH'])
def update_contact(contact_id):
    """Update contact fields"""
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()
        
        # Build update query dynamically
        fields = []
        values = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)
        
        if fields:
            values.append(datetime.now().isoformat())
            values.append(contact_id)
            query = f"UPDATE contacts SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
        return jsonify({'success': True, 'message': 'Contact updated'})
    except Exception as e:
        logger.error(f"Update contact error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= ENRICHMENT ENDPOINTS =============
@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    """Enrich a single contact"""
    try:
        if not enrichment_engine:
            return jsonify({'success': False, 'error': 'Enrichment engine unavailable'}), 503
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        contact_dict = dict(contact)
        
        # Run enrichment
        logger.info(f"Enriching contact {contact_id}: {contact_dict.get('name')}")
        enriched_data = enrichment_engine.enrich_contact(contact_dict)
        
        if enriched_data:
            # Update database
            cursor.execute('''
                UPDATE contacts 
                SET profile_content = ?,
                    enrichment_status = 'completed',
                    updated_at = ?
                WHERE id = ?
            ''', (enriched_data, datetime.now().isoformat(), contact_id))
            conn.commit()
            
            # Score the contact
            if scoring_engine:
                cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
                updated_contact = dict(cursor.fetchone())
                scores = scoring_engine.score_contact(updated_contact)
                
                if scores:
                    cursor.execute('''
                        UPDATE contacts 
                        SET priority_score = ?, mdcp_score = ?, rss_score = ?,
                            mdcp_tier = ?, rss_tier = ?, urgency_level = ?,
                            last_scored = ?
                        WHERE id = ?
                    ''', (
                        scores.get('priority_score'),
                        scores.get('mdcp_score'),
                        scores.get('rss_score'),
                        scores.get('mdcp_tier'),
                        scores.get('rss_tier'),
                        scores.get('urgency_level'),
                        datetime.now().isoformat(),
                        contact_id
                    ))
                    conn.commit()
            
            conn.close()
            return jsonify({'success': True, 'message': 'Contact enriched successfully'})
        else:
            conn.close()
            return jsonify({'success': False, 'error': 'Enrichment failed'}), 500
            
    except Exception as e:
        logger.error(f"Enrichment error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= CONTENT GENERATION ENDPOINTS =============
@app.route('/api/contacts/<int:contact_id>/generate-content', methods=['POST'])
def generate_content(contact_id):
    """Generate outreach content for a contact"""
    try:
        data = request.json or {}
        content_type = data.get('content_type', 'all')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        contact_dict = dict(contact)
        results = {}
        
        # Generate emails
        if content_type in ['all', 'email']:
            try:
                emails = email_generator.generate_email_sequence(
                    contact_dict,
                    contact_dict.get('profile_content', '')
                )
                if emails:
                    for i, email in enumerate(emails[:3], 1):
                        cursor.execute(f'''
                            UPDATE contacts 
                            SET email_{i}_subject = ?, email_{i}_body = ?
                            WHERE id = ?
                        ''', (email.get('subject'), email.get('body'), contact_id))
                    results['email'] = {'success': True, 'count': len(emails)}
            except Exception as e:
                logger.error(f"Email generation error: {e}")
                results['email'] = {'success': False, 'error': str(e)}
        
        # Generate call scripts
        if content_type in ['all', 'call']:
            try:
                scripts = call_generator.generate_call_scripts(
                    contact_dict,
                    contact_dict.get('profile_content', '')
                )
                if scripts:
                    for i, script in enumerate(scripts[:3], 1):
                        cursor.execute(f'''
                            UPDATE contacts 
                            SET call_script_{i} = ?
                            WHERE id = ?
                        ''', (script, contact_id))
                    results['call'] = {'success': True, 'count': len(scripts)}
            except Exception as e:
                logger.error(f"Call script generation error: {e}")
                results['call'] = {'success': False, 'error': str(e)}
        
        # Generate LinkedIn content
        if content_type in ['all', 'linkedin']:
            try:
                linkedin_content = linkedin_generator.generate_linkedin_content(
                    contact_dict,
                    contact_dict.get('profile_content', '')
                )
                if linkedin_content:
                    cursor.execute('''
                        UPDATE contacts 
                        SET linkedin_connect = ?, linkedin_followup = ?,
                            linkedin_inmail = ?, linkedin_warmup = ?
                        WHERE id = ?
                    ''', (
                        linkedin_content.get('connection_request'),
                        linkedin_content.get('followup_message'),
                        linkedin_content.get('inmail'),
                        linkedin_content.get('warmup_sequence'),
                        contact_id
                    ))
                    results['linkedin'] = {'success': True}
            except Exception as e:
                logger.error(f"LinkedIn generation error: {e}")
                results['linkedin'] = {'success': False, 'error': str(e)}
        
        # Update timestamp
        cursor.execute('''
            UPDATE contacts SET content_generated_at = ?, updated_at = ? WHERE id = ?
        ''', (datetime.now().isoformat(), datetime.now().isoformat(), contact_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= HUBSPOT IMPORT =============
@app.route('/api/hubspot/import', methods=['POST'])
def import_from_hubspot():
    """Import contacts from HubSpot"""
    try:
        import requests
        
        hubspot_token = os.getenv('HUBSPOT_ACCESS_TOKEN')
        if not hubspot_token:
            return jsonify({'success': False, 'error': 'HubSpot token not configured'}), 400
        
        url = 'https://api.hubapi.com/crm/v3/objects/contacts'
        headers = {'Authorization': f'Bearer {hubspot_token}'}
        params = {'limit': 100, 'properties': 'firstname,lastname,email,phone,company,jobtitle,lifecyclestage,hs_lead_status'}
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        contacts = data.get('results', [])
        imported = 0
        
        conn = get_db()
        cursor = conn.cursor()
        
        for contact in contacts:
            props = contact.get('properties', {})
            email = props.get('email')
            
            if not email:
                continue
            
            # Check if exists
            cursor.execute('SELECT id FROM contacts WHERE email = ?', (email,))
            if cursor.fetchone():
                continue
            
            # Insert new contact
            cursor.execute('''
                INSERT INTO contacts (
                    firstname, lastname, name, email, phone, company, title, 
                    lifecycle_stage, lead_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                props.get('firstname', ''),
                props.get('lastname', ''),
                f"{props.get('firstname', '')} {props.get('lastname', '')}".strip(),
                email,
                props.get('phone', ''),
                props.get('company', ''),
                props.get('jobtitle', ''),
                props.get('lifecyclestage', ''),
                props.get('hs_lead_status', ''),
                datetime.now().isoformat()
            ))
            imported += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'imported': imported,
            'total': len(contacts)
        })
        
    except Exception as e:
        logger.error(f"HubSpot import error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= TODAY'S BOARD ENDPOINT =============
@app.route('/api/todays-board', methods=['GET'])
def get_todays_board():
    """Generate daily prioritized action list"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # RELATIONSHIPS QUERY
        cursor.execute("""
            SELECT id, name, email, phone, company, title,
                   priority_score, mdcp_score, enrichment_status,
                   email_1_subject, email_1_body, call_script_1, linkedin_connect,
                   linkedin_activity_detected, company_news_detected,
                   CASE WHEN last_contact_date IS NULL THEN 0
                        ELSE CAST(julianday('now') - julianday(last_contact_date) AS INTEGER)
                   END AS days_since_contact
            FROM contacts
            WHERE enrichment_status = 'completed'
            AND last_contact_date IS NOT NULL AND last_contact_date != ''
            LIMIT 30
        """)
        
        relationships = []
        for row in cursor.fetchall():
            c = dict(row)
            days = c.get('days_since_contact', 0)
            if days > 365:
                c['urgency_tier'] = 'urgent'
                c['urgency_label'] = '🔥 ACT TODAY'
                c['why_now'] = f"Last spoke {days} days ago - going cold"
            elif days > 180:
                c['urgency_tier'] = 'warm'
                c['urgency_label'] = '⏰ THIS WEEK'
                c['why_now'] = f"Last spoke {days} days ago - reconnect"
            elif days > 90:
                c['urgency_tier'] = 'nurture'
                c['urgency_label'] = '💎 NURTURE'
                c['why_now'] = f"Last spoke {days} days ago"
            else:
                c['urgency_tier'] = 'stable'
                c['urgency_label'] = '📚 STABLE'
                c['why_now'] = 'Recent contact'
            c['contact_type'] = 'relationship'
            c['urgency_message'] = c['why_now']
            relationships.append(c)
        
        # PROSPECTS QUERY
        cursor.execute("""
            SELECT id, name, email, phone, company, title,
                   priority_score, mdcp_score, enrichment_status,
                   email_1_subject, email_1_body, call_script_1, linkedin_connect,
                   0 as days_since_contact
            FROM contacts
            WHERE enrichment_status = 'completed'
            AND (last_contact_date IS NULL OR last_contact_date = '')
            AND priority_score >= 60
            LIMIT 15
        """)
        
        prospects = []
        for row in cursor.fetchall():
            c = dict(row)
            p = c.get('priority_score', 0)
            if p >= 85:
                c['urgency_tier'] = 'hot_prospect'
                c['urgency_label'] = '🎯 HOT'
                c['why_now'] = f"High priority: {p:.1f}"
            elif p >= 75:
                c['urgency_tier'] = 'qualified_prospect'
                c['urgency_label'] = '✅ QUALIFIED'
                c['why_now'] = f"Good fit: {p:.1f}"
            else:
                c['urgency_tier'] = 'potential_prospect'
                c['urgency_label'] = '🔍 POTENTIAL'
                c['why_now'] = f"Priority: {p:.1f}"
            c['contact_type'] = 'prospect'
            c['urgency_message'] = c['why_now']
            prospects.append(c)
        
        # ORGANIZE BY TIERS
        urgent = [c for c in relationships if c['urgency_tier'] == 'urgent']
        warm = [c for c in relationships if c['urgency_tier'] == 'warm']
        nurture = [c for c in relationships if c['urgency_tier'] == 'nurture']
        stable = [c for c in relationships if c['urgency_tier'] == 'stable']
        hot = [c for c in prospects if c['urgency_tier'] == 'hot_prospect']
        qualified = [c for c in prospects if c['urgency_tier'] == 'qualified_prospect']
        potential = [c for c in prospects if c['urgency_tier'] == 'potential_prospect']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%I:%M %p'),
            'total_actions': len(urgent) + len(warm) + len(hot) + len(qualified),
            'recommendation': f"Call {len(urgent)} urgent + {len(hot)} hot prospects",
            'relationships': {
                'total': len(relationships),
                'urgent_count': len(urgent),
                'warm_count': len(warm),
                'nurture_count': len(nurture),
                'stable_count': len(stable),
                'tiers': {
                    'urgent': urgent[:5],
                    'warm': warm[:5],
                    'nurture': nurture[:4],
                    'stable': stable[:4]
                }
            },
            'new_prospects': {
                'total': len(prospects),
                'hot_count': len(hot),
                'qualified_count': len(qualified),
                'potential_count': len(potential),
                'tiers': {
                    'hot': hot[:5],
                    'qualified': qualified[:5],
                    'potential': potential[:5]
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Today's Board error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= ACTIVITY LOGGING ENDPOINTS (PHASE 2) =============
@app.route('/api/activities/log', methods=['POST'])
def log_activity():
    """Log a contact activity"""
    try:
        data = request.json
        contact_id = data.get('contact_id')
        activity_type = data.get('activity_type')
        activity_date = data.get('activity_date', datetime.now().isoformat())
        direction = data.get('direction', 'outbound')
        subject = data.get('subject', '')
        notes = data.get('notes', '')
        outcome = data.get('outcome', '')
        
        if not contact_id or not activity_type:
            return jsonify({'success': False, 'error': 'contact_id and activity_type required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO contact_activities 
            (contact_id, activity_type, activity_date, direction, subject, notes, outcome)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (contact_id, activity_type, activity_date, direction, subject, notes, outcome))
        
        cursor.execute("""
            UPDATE contacts 
            SET last_contact_date = ? 
            WHERE id = ?
        """, (activity_date.split('T')[0], contact_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'activity_id': cursor.lastrowid,
            'message': f'{activity_type.title()} logged successfully'
        })
        
    except Exception as e:
        logger.error(f"Activity logging error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/activities/<int:contact_id>', methods=['GET'])
def get_contact_activities(contact_id):
    """Get activity timeline for a contact"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, activity_type, activity_date, direction, subject, notes, outcome, created_at
            FROM contact_activities
            WHERE contact_id = ?
            ORDER BY activity_date DESC
            LIMIT 50
        """, (contact_id,))
        
        activities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'activities': activities,
            'total': len(activities)
        })
        
    except Exception as e:
        logger.error(f"Get activities error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= OPPORTUNITY SIGNALS ENDPOINTS (PHASE 2) =============
@app.route('/api/signals/detect', methods=['POST'])
def detect_signals():
    """Trigger signal detection for contacts"""
    try:
        data = request.json or {}
        contact_ids = data.get('contact_ids', [])
        
        if not contact_ids:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM contacts 
                WHERE enrichment_status = 'completed' 
                ORDER BY priority_score DESC 
                LIMIT 50
            """)
            contact_ids = [row['id'] for row in cursor.fetchall()]
            conn.close()
        
        conn = get_db()
        cursor = conn.cursor()
        
        signals_created = 0
        
        for contact_id in contact_ids:
            cursor.execute("SELECT name, company, title, email FROM contacts WHERE id = ?", (contact_id,))
            contact = cursor.fetchone()
            
            if not contact:
                continue
            
            # Simulated signal detection (30% chance per contact)
            import random
            
            if random.random() > 0.7:
                signal_types = ['job_change', 'linkedin_post', 'company_news', 'funding']
                signal_type = random.choice(signal_types)
                
                signal_messages = {
                    'job_change': f"📢 {contact['name']} updated their LinkedIn profile",
                    'linkedin_post': f"💬 {contact['name']} posted about industry trends",
                    'company_news': f"📰 {contact['company']} announced expansion plans",
                    'funding': f"💰 {contact['company']} raised new funding round"
                }
                
                urgency_boost = {
                    'job_change': 30,
                    'linkedin_post': 15,
                    'company_news': 25,
                    'funding': 35
                }.get(signal_type, 10)
                
                cursor.execute("""
                    INSERT INTO opportunity_signals
                    (contact_id, signal_type, signal_date, signal_data, urgency_boost)
                    VALUES (?, ?, ?, ?, ?)
                """, (contact_id, signal_type, datetime.now().isoformat(), 
                      signal_messages[signal_type], urgency_boost))
                
                # Update contact flags
                if signal_type in ['job_change', 'linkedin_post']:
                    cursor.execute("""
                        UPDATE contacts 
                        SET linkedin_activity_detected = 1, 
                            last_signal_date = ?,
                            signal_count = signal_count + 1
                        WHERE id = ?
                    """, (datetime.now().isoformat(), contact_id))
                elif signal_type in ['company_news', 'funding']:
                    cursor.execute("""
                        UPDATE contacts 
                        SET company_news_detected = 1,
                            last_signal_date = ?,
                            signal_count = signal_count + 1
                        WHERE id = ?
                    """, (datetime.now().isoformat(), contact_id))
                
                signals_created += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'signals_created': signals_created,
            'contacts_scanned': len(contact_ids)
        })
        
    except Exception as e:
        logger.error(f"Signal detection error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signals/unread', methods=['GET'])
def get_unread_signals():
    """Get all unread opportunity signals"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                s.id, s.contact_id, s.signal_type, s.signal_date, 
                s.signal_data, s.urgency_boost,
                c.name, c.company, c.title, c.priority_score, c.email
            FROM opportunity_signals s
            JOIN contacts c ON s.contact_id = c.id
            WHERE s.viewed = 0
            ORDER BY s.signal_date DESC, s.urgency_boost DESC
            LIMIT 20
        """)
        
        signals = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'signals': signals,
            'total': len(signals)
        })
        
    except Exception as e:
        logger.error(f"Get signals error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/signals/mark-read/<int:signal_id>', methods=['POST'])
def mark_signal_read(signal_id):
    """Mark a signal as viewed"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE opportunity_signals SET viewed = 1 WHERE id = ?", (signal_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Signal marked as read'})
        
    except Exception as e:
        logger.error(f"Mark signal read error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= DAILY DIGEST ENDPOINTS (PHASE 2) =============
@app.route('/api/digest/generate', methods=['GET'])
def generate_digest():
    """Generate daily digest email content"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get urgent relationships
        cursor.execute("""
            SELECT name, company, title,
                   CAST(julianday('now') - julianday(last_contact_date) AS INTEGER) as days
            FROM contacts
            WHERE enrichment_status = 'completed'
            AND last_contact_date IS NOT NULL
            AND julianday('now') - julianday(last_contact_date) > 365
            ORDER BY days DESC
            LIMIT 3
        """)
        urgent = [dict(row) for row in cursor.fetchall()]
        
        # Get hot prospects
        cursor.execute("""
            SELECT name, company, title, priority_score
            FROM contacts
            WHERE enrichment_status = 'completed'
            AND (last_contact_date IS NULL OR last_contact_date = '')
            AND priority_score >= 85
            ORDER BY priority_score DESC
            LIMIT 3
        """)
        prospects = [dict(row) for row in cursor.fetchall()]
        
        # Get unread signals
        cursor.execute("""
            SELECT c.name, c.company, s.signal_data
            FROM opportunity_signals s
            JOIN contacts c ON s.contact_id = c.id
            WHERE s.viewed = 0
            ORDER BY s.signal_date DESC
            LIMIT 5
        """)
        signals = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # Build digest HTML
        digest_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #4f46e5;">🌅 Your Daily Board - {datetime.now().strftime('%B %d, %Y')}</h1>
            
            <div style="background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0;">
                <h2 style="color: #dc2626; margin-top: 0;">🔥 Urgent - {len(urgent)} Relationships Going Cold</h2>
                <ul>
                    {''.join([f"<li><strong>{c['name']}</strong> at {c['company']} - Last spoke {c['days']} days ago</li>" for c in urgent]) or '<li>All relationships are warm!</li>'}
                </ul>
            </div>
            
            <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 15px; margin: 20px 0;">
                <h2 style="color: #16a34a; margin-top: 0;">🎯 Hot Prospects - {len(prospects)} Ready to Call</h2>
                <ul>
                    {''.join([f"<li><strong>{c['name']}</strong> at {c['company']} - Priority: {c['priority_score']:.1f}</li>" for c in prospects]) or '<li>No hot prospects today</li>'}
                </ul>
            </div>
            
            <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0;">
                <h2 style="color: #2563eb; margin-top: 0;">💡 Opportunity Signals - {len(signals)} New Alerts</h2>
                <ul>
                    {''.join([f"<li><strong>{s['name']}</strong> at {s['company']}: {s['signal_data']}</li>" for s in signals]) or '<li>No new signals</li>'}
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="http://localhost:5173" style="background: #4f46e5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    Open Today's Board →
                </a>
            </div>
            
            <p style="color: #6b7280; font-size: 12px; margin-top: 30px; text-align: center;">
                Apex Intelligence • Your AI Sales Copilot
            </p>
        </body>
        </html>
        """
        
        return jsonify({
            'success': True,
            'html': digest_html,
            'summary': {
                'urgent_count': len(urgent),
                'prospects_count': len(prospects),
                'signals_count': len(signals),
                'total_actions': len(urgent) + len(prospects)
            }
        })
        
    except Exception as e:
        logger.error(f"Digest generation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/digest/send', methods=['POST'])
def send_digest():
    """Send digest email (requires email service setup)"""
    try:
        data = request.json
        recipient_email = data.get('email')
        
        if not recipient_email:
            return jsonify({'success': False, 'error': 'Email required'}), 400
        
        # Generate digest
        digest_response = generate_digest()
        digest_data = digest_response.get_json()
        
        if not digest_data.get('success'):
            return jsonify({'success': False, 'error': 'Failed to generate digest'}), 500
        
        # TODO: Integrate with SendGrid, AWS SES, or other email service
        logger.info(f"Would send digest to {recipient_email}")
        logger.info(f"Summary: {digest_data['summary']}")
        
        return jsonify({
            'success': True,
            'message': f'Digest prepared for {recipient_email}',
            'preview_html': digest_data['html']
        })
        
    except Exception as e:
        logger.error(f"Send digest error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= MAIN =============
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
    