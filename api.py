#!/usr/bin/env python3
"""
Apex API Server - Flask Version with REAL AI Enrichment + Scoring
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

# ============= LOAD ENV ONCE =============
load_dotenv('/Users/chrisrabenold/projects/apex/.env')

# ============= FIX PYTHON PATH =============
BACKEND_PATH = '/Users/chrisrabenold/projects/apex/apps/backend'
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)
    
# Configure logging ONCE
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys
HUBSPOT_TOKEN = (
    os.getenv('HUBSPOT_ACCESS_TOKEN') or 
    os.getenv('HUBSPOT_API_KEY') or 
    os.getenv('HUBSPOT_ACCESS_KEY')
)
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

logger.info(f"Loaded HubSpot Token: {HUBSPOT_TOKEN[:20] if HUBSPOT_TOKEN else 'NONE'}...")
logger.info(f"Perplexity Key: {'✅ Found' if PERPLEXITY_API_KEY else '❌ Missing'}")
logger.info(f"OpenAI Key: {'✅ Found' if OPENAI_API_KEY else '❌ Missing'}")

# ============= TRY TO IMPORT ENRICHMENT =============
ENRICHMENT_AVAILABLE = False
PerplexityEnrichment = None

try:
    from intelligence.engines.enrichment.perplexity_enrichment import PerplexityEnrichment
    ENRICHMENT_AVAILABLE = True
    logger.info("✅ Enrichment engine loaded")
except ImportError as e:
    logger.warning(f"⚠️ Could not load enrichment engine: {e}")
    
# ============= TRY TO IMPORT SCORING =============
SCORING_AVAILABLE = False
score_contact_from_db = None
bulk_score_contacts = None
get_apex_scores = None

try:
    scoring_path = os.path.join(BACKEND_PATH, 'intelligence', 'engines', 'scoring')
    logger.info(f"Looking for scoring modules in: {scoring_path}")
    logger.info(f"Path exists: {os.path.exists(scoring_path)}")
    
    if os.path.exists(scoring_path):
        contents = os.listdir(scoring_path)
        logger.info(f"Scoring directory contents: {contents}")
        
    from intelligence.engines.scoring.scoring_wrapper import (
        score_contact_from_db,
        bulk_score_contacts,
        get_apex_scores
    )
    from intelligence.engines.scoring import ApexScoringEngine, ScoringOrchestrator
    
    SCORING_AVAILABLE = True
    logger.info("✅ Scoring engines loaded successfully")
    
except ImportError as e:
    logger.error(f"❌ Scoring engines not available: {e}")
    logger.error(traceback.format_exc())
    logger.warning("⚠️ Using fallback scoring functions")
    
    def score_contact_from_db(conn, contact_id, trigger='manual'):
        """Simple fallback scoring"""
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
            },
            'recommended_action': f'{urgency} priority contact',
            'timestamp': datetime.now().isoformat()
        }
    
    def bulk_score_contacts(conn, contact_ids, trigger='batch'):
        """Bulk scoring fallback"""
        results = []
        for cid in contact_ids:
            try:
                result = score_contact_from_db(conn, cid, trigger)
                results.append(result)
            except Exception as e:
                results.append({'contact_id': cid, 'error': str(e)})
        return results
    
    def get_apex_scores(conn):
        """Get scored contacts"""
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


def ensure_scoring_columns():
    """Ensure all scoring columns exist in contacts table"""
    conn = get_db()
    cursor = conn.cursor()
    
    columns_to_add = [
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
    
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f'ALTER TABLE contacts ADD COLUMN {col_name} {col_type}')
            logger.info(f"✅ Added column: {col_name}")
        except sqlite3.OperationalError:
            pass
            
    conn.commit()
    conn.close()
    logger.info("✅ Database schema checked for scoring")
    

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


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts with optional filtering"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)
        
        query = 'SELECT * FROM contacts'
        params = []
        
        if status:
            query += ' WHERE enrichment_status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(contacts)
        
    except Exception as e:
        logger.error(f"❌ Error fetching contacts: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a single contact by ID"""
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


@app.route('/api/hubspot/import', methods=['POST'])
def hubspot_import():
    """Import contacts from HubSpot with filtering and pagination"""
    
    if not HUBSPOT_TOKEN:
        logger.error("❌ HubSpot token not found in environment")
        return jsonify({
            'error': 'HubSpot API key not configured',
            'message': 'Please add HUBSPOT_ACCESS_TOKEN to your .env file',
            'imported': 0,
            'existing': 0,
            'filtered': 0,
            'total_in_hubspot': 0
        }), 400
    
    url = 'https://api.hubapi.com/crm/v3/objects/contacts'
    
    headers = {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }
    
    logger.info(f"Request URL: {url}")
    logger.info(f"Auth header: Bearer {HUBSPOT_TOKEN[:20]}...{HUBSPOT_TOKEN[-4:]}")
    
    base_params = {
        'limit': 100,
        'properties': [
            'firstname', 'lastname', 'email', 'phone', 'company',
            'jobtitle', 'industry', 'linkedin_url', 'hs_object_id',
            'hs_lead_status', 'lifecyclestage', 'numemployees',
            'annualrevenue', 'city', 'state', 'website', 'personal_contact'
        ]
    }
    
    EXCLUDED_LEAD_STATUSES = ['unqualified', 'do not contact', 'unsubscribe']
    EXCLUDED_LIFECYCLE_STAGES = ['unqualified']
    MAX_IMPORTS_PER_RUN = 100
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        imported = 0
        skipped = 0
        filtered = 0
        total_processed = 0
        
        after = None
        has_more = True
        page = 1
        limit_reached = False
        
        while has_more and not limit_reached:
            params = base_params.copy()
            if after:
                params['after'] = after
            
            logger.info(f"📡 Requesting page {page} from HubSpot (imported so far: {imported}/{MAX_IMPORTS_PER_RUN})...")
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 401:
                logger.error("❌ HubSpot authentication failed - 401 Unauthorized")
                conn.close()
                return jsonify({
                    'error': 'HubSpot authentication failed',
                    'message': 'Your HubSpot token is invalid or expired',
                    'imported': imported,
                    'existing': skipped,
                    'filtered': filtered,
                    'total_in_hubspot': total_processed
                }), 401
            
            if response.status_code != 200:
                logger.error(f"❌ HubSpot API error: {response.status_code}")
                conn.close()
                return jsonify({
                    'error': f'HubSpot API error {response.status_code}',
                    'message': response.text,
                    'imported': imported,
                    'existing': skipped,
                    'filtered': filtered,
                    'total_in_hubspot': total_processed
                }), response.status_code
            
            hubspot_data = response.json()
            contacts = hubspot_data.get('results', [])
            paging = hubspot_data.get('paging', {})
            
            logger.info(f"✅ Retrieved {len(contacts)} contacts from HubSpot (page {page})")
            total_processed += len(contacts)
            
            for contact in contacts:
                if imported >= MAX_IMPORTS_PER_RUN:
                    logger.info(f"🛑 Hit import limit of {MAX_IMPORTS_PER_RUN} contacts")
                    limit_reached = True
                    break
                
                props = contact.get('properties', {})
                hubspot_id = contact.get('id')
                
                def safe_get(key, default=''):
                    value = props.get(key)
                    if value is None:
                        return default
                    return str(value).strip()
                
                first = safe_get('firstname')
                last = safe_get('lastname')
                email = safe_get('email')
                phone = safe_get('phone')
                company = safe_get('company')
                lead_status = safe_get('hs_lead_status').lower()
                lifecycle_stage = safe_get('lifecyclestage').lower()
                personal_contact = safe_get('personal_contact').lower()
                
                name = f"{first} {last}".strip()
                if not name and email:
                    name = email.split('@')[0]
                if not name:
                    name = f"HubSpot-{hubspot_id}"
                
                if personal_contact == 'true':
                    filtered += 1
                    logger.warning(f"⚠️ Filtered (personal contact): {name}")
                    continue
                
                if not email or not company or not name or not phone:
                    filtered += 1
                    logger.warning(f"⚠️ Filtered (missing required fields): {name}")
                    continue
                
                if lead_status in EXCLUDED_LEAD_STATUSES:
                    filtered += 1
                    logger.warning(f"⚠️ Filtered (lead status: {lead_status}): {name}")
                    continue
                
                if lifecycle_stage in EXCLUDED_LIFECYCLE_STAGES:
                    filtered += 1
                    logger.warning(f"⚠️ Filtered (lifecycle: {lifecycle_stage}): {name}")
                    continue
                
                cursor.execute('SELECT id FROM contacts WHERE email = ? OR hubspot_id = ?', (email, hubspot_id))
                if cursor.fetchone():
                    skipped += 1
                    logger.info(f"⏭️  Skipped (exists): {name}")
                    continue
                
                cursor.execute('''
                    INSERT INTO contacts 
                    (name, firstname, lastname, email, phone, company, title, 
                     hubspot_id, linkedin_url, lead_status, lifecycle_stage, enrichment_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                ''', (
                    name, first, last, email, phone, company,
                    safe_get('jobtitle'), hubspot_id, safe_get('linkedin_url'),
                    safe_get('hs_lead_status'), safe_get('lifecyclestage')
                ))
                
                imported += 1
                logger.info(f"✅ Imported ({imported}/{MAX_IMPORTS_PER_RUN}): {name} - {company}")
            
            if not limit_reached:
                after = paging.get('next', {}).get('after')
                has_more = after is not None
                
                if has_more:
                    logger.info(f"🔄 More contacts available, fetching next page...")
                    page += 1
                else:
                    logger.info(f"🏁 Reached end of contacts")
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Import complete: {imported} new, {skipped} existing, {filtered} filtered from {total_processed} total")
        
        return jsonify({
            'success': True,
            'imported': imported,
            'existing': skipped,
            'filtered': filtered,
            'total_in_hubspot': total_processed,
            'message': f'Successfully imported {imported} new contacts from {total_processed} total in HubSpot ({filtered} filtered out)'
        })
        
    except Exception as e:
        logger.error(f"❌ Error importing from HubSpot: {e}")
        logger.error(traceback.format_exc())
        if 'conn' in locals():
            conn.close()
        return jsonify({
            'error': 'Import failed',
            'message': str(e),
            'imported': 0,
            'existing': 0,
            'filtered': 0,
            'total_in_hubspot': 0
        }), 500


@app.route('/api/contacts/<int:contact_id>/score', methods=['POST'])
def score_single_contact(contact_id):
    """Score a single contact"""
    try:
        logger.info(f"🎯 Scoring contact {contact_id}...")
        
        conn = get_db()
        
        # Use the scoring wrapper
        if score_contact_from_db:
            result = score_contact_from_db(conn, contact_id, trigger='manual')
            
            # The wrapper should have updated the database
            conn.commit()
            
            # Fetch the updated scores to return
            cursor = conn.cursor()
            cursor.execute('''
                SELECT mdcp_score, rss_score, priority_score, urgency_level, 
                       mdcp_tier, rss_tier, recommended_action
                FROM contacts WHERE id = ?
            ''', (contact_id,))
            row = cursor.fetchone()
            
            if row:
                logger.info(f"✅ Scored contact {contact_id}")
                return jsonify({
                    'success': True,
                    'contact_id': contact_id,
                    'scores': {
                        'mdcp_score': row['mdcp_score'],
                        'rss_score': row['rss_score'],
                        'priority_score': row['priority_score'],
                        'urgency_level': row['urgency_level'],
                        'mdcp_tier': row['mdcp_tier'],
                        'rss_tier': row['rss_tier'],
                        'recommended_action': row['recommended_action']
                    }
                })
            else:
                # Return the result from wrapper even if fetch failed
                logger.info(f"✅ Scored contact {contact_id} (fetch failed)")
                return jsonify(result)
        else:
            # Fallback scoring
            logger.warning("Using fallback scoring")
            # ... existing fallback code ...
            
    except Exception as e:
        logger.error(f"❌ Error scoring contact {contact_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        conn.close()
        
    
@app.route('/api/contacts/score-batch', methods=['POST'])
def score_batch_contacts():
    """Score multiple contacts in batch"""
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 50)
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM contacts 
            WHERE mdcp_score IS NULL OR last_scored IS NULL
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        contact_ids = [row[0] for row in cursor.fetchall()]
        
        if not contact_ids:
            conn.close()
            return jsonify({
                'success': True,
                'scored': 0,
                'failed': 0,
                'total': 0,
                'message': 'No contacts need scoring'
            })
        
        logger.info(f"🎯 Starting batch scoring for {len(contact_ids)} contacts...")
        
        results = bulk_score_contacts(conn, contact_ids, trigger='batch')
        
        scored = sum(1 for r in results if r.get('success'))
        failed = len(results) - scored
        
        conn.close()
        
        logger.info(f"✅ Batch scoring complete: {scored} scored, {failed} failed")
        
        return jsonify({
            'success': True,
            'scored': scored,
            'failed': failed,
            'total': len(contact_ids),
            'results': results
        })
    
    except Exception as e:
        logger.error(f"❌ Error in batch scoring: {e}")
        logger.error(traceback.format_exc())
        if 'conn' in locals():
            conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    """Enrich a single contact with REAL AI intelligence using Perplexity"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Contact not found'
            }), 404
        
        if contact['enrichment_status'] == 'complete':
            conn.close()
            return jsonify({
                'success': True,
                'message': 'Contact already enriched',
                'contact_id': contact_id
            }), 200
        
        # Update status to processing
        cursor.execute("""
            UPDATE contacts 
            SET enrichment_status = 'processing',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (contact_id,))
        conn.commit()
        
        logger.info(f"🔍 Starting AI enrichment for contact {contact_id}: {contact['name']}")
        
        # Check if enrichment engine is available
        if not ENRICHMENT_AVAILABLE or not PERPLEXITY_API_KEY:
            logger.warning("⚠️ Enrichment engine or API key not available, using fallback")
            enrichment_data = {
                'enriched_at': datetime.now().isoformat(),
                'source': 'fallback',
                'note': 'Enrichment engine not available. Install perplexity_enrichment or add PERPLEXITY_API_KEY',
                'company_info': {
                    'name': contact['company'],
                    'industry': 'Unknown'
                },
                'professional_background': {
                    'current_title': contact['title']
                }
            }
        else:
            # REAL AI ENRICHMENT
            try:
                enricher = PerplexityEnrichment(api_key=PERPLEXITY_API_KEY)
                
                # Build contact dict for enricher
                contact_dict = {
                    'id': contact['id'],
                    'name': contact['name'],
                    'email': contact['email'],
                    'company': contact['company'],
                    'title': contact['title'],
                    'phone': contact['phone'],
                    'linkedin_url': contact['linkedin_url']
                }
                
                logger.info(f"📡 Calling Perplexity API for {contact['name']}...")
                
                result = enricher.enrich_contact(contact_dict)
                
                logger.info(f"📦 Result type: {type(result)}, keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
                
                # The enrichment saves to file but may not return it in the dict
                profile_file = f"profile_{contact_id}.txt"
                full_profile = ""
                
                # Try to get from result first
                if result and isinstance(result, dict):
                    enrichment_data = result.get('enrichment_data', result)
                    full_profile = (
                        enrichment_data.get('full_profile_text') or
                        enrichment_data.get('full_profile') or
                        enrichment_data.get('perplexity_insights') or
                        ''
                    )
                    logger.info(f"📋 Profile from result: {len(full_profile)} chars")
                    
                # If no profile in result, read from file
                if not full_profile and os.path.exists(profile_file):
                    try:
                        with open(profile_file, 'r', encoding='utf-8') as f:
                            full_profile = f.read()
                        logger.info(f"📖 Read {len(full_profile)} chars from {profile_file}")
                    except Exception as file_err:
                        logger.error(f"Error reading profile file: {file_err}")
                        
                # Build enrichment data with the profile
                if not enrichment_data or not isinstance(enrichment_data, dict):
                    enrichment_data = {}
                    
                enrichment_data['full_profile_text'] = full_profile
                enrichment_data['perplexity_insights'] = full_profile
                enrichment_data['enriched_at'] = datetime.now().isoformat()
                enrichment_data['source'] = 'perplexity_ai'
                enrichment_data['profile_length'] = len(full_profile)
                
                if full_profile:
                    logger.info(f"✅ Successfully enriched {contact['name']} - {len(full_profile)} chars")
                else:
                    raise Exception("No profile data generated")
                    
            except Exception as enrich_err:
                logger.error(f"❌ Enrichment failed: {enrich_err}")
                logger.error(traceback.format_exc())
                enrichment_data = {
                    'enriched_at': datetime.now().isoformat(),
                    'source': 'error_fallback',
                    'error': str(enrich_err),
                    'note': f'Enrichment failed: {str(enrich_err)}',
                    'company_info': {
                        'name': contact['company']
                    }
                }
                
        # Save enrichment data
        cursor.execute("""
            UPDATE contacts 
            SET enrichment_status = 'complete',
                enrichment_data = ?,
                enriched = 1,
                enrichment_date = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(enrichment_data), datetime.now().isoformat(), contact_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Contact {contact_id} enrichment saved to database")
        
        return jsonify({
            'success': True,
            'message': 'Contact enriched successfully with AI intelligence',
            'contact_id': contact_id,
            'source': enrichment_data.get('source'),
            'data_size': len(json.dumps(enrichment_data))
        }), 200
    
    except Exception as e:
        logger.error(f"Error enriching contact {contact_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Try to reset status on error
        try:
            cursor.execute("""
                UPDATE contacts 
                SET enrichment_status = 'failed',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (contact_id,))
            conn.commit()
        except:
            pass
            
        if 'conn' in locals():
            conn.close()
            
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
@app.route('/api/contacts/<int:contact_id>/intelligence', methods=['GET'])
def get_contact_intelligence(contact_id):
    """Get full intelligence data for a contact - FIXED"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': False,
                'error': 'Contact not found'
            }), 404
        
        # Safely parse enrichment_data
        enrichment_data = {}
        if row['enrichment_data']:
            try:
                enrichment_data = json.loads(row['enrichment_data'])
            except:
                pass
        
        # Build contact dict from row
        contact_data = {
            'id': row['id'],
            'name': row['name'],
            'firstname': row['firstname'],
            'lastname': row['lastname'],
            'email': row['email'],
            'company': row['company'],
            'title': row['title'],
            'phone': row['phone'],
            'linkedin_url': row['linkedin_url'],
            'enrichment_status': row['enrichment_status'],
            'enrichment_date': row['enrichment_date'] or row['last_scored'],
            'mdcp_score': row['mdcp_score'],
            'rss_score': row['rss_score'],
            'priority_score': row['priority_score'],
            'urgency_level': row['urgency_level'],
            'persona_type': row['persona_type'],
            'persona_tier': row['persona_tier'],
            'mdcp_tier': row['mdcp_tier'],
            'rss_tier': row['rss_tier']
        }
        
        return jsonify({
            'success': True,
            'contact': contact_data,
            'enrichment_data': enrichment_data,
            'dashboard': enrichment_data  # Same as enrichment_data since no separate dashboard column
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching intelligence for contact {contact_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/contacts/<int:contact_id>/reset-enrichment', methods=['POST'])
def reset_enrichment(contact_id):
    """Reset enrichment status to allow re-enrichment"""
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
    
@app.route('/api/contacts/<int:contact_id>/report-issue', methods=['POST'])
def report_issue(contact_id):
    """Log reported profile issues"""
    try:
        data = request.get_json()
        reason = data.get('reason', 'No reason provided')
        logger.warning(f"⚠️ Profile issue reported for contact {contact_id}: {reason}")
        # TODO: Save to issues table or send notification
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/api/apex/scores', methods=['GET'])
def get_apex_intelligence_scores():
    """Get all Apex Intelligence scores for dashboard"""
    try:
        conn = get_db()
        result = get_apex_scores(conn)
        conn.close()
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"❌ Error getting Apex scores: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/preferences', methods=['GET'])
def get_user_preferences():
    """Get current user's scoring preferences"""
    user_id = request.headers.get('X-User-Id', 'default')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            'user_id': row['user_id'],
            'scoring_profile': row['scoring_profile'],
            'custom_ideal_titles': json.loads(row['custom_ideal_titles'] or '[]'),
            'custom_avoid_titles': json.loads(row['custom_avoid_titles'] or '[]'),
            'ideal_company_size_min': row['ideal_company_size_min'],
            'ideal_company_size_max': row['ideal_company_size_max'],
            'target_seniority_levels': json.loads(row['target_seniority_levels'] or '[]'),
            'exclude_c_suite': row['exclude_c_suite']
        })
    else:
        return jsonify({
            'user_id': user_id,
            'scoring_profile': 'DEFAULT',
            'message': 'No preferences set yet'
        })
    
@app.route('/api/user/preferences', methods=['POST'])
def update_user_preferences():
    """Update user's scoring preferences"""
    user_id = request.headers.get('X-User-Id', 'default')
    data = request.get_json()
    
    from intelligence.engines.scoring.user_scoring_engine import UserSpecificScoringEngine
    
    engine = UserSpecificScoringEngine(user_id)
    engine.update_preferences(data)
    
    return jsonify({
        'success': True,
        'message': 'Preferences updated successfully',
        'user_id': user_id
    })
    
@app.route('/api/user/onboarding', methods=['POST'])
def user_onboarding():
    """Save user preferences from onboarding"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                scoring_profile TEXT DEFAULT 'DEFAULT',
                custom_ideal_titles TEXT,
                custom_avoid_titles TEXT,
                ideal_company_size_min INTEGER,
                ideal_company_size_max INTEGER,
                ideal_industries TEXT,
                target_seniority_levels TEXT,
                exclude_c_suite BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Convert lists to JSON strings
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences 
            (user_id, scoring_profile, custom_ideal_titles, custom_avoid_titles, 
             ideal_company_size_min, ideal_company_size_max, ideal_industries,
             target_seniority_levels, exclude_c_suite, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            user_id,
            data.get('industry', 'DEFAULT'),
            json.dumps(data.get('ideal_titles', [])),
            json.dumps(data.get('avoid_titles', [])),
            data.get('min_company_size', 50),
            data.get('max_company_size', 5000),
            json.dumps(data.get('target_industries', [])),
            json.dumps(data.get('seniority_levels', [])),
            data.get('exclude_c_suite', False)
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Preferences saved successfully',
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Onboarding error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/api/user/preferences/<user_id>', methods=['GET'])
def get_user_preferences_by_id(user_id):  # <-- RENAMED FUNCTION
    """Get user's scoring preferences"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Convert row to dict
            columns = [desc[0] for desc in cursor.description]
            pref_dict = dict(zip(columns, row))
            
            return jsonify({
                'success': True,
                'user_id': pref_dict.get('user_id'),
                'scoring_profile': pref_dict.get('scoring_profile'),
                'custom_ideal_titles': json.loads(pref_dict.get('custom_ideal_titles') or '[]'),
                'custom_avoid_titles': json.loads(pref_dict.get('custom_avoid_titles') or '[]'),
                'ideal_company_size_min': pref_dict.get('ideal_company_size_min'),
                'ideal_company_size_max': pref_dict.get('ideal_company_size_max'),
                'target_seniority_levels': json.loads(pref_dict.get('target_seniority_levels') or '[]'),
                'exclude_c_suite': bool(pref_dict.get('exclude_c_suite'))
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No preferences found for user'
            })
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
    
@app.route('/api/apex/score-all', methods=['POST'])
def score_all_contacts():
    """Score all unscored contacts"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM contacts 
            WHERE mdcp_score IS NULL OR last_scored IS NULL
        ''')
        
        contact_ids = [row[0] for row in cursor.fetchall()]
        
        if not contact_ids:
            conn.close()
            return jsonify({
                'success': True,
                'message': 'All contacts already scored',
                'scored': 0
            })
        
        logger.info(f"🎯 Scoring all {len(contact_ids)} contacts...")
        
        results = bulk_score_contacts(conn, contact_ids, trigger='batch_all')
        scored = sum(1 for r in results if r.get('success'))
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Scored {scored} contacts',
            'scored': scored,
            'total': len(contact_ids)
        })
    
    except Exception as e:
        logger.error(f"❌ Error scoring all contacts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/verify-vertical', methods=['POST'])
def verify_contact_vertical(contact_id):
    """Verify if contact is in CRE vertical"""
    try:
        from intelligence.engines.scoring.vertical_verifier import VerticalVerifier
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get contact and enrichment data
        cursor.execute('''
            SELECT id, name, title, company, enrichment_data 
            FROM contacts 
            WHERE id = ?
        ''', (contact_id,))
        
        row = cursor.fetchone()
        if not row:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        
        contact = dict(row)
        enrichment_data = {}
        if contact['enrichment_data']:
            try:
                enrichment_data = json.loads(contact['enrichment_data'])
            except:
                pass
                
        # Verify vertical
        verifier = VerticalVerifier()
        verification = verifier.verify_from_enrichment(contact, enrichment_data)
        
        # Save verification result
        cursor.execute('''
            UPDATE contacts 
            SET vertical_verification = ? 
            WHERE id = ?
        ''', (json.dumps(verification), contact_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'verification': verification
        })
    
    except Exception as e:
        logger.error(f"Error verifying vertical: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/api/apex/scores', methods=['GET'])
def get_apex_scores_endpoint():
    """Get all scored contacts for Apex Intelligence dashboard"""
    try:
        conn = get_db()
        
        if get_apex_scores:
            # Use the scoring wrapper function
            result = get_apex_scores(conn)
            conn.close()
            return jsonify(result)
        else:
            # Fallback - get scored contacts directly
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, company, email, title,
                       mdcp_score, mdcp_tier,
                       rss_score, rss_tier,
                       priority_score, urgency_level,
                       lifecycle_stage, recommended_action
                FROM contacts
                WHERE priority_score IS NOT NULL
                ORDER BY priority_score DESC
            ''')
            
            columns = [desc[0] for desc in cursor.description]
            contacts = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.close()
            
            return jsonify({
                'status': 'success',
                'count': len(contacts),
                'contacts': contacts
            })
        
    except Exception as e:
        logger.error(f"Error getting apex scores: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

if __name__ == '__main__':
    ensure_scoring_columns()
    logger.info(f"✅ Apex API Server starting on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT, debug=True)
    