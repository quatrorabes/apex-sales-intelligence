#!/usr/bin/env python3
"""
Apex API Server - WITH STRUCTURED INTELLIGENCE PARSING
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Keys
HUBSPOT_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN') or os.getenv('HUBSPOT_API_KEY')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logger.info(f"HubSpot Token: {HUBSPOT_TOKEN[:20] if HUBSPOT_TOKEN else 'NONE'}...")
logger.info(f"Perplexity Key: {'✅ Found' if PERPLEXITY_API_KEY else '❌ Missing'}")
logger.info(f"OpenAI Key: {'✅ Found' if OPENAI_API_KEY else '❌ Missing'}")

# ============= IMPORT ENRICHMENT =============
ENRICHMENT_AVAILABLE = False
try:
    from intelligence.engines.enrichment.enhanced_enrichment import EnhancedEnrichment
    ENRICHMENT_AVAILABLE = True
    logger.info("✅ Enrichment engine loaded")
except ImportError as e:
    logger.warning(f"⚠️ Could not load enrichment engine: {e}")

# ============= IMPORT SCORING =============
SCORING_AVAILABLE = False
try:
    from intelligence.engines.scoring.apex_intelligence_engine import ApexScoringEngine
    from intelligence.engines.scoring.scoring_wrapper import (
        score_contact_from_db,
        bulk_score_contacts,
        get_apex_scores
    )
    SCORING_AVAILABLE = True
    logger.info("✅ Scoring engines loaded")
except ImportError as e:
    logger.error(f"❌ Scoring engines not available: {e}")
    logger.warning("⚠️ Using fallback scoring")

    # Fallback scoring functions [unchanged from before]
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
        urgency = 'IMMEDIATE' if score >= 80 else 'HIGH' if score >= 70 else 'MEDIUM'

        cursor.execute('''
            UPDATE contacts 
            SET mdcp_score = ?, mdcp_tier = ?,
                rss_score = ?, rss_tier = ?,
                priority_score = ?, urgency_level = ?,
                recommended_action = ?,
                calculation_version = 'fallback_v1',
                last_scored = ?
            WHERE id = ?
        ''', (score, tier, score, tier, score, urgency,
              f'{urgency} priority contact',
              datetime.now().isoformat(), contact_id))
        conn.commit()

        return {
            'success': True,
            'contact_id': contact_id,
            'scores': {
                'mdcp_score': score,
                'mdcp_tier': tier,
                'rss_score': score,
                'rss_tier': tier,
                'priority_score': score,
                'urgency_level': urgency
            }
        }

    def bulk_score_contacts(conn, contact_ids, trigger='batch'):
        results = []
        for cid in contact_ids:
            try:
                result = score_contact_from_db(conn, cid, trigger)
                results.append(result)
            except Exception as e:
                results.append({'contact_id': cid, 'error': str(e)})
        return results

    def get_apex_scores(conn):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, company, email, lead_type, lifecycle_stage,
                   mdcp_score as mdcp_total, mdcp_tier,
                   rss_score as rss_total, rss_tier,
                   priority_score, urgency_level,
                   recommended_action, last_scored
            FROM contacts
            WHERE mdcp_score IS NOT NULL
            ORDER BY priority_score DESC
        ''')
        columns = [desc[0] for desc in cursor.description]
        contacts = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return {
            'status': 'success',
            'count': len(contacts),
            'contacts': contacts
        }

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configuration
DATABASE = '/Users/chrisrabenold/projects/apex/apex.db'
PORT = 8000

# ============= DATABASE HELPERS =============
def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_intelligence_columns():
    """Add structured intelligence columns"""
    conn = get_db()
    cursor = conn.cursor()

    # Original columns
    original_columns = [
        ('mdcp_score', 'REAL'),
        ('mdcp_tier', 'TEXT'),
        ('rss_score', 'REAL'),
        ('rss_tier', 'TEXT'),
        ('priority_score', 'REAL'),
        ('urgency_level', 'TEXT'),
        ('recommended_action', 'TEXT'),
        ('calculation_version', 'TEXT'),
        ('last_scored', 'TEXT'),
        ('lead_type', 'TEXT')
    ]
    
    # NEW: Structured intelligence fields
    intelligence_columns = [
        ('executive_summary', 'TEXT'),
        ('professional_overview', 'TEXT'),
        ('background_experience', 'TEXT'),
        ('education', 'TEXT'),
        ('personality_style', 'TEXT'),
        ('social_presence', 'TEXT'),
        ('company_overview', 'TEXT'),
        ('products_services', 'TEXT'),
        ('market_position', 'TEXT'),
        ('leadership', 'TEXT'),
        ('recent_activity', 'TEXT'),
        ('trigger_events', 'TEXT'),
        ('pain_points', 'TEXT'),
        ('engagement_strategy', 'TEXT'),
        ('recommended_opening', 'TEXT'),
        ('opportunity_level', 'TEXT'),
        ('top_reasons', 'TEXT'),
        ('strategic_summary', 'TEXT'),
        ('competitive_intelligence', 'TEXT'),
    ]

    all_columns = original_columns + intelligence_columns

    for col_name, col_type in all_columns:
        try:
            cursor.execute(f'ALTER TABLE contacts ADD COLUMN {col_name} {col_type}')
            logger.info(f"✅ Added column: {col_name}")
        except sqlite3.OperationalError:
            pass  # Column already exists

    conn.commit()
    conn.close()
    logger.info("✅ Database schema updated with intelligence fields")

def ensure_user_preferences_table():
    """Ensure user_preferences table exists"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL DEFAULT 'default_user',
            products TEXT DEFAULT '[]',
            services TEXT DEFAULT '[]',
            value_propositions TEXT DEFAULT '[]',
            target_customers TEXT DEFAULT '[]',
            personal_differentiators TEXT DEFAULT '[]',
            company_differentiators TEXT DEFAULT '[]',
            scoring_profile TEXT DEFAULT 'DEFAULT',
            custom_ideal_titles TEXT DEFAULT '[]',
            custom_avoid_titles TEXT DEFAULT '[]',
            ideal_company_size_min INTEGER,
            ideal_company_size_max INTEGER,
            ideal_industries TEXT DEFAULT '[]',
            target_seniority_levels TEXT DEFAULT '[]',
            exclude_c_suite BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        INSERT OR IGNORE INTO user_preferences (user_id) 
        VALUES ('default_user')
    ''')

    conn.commit()
    conn.close()
    logger.info("✅ User preferences table checked")

# Run DB setup
ensure_intelligence_columns()
ensure_user_preferences_table()

# ============= API ROUTES =============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'enrichment_available': ENRICHMENT_AVAILABLE,
        'scoring_available': SCORING_AVAILABLE
    })

# ============= CONTACTS ENDPOINTS =============

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts with optional filtering"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        query = 'SELECT * FROM contacts'
        count_query = 'SELECT COUNT(*) FROM contacts'
        params = []
        count_params = []
        
        if status:
            query += ' WHERE enrichment_status = ?'
            count_query += ' WHERE enrichment_status = ?'
            params.append(status)
            count_params.append(status)
            
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        contacts = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'contacts': contacts,
            'total': total,
            'page': (offset // limit) + 1,
            'hasMore': offset + limit < total
        })
    
    except Exception as e:
        logger.error(f"❌ Error fetching contacts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a single contact with ALL intelligence fields"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = cursor.fetchone()
        conn.close()

        if contact:
            return jsonify(dict(contact))
        else:
            return jsonify({'error': 'Contact not found'}), 404

    except Exception as e:
        logger.error(f"❌ Error fetching contact: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PATCH'])
def update_contact(contact_id):
    """Update contact fields"""
    try:
        data = request.get_json()
        conn = get_db()
        cursor = conn.cursor()

        fields = []
        values = []
        for key, value in data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return jsonify({'error': 'No fields to update'}), 400

        values.append(contact_id)
        query = f"UPDATE contacts SET {', '.join(fields)} WHERE id = ?"

        cursor.execute(query, values)
        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        logger.error(f"❌ Error updating contact: {e}")
        return jsonify({'error': str(e)}), 500

# ============= ENRICHMENT ENDPOINTS =============

@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    """Enrich contact WITH PARSING into structured fields"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return jsonify({"success": False, "error": "Contact not found"}), 404

        contact = dict(row)
        
        # Set to processing
        cursor.execute("""
            UPDATE contacts 
            SET enrichment_status = 'processing'
            WHERE id = ?
        """, (contact_id,))
        conn.commit()
        conn.close()

        if not ENRICHMENT_AVAILABLE:
            return jsonify({
                "success": False,
                "error": "Enrichment engine not available"
            }), 500

        logger.info(f"🔍 Starting enrichment for {contact['firstname']} {contact['lastname']}")

        enricher = EnhancedEnrichment()
        result = enricher.enrich_contact(contact)

        if result and result.get('success'):
            parsed_data = result.get('parsed_data', {})
            
            # Build update query with ALL parsed fields
            update_fields = [
                'profile_content = ?',
                'enriched = 1',
                'enriched_at = ?',
                'enrichment_status = ?'
            ]
            update_values = [
                result['profile_text'],
                datetime.now().isoformat(),
                'completed'
            ]
            
            # Add all parsed fields
            for field_name, field_value in parsed_data.items():
                update_fields.append(f"{field_name} = ?")
                update_values.append(field_value)
            
            update_values.append(contact_id)
            
            conn = get_db()
            conn.execute(f"""
                UPDATE contacts SET
                {', '.join(update_fields)}
                WHERE id = ?
            """, update_values)
            conn.commit()
            conn.close()

            logger.info(f"✅ Enrichment complete with {len(parsed_data)} parsed sections")
            return jsonify({
                'success': True,
                'contact_id': contact_id,
                'status': 'completed',
                'profile_length': result['character_count'],
                'parsed_sections': len(parsed_data)
            }), 200
        else:
            # Mark as failed
            conn = get_db()
            conn.execute("""
                UPDATE contacts 
                SET enrichment_status = 'failed'
                WHERE id = ?
            """, (contact_id,))
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': False,
                'status': 'failed',
                'error': 'Enrichment failed'
            }), 500

    except Exception as e:
        logger.error(f"❌ Enrichment error: {e}")
        traceback.print_exc()
        
        try:
            conn = get_db()
            conn.execute("""
                UPDATE contacts 
                SET enrichment_status = 'failed'
                WHERE id = ?
            """, (contact_id,))
            conn.commit()
            conn.close()
        except:
            pass
            
        return jsonify({
            'success': False,
            'status': 'failed',
            'error': str(e)
        }), 500

@app.route('/api/contacts/<int:contact_id>/enrichment-status', methods=['GET'])
def get_enrichment_status(contact_id):
    """Get enrichment status"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, enrichment_status, enriched_at, 
                   mdcp_score, priority_score, profile_content
            FROM contacts 
            WHERE id = ?
        """, (contact_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({
                'success': False,
                'error': 'Contact not found'
            }), 404

        contact = dict(row)
        status = contact.get('enrichment_status', 'none')
        
        # Extract why_now
        why_now = None
        profile = contact.get('profile_content')
        if profile and '## Sales Opportunities' in profile:
            try:
                why_section = profile.split('## Sales Opportunities')[1].split('##')[0]
                why_now = why_section.strip()[:200] + '...'
            except:
                pass

        return jsonify({
            'contact_id': contact_id,
            'status': status,
            'last_enriched': contact.get('enriched_at'),
            'mdcp_score': contact.get('mdcp_score'),
            'priority_score': contact.get('priority_score'),
            'why_now': why_now
        }), 200

    except Exception as e:
        logger.error(f"❌ Error getting enrichment status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/contacts/<int:contact_id>/reset-enrichment', methods=['POST'])
def reset_enrichment(contact_id):
    """Reset enrichment status for re-enrichment"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts 
            SET enrichment_status = 'pending'
            WHERE id = ?
        """, (contact_id,))
        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============= TODAY'S BOARD ENDPOINT =============

@app.route('/api/todays-board', methods=['GET'])
def get_todays_board():
    """Daily prioritized action list"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        now = datetime.now()
        date_str = now.strftime('%B %d, %Y')
        time_str = now.strftime('%I:%M %p')
        
        cursor.execute("""
            SELECT id, name, email, phone, company, title,
                   mdcp_score, priority_score, enrichment_status,
                   enriched_at as last_enriched
            FROM contacts
            ORDER BY id DESC
            LIMIT 100
        """)
        
        all_contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"📊 Found {len(all_contacts)} contacts for Today's Board")
        
        urgent = []
        warm = []
        hot = []
        qualified = []
        potential = []
        
        for c in all_contacts:
            score = 50
            if c.get('email'): score += 10
            if c.get('phone'): score += 10
            if c.get('company'): score += 10
            if c.get('title'): score += 10
            
            c['mdcp_score'] = float(score)
            c['priority_score'] = float(score)
            c['enrichment_status'] = c.get('enrichment_status') or 'pending'
            c['why_now'] = f"⚡ Ready to enrich - Data score: {score}"
            
            if score >= 90:
                c['urgency_tier'] = 'urgent'
                c['urgency_label'] = '🔥 URGENT'
                c['contact_type'] = 'relationship'
                if len(urgent) < 10:
                    urgent.append(c)
            elif score >= 80:
                c['urgency_tier'] = 'hot_prospect'
                c['urgency_label'] = '🎯 HOT'
                c['contact_type'] = 'prospect'
                if len(hot) < 10:
                    hot.append(c)
            elif score >= 70:
                c['urgency_tier'] = 'warm'
                c['urgency_label'] = '⏰ WARM'
                c['contact_type'] = 'relationship'
                if len(warm) < 10:
                    warm.append(c)
            elif score >= 60:
                c['urgency_tier'] = 'qualified_prospect'
                c['urgency_label'] = '✅ QUALIFIED'
                c['contact_type'] = 'prospect'
                if len(qualified) < 10:
                    qualified.append(c)
            else:
                c['urgency_tier'] = 'potential_prospect'
                c['urgency_label'] = '🔍 POTENTIAL'
                c['contact_type'] = 'prospect'
                if len(potential) < 10:
                    potential.append(c)
        
        return jsonify({
            'success': True,
            'date': date_str,
            'time': time_str,
            'total_actions': len(urgent) + len(hot) + len(warm) + len(qualified),
            'recommendation': f"Start enriching {len(urgent)} urgent and {len(hot)} hot contacts",
            'relationships': {
                'total': len(urgent) + len(warm),
                'urgent_count': len(urgent),
                'warm_count': len(warm),
                'nurture_count': 0,
                'stable_count': 0,
                'tiers': {
                    'urgent': urgent,
                    'warm': warm,
                    'nurture': [],
                    'stable': []
                }
            },
            'new_prospects': {
                'total': len(hot) + len(qualified) + len(potential),
                'hot_count': len(hot),
                'qualified_count': len(qualified),
                'potential_count': len(potential),
                'tiers': {
                    'hot': hot,
                    'qualified': qualified,
                    'potential': potential
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Today's Board error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
