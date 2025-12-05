#!/usr/bin/env python3
"""
Apex API Server - Flask Version with REAL AI Enrichment + Scoring
"""
from config import *
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

# ============= LOAD ENV ONCE AT THE TOP =============
load_dotenv('/Users/chrisrabenold/projects/apex/.env')

# ============= FIX PATH TO ENRICHMENT & SCORING ENGINES =============
BACKEND_PATH = '/Users/chrisrabenold/projects/apex/apps/backend'
sys.path.insert(0, BACKEND_PATH)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get API keys - TRY ALL POSSIBLE ENVIRONMENT VARIABLE NAMES
HUBSPOT_TOKEN = (
    os.getenv('HUBSPOT_ACCESS_TOKEN') or 
    os.getenv('HUBSPOT_API_KEY') or 
    os.getenv('HUBSPOT_ACCESS_KEY')
)
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Debug: Print what we loaded
logger.info(f"Loaded HubSpot Token: {HUBSPOT_TOKEN[:20] if HUBSPOT_TOKEN else 'NONE'}...")
logger.info(f"Perplexity Key: {'✅ Found' if PERPLEXITY_API_KEY else '❌ Missing'}")
logger.info(f"OpenAI Key: {'✅ Found' if OPENAI_API_KEY else '❌ Missing'}")

# Try to import enrichment engine
ENRICHMENT_AVAILABLE = False
PerplexityEnrichment = None

try:
    from intelligence.engines.enrichment.apex_intelligence_engine import ApexScoringEngine
    from intelligence.engines.enrichment.scoring_orchestrator import ScoringOrchestrator
    SCORING_AVAILABLE = True
    logger.info("✅ Scoring engines loaded successfully")
except ImportError as e:
    SCORING_AVAILABLE = False
    ApexScoringEngine = None
    ScoringOrchestrator = None
    logger.warning(f"⚠️ Scoring engines not available: {e}")
    
# Try to import scoring engine
SCORING_AVAILABLE = False
score_contact_func = None

try:
    from intelligence.engines.scoring.apex_intelligence_engine import score_contact as score_contact_func
    SCORING_AVAILABLE = True
    logger.info(f"✅ Scoring engine loaded")
except ImportError as e:
    logger.warning(f"⚠️ Could not load scoring engine: {e}")
    
# Verify tokens loaded
if HUBSPOT_TOKEN:
    logger.info(f"✅ HubSpot Token Loaded")
else:
    logger.warning("⚠️ HubSpot Token NOT FOUND")
    
if PERPLEXITY_API_KEY:
    logger.info(f"✅ Perplexity API Key Loaded")
else:
    logger.warning("⚠️ Perplexity API Key NOT FOUND")
    
# Initialize Flask
app = Flask(__name__)
CORS(app)

# Configuration
DATABASE = '/Users/chrisrabenold/projects/apex/apex.db'
PORT = 8000

# ... rest of your helper functions stay the same ...


# ============= HELPER FUNCTIONS =============

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def column_exists(cursor, table, column):
    """Check if a column exists in a table"""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns

def init_db():
    """Initialize database with complete schema and migrations"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create comprehensive contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            firstname TEXT,
            lastname TEXT,
            email TEXT,
            phone TEXT,
            company TEXT,
            title TEXT,
            hubspot_id TEXT UNIQUE,
            linkedin_url TEXT,
            lead_status TEXT,
            lifecycle_stage TEXT,
            enrichment_status TEXT DEFAULT 'pending',
            enrichment_data TEXT DEFAULT '{}',
            enrichment_date TEXT,
            opportunity_score REAL,
            priority_score REAL,
            mdcp_score REAL,
            rss_score REAL,
            persona_tier TEXT,
            persona_type TEXT,
            urgency_level TEXT DEFAULT 'LOW',
            recommended_action TEXT,
            enriched INTEGER DEFAULT 0,
            last_scored TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migrate existing database - add missing columns
    migrations = [
        ('firstname', 'TEXT'),
        ('lastname', 'TEXT'),
        ('lead_status', 'TEXT'),
        ('lifecycle_stage', 'TEXT'),
        ('opportunity_score', 'REAL'),
        ('priority_score', 'REAL'),
        ('mdcp_score', 'REAL'),
        ('rss_score', 'REAL'),
        ('persona_tier', 'TEXT'),
        ('persona_type', 'TEXT'),
        ('urgency_level', 'TEXT DEFAULT "LOW"'),
        ('recommended_action', 'TEXT'),
        ('linkedin_url', 'TEXT'),
        ('hubspot_id', 'TEXT'),
        ('enrichment_date', 'TEXT'),
        ('last_scored', 'TEXT')
    ]
    
    for column_name, column_type in migrations:
        if not column_exists(cursor, 'contacts', column_name):
            try:
                cursor.execute(f'ALTER TABLE contacts ADD COLUMN {column_name} {column_type}')
                logger.info(f"✅ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                logger.warning(f"⚠️ Column {column_name} migration issue: {e}")
    
    conn.commit()
    conn.close()

def _extract_section(text, start_marker, end_marker):
    """Helper to extract text sections from the profile"""
    if not text or not start_marker:
        return ""
    
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return ""
    
    if end_marker:
        end_idx = text.find(end_marker, start_idx)
        if end_idx == -1:
            return text[start_idx:]
        return text[start_idx:end_idx].strip()
    
    return text[start_idx:].strip()

# ============= ROUTES =============

@app.route('/')
def home():
    """API homepage"""
    return jsonify({
        'name': 'Apex API',
        'version': '2.5.0',
        'status': 'online',
        'hubspot_configured': bool(HUBSPOT_TOKEN),
        'enrichment_available': ENRICHMENT_AVAILABLE,
        'endpoints': {
            'health': '/health',
            'contacts': '/api/contacts',
            'analytics': '/api/analytics/dashboard',
            'enrich': '/api/contacts/<id>/deep-enrich',
            'intelligence': '/api/contacts/<id>/intelligence',
            'hubspot_import': '/api/hubspot/import'
        }
    })

@app.route('/health')
def health():
    """Health check"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM contacts")
    count = cursor.fetchone()[0]
    conn.close()
    
    return jsonify({
        'status': 'healthy',
        'contacts_count': count,
        'hubspot_configured': bool(HUBSPOT_TOKEN),
        'perplexity_configured': bool(PERPLEXITY_API_KEY),
        'enrichment_available': ENRICHMENT_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

# ============= CONTACTS ENDPOINTS =============


@app.route('/api/db-test')
def db_test():
    """Test database connection"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("SELECT sql FROM sqlite_master WHERE name='contacts'")
        schema = cursor.fetchone()
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM contacts")
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'database': DATABASE,
            'connected': True,
            'record_count': count,
            'has_schema': bool(schema)
        })
    except Exception as e:
        return jsonify({
            'database': DATABASE,
            'connected': False,
            'error': str(e)
        })

@app.route('/api/contacts', methods=['GET', 'POST'])
def contacts():
    """List contacts or create new one"""
    conn = get_db()
    
    if request.method == 'GET':
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, firstname, lastname, email, phone, company, title, 
                   lead_status, lifecycle_stage, enrichment_status, enriched, 
                   priority_score, mdcp_score, urgency_level, created_at
            FROM contacts 
            ORDER BY priority_score DESC NULLS LAST, created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        contacts_list = []
        for row in cursor.fetchall():
            contact = dict(row)
            contact['status_badge'] = '✅ Enriched' if contact.get('enriched') == 1 else '⏳ Pending'
            contacts_list.append(contact)
            
        conn.close()
        return jsonify(contacts_list)
    
    elif request.method == 'POST':
        data = request.get_json()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contacts (name, firstname, lastname, email, phone, company, title, lead_status, lifecycle_stage)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('firstname'),
            data.get('lastname'),
            data.get('email'),
            data.get('phone'),
            data.get('company'),
            data.get('title'),
            data.get('lead_status'),
            data.get('lifecycle_stage')
        ))
        
        conn.commit()
        contact_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'id': contact_id,
            'message': 'Contact created successfully'
        }), 201

@app.route('/api/contacts/<int:contact_id>')
def get_contact(contact_id):
    """Get single contact"""
    conn = get_db()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    conn.close()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    return jsonify(dict(contact))

@app.route('/api/contacts/<int:contact_id>/intelligence')
def get_contact_intelligence(contact_id):
    """Get full intelligence report for display in dashboard"""
    conn = get_db()
    
    contact = conn.execute('''
        SELECT id, name, firstname, lastname, email, phone, company, 
               linkedin_url, enrichment_data, mdcp_score, rss_score, 
               priority_score, urgency_level, enrichment_status, 
               enrichment_date, last_scored, lead_status, lifecycle_stage
        FROM contacts 
        WHERE id = ?
    ''', (contact_id,)).fetchone()
    
    conn.close()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    contact_dict = dict(contact)
    
    # Parse the enrichment data
    enrichment_data = {}
    if contact_dict.get('enrichment_data'):
        try:
            enrichment_data = json.loads(contact_dict['enrichment_data'])
        except Exception as e:
            logger.error(f"❌ Error parsing enrichment data: {e}")
            enrichment_data = {}
    
    # Build the response
    response = {
        'contact': {
            'id': contact_dict['id'],
            'name': contact_dict['name'],
            'firstname': contact_dict.get('firstname'),
            'lastname': contact_dict.get('lastname'),
            'email': contact_dict['email'],
            'phone': contact_dict['phone'],
            'company': contact_dict['company'],
            'linkedin_url': contact_dict['linkedin_url'],
            'lead_status': contact_dict.get('lead_status'),
            'lifecycle_stage': contact_dict.get('lifecycle_stage'),
            'mdcp_score': contact_dict['mdcp_score'],
            'rss_score': contact_dict['rss_score'],
            'priority_score': contact_dict['priority_score'],
            'urgency_level': contact_dict['urgency_level'],
            'enrichment_status': contact_dict['enrichment_status'],
            'enrichment_date': contact_dict['enrichment_date']
        },
        'enrichment_data': enrichment_data,
        'dashboard': {
            'full_profile_text': enrichment_data.get('full_profile_text', ''),
            'perplexity_insights': enrichment_data.get('perplexity_insights', ''),
            'metadata': enrichment_data.get('metadata', {})
        }
    }
    
    return jsonify(response)

@app.route('/api/contacts/<int:contact_id>/deep-enrich', methods=['POST'])
def enrich_contact_endpoint(contact_id):
    """Deep enrichment pipeline: Perplexity → Intelligence Compilation → Scoring"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
        contact_row = cursor.fetchone()
        
        if not contact_row:
            conn.close()
            return jsonify({'success': False, 'message': 'Contact not found'}), 404
        
        contact_dict = dict(contact_row)
        conn.close()
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 APEX DEEP INTELLIGENCE PIPELINE")
        logger.info(f"{'='*70}")
        logger.info(f"Contact: {contact_dict.get('name')} @ {contact_dict.get('company')}")
        
        # STEP 1: Perplexity Web Search
        logger.info(f"\n📡 STEP 1: Perplexity Web Search (Raw Data Collection)...")
        
        if not ENRICHMENT_AVAILABLE or not PERPLEXITY_API_KEY:
            return jsonify({'success': False, 'message': 'Enrichment not available'}), 500
        
        try:
            enricher = PerplexityEnrichment(api_key=PERPLEXITY_API_KEY)
            enrichment_result = enricher.enrich_contact(contact_dict)
            
            if enrichment_result.get('status') != 'success':
                raise Exception(enrichment_result.get('message', 'Enrichment failed'))
                
            logger.info("✅ Raw web search complete")
            
        except Exception as e:
            logger.error(f"❌ Enrichment failed: {e}")
            return jsonify({'success': False, 'message': f'Enrichment error: {str(e)}'}), 500
        
        # STEP 2: Intelligence Compilation
        logger.info(f"\n🧠 STEP 2: GPT-4 Intelligence Compilation...")
        
        try:
            from intelligence.engines.enrichment.intelligence_compiler import IntelligenceCompiler
            
            compiler = IntelligenceCompiler()
            enrichment_data_only = enrichment_result.get('enrichment_data', {})
            raw_results = enrichment_data_only.get('raw_responses', [])
            
            logger.info(f"   📊 Raw results count: {len(raw_results)}")
            
            # Fallback to file if needed
            if len(raw_results) == 0:
                raw_file_path = enrichment_result.get('raw_file', f"profile_{contact_id}.txt")
                
                if os.path.exists(raw_file_path):
                    with open(raw_file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    raw_results = [{'content': file_content, 'model': 'file_fallback'}]
                    logger.info(f"   ✅ Loaded {len(file_content)} chars from {raw_file_path}")
            
            if len(raw_results) > 0:
                intelligence_dossier = compiler.compile_dossier(contact_dict, raw_results)
                logger.info(f"✅ Intelligence dossier compiled")
                logger.info(f"   Data Quality: {intelligence_dossier.get('metadata', {}).get('data_quality')}")
                logger.info(f"   Completeness: {intelligence_dossier.get('metadata', {}).get('completeness_score')}%")
            else:
                intelligence_dossier = {
                    "error": "No search results available",
                    "metadata": {"data_quality": "NONE", "completeness_score": 0}
                }
                
        except Exception as e:
            logger.error(f"❌ Intelligence compilation failed: {e}", exc_info=True)
            intelligence_dossier = {
                "error": str(e),
                "metadata": {"data_quality": "ERROR", "completeness_score": 0}
            }
            
        # STEP 3: Save to Database
        logger.info(f"\n💾 STEP 3: Saving intelligence to database...")
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE contacts
            SET enrichment_status = 'complete',
                enriched = 1,
                enrichment_data = ?,
                enrichment_date = ?,
                title = COALESCE(?, title),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            json.dumps(intelligence_dossier),
            datetime.now().isoformat(),
            intelligence_dossier.get('overview', {}).get('current_title'),
            contact_id
        ))
        
        conn.commit()
        conn.close()
        
        logger.info("✅ Intelligence saved to database")
        
        # STEP 4: MDCP/RSS Scoring
        logger.info(f"\n📊 STEP 4: MDCP/RSS Scoring...")
        
        if SCORING_AVAILABLE and score_contact_func:
            try:
                scoring_result = score_contact_func(contact_id, db_path=DATABASE)
                logger.info(f"✅ Scoring complete - Priority: {scoring_result.get('priority_score')}")
            except Exception as e:
                logger.error(f"❌ Scoring failed: {e}")
                scoring_result = {'priority_score': 50, 'mdcp_score': 50, 'rss_score': 0}
        else:
            scoring_result = {'priority_score': 50, 'mdcp_score': 50, 'rss_score': 0}
            
        # Final Result
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ APEX DEEP INTELLIGENCE PIPELINE COMPLETE")
        logger.info(f"   Intelligence Quality: {intelligence_dossier.get('metadata', {}).get('data_quality')}")
        logger.info(f"   Priority Score: {scoring_result.get('priority_score')}")
        logger.info(f"{'='*70}\n")
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'message': 'Deep intelligence compilation complete',
            'intelligence': intelligence_dossier,
            'scoring': scoring_result,
            'pipeline': {
                'steps_completed': ['perplexity_search', 'intelligence_compilation', 'scoring'],
                'data_quality': intelligence_dossier.get('metadata', {}).get('data_quality'),
                'completeness': intelligence_dossier.get('metadata', {}).get('completeness_score')
            }
        })
    
    except Exception as e:
        logger.error(f"❌ PIPELINE FAILED: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    
@app.route('/api/contacts/<int:contact_id>/score', methods=['POST'])
def score_single_contact(contact_id):
    """Score a single contact using Apex Intelligence Engine"""
    
    if not SCORING_AVAILABLE:
        return jsonify({'error': 'Scoring engine not available'}), 500
    
    try:
        logger.info(f"🎯 Scoring contact {contact_id}...")
        
        # Initialize orchestrator
        conn = get_db()
        orchestrator = ScoringOrchestrator(conn)
        
        # Score the contact
        result = orchestrator.score_contact(contact_id, trigger='manual')
        conn.close()
        
        if 'error' in result:
            return jsonify(result), 500
        
        logger.info(f"✅ Scored contact {contact_id}: Priority={result.get('priority_score')}")
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'scores': {
                'mdcp_score': result.get('mdcp_score', 0),
                'rss_score': result.get('rss_score', 0),
                'priority_score': result.get('priority_score', 0)
            },
            'tiers': {
                'mdcp_tier': result.get('mdcp_tier', ''),
                'rss_tier': result.get('rss_tier', ''),
                'urgency_level': result.get('urgency_level', '')
            },
            'persona': result.get('persona', {}),
            'recommended_action': result.get('recommended_action', ''),
            'timestamp': result.get('timestamp')
        })
    
    except Exception as e:
        logger.error(f"❌ Error scoring contact {contact_id}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/api/contacts/score-batch', methods=['POST'])
def score_batch_contacts():
    """Score multiple contacts in batch"""
    
    if not SCORING_AVAILABLE:
        return jsonify({'error': 'Scoring engine not available'}), 500
    
    try:
        data = request.get_json() or {}
        limit = data.get('limit', 50)
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get unscored contacts
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
                'message': 'No contacts need scoring'
            })
        
        logger.info(f"🎯 Starting batch scoring for {len(contact_ids)} contacts...")
        
        orchestrator = ScoringOrchestrator(conn)
        results = orchestrator.bulk_score(contact_ids, trigger='batch')
        
        scored = sum(1 for r in results if 'error' not in r)
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
        import traceback
        logger.error(traceback.format_exc())
        if 'conn' in locals():
            conn.close()
        return jsonify({'error': str(e)}), 500
    
    
@app.route('/api/contacts/<int:contact_id>/scores', methods=['GET'])
def get_contact_scores(contact_id):
    """Get scoring details for a contact"""
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT mdcp_score, mdcp_tier, rss_score, rss_tier, 
                   priority_score, urgency_level, recommended_action,
                   persona_tier, persona_type, persona_confidence,
                   last_scored, calculation_version
            FROM contacts 
            WHERE id = ?
        ''', (contact_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Contact not found'}), 404
        
        columns = [desc[0] for desc in cursor.description]
        scores = dict(zip(columns, row))
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'scores': scores
        })
    
    except Exception as e:
        logger.error(f"❌ Error getting scores: {e}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/api/analytics/dashboard')
def analytics():
    """Dashboard analytics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'complete'")
    enriched = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'pending'")
    pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(COALESCE(opportunity_score, 0)) FROM contacts")
    avg_score_row = cursor.fetchone()
    avg_score = avg_score_row[0] if avg_score_row[0] else 0
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE created_at >= datetime('now', '-30 days')")
    last_30_days = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE urgency_level = 'HIGH'")
    high_priority = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_contacts': total,
        'enriched_contacts': enriched,
        'pending_enrichment': pending,
        'avg_opportunity_score': round(avg_score, 2),
        'contacts_last_30_days': last_30_days,
        'high_priority_contacts': high_priority
    })

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
    MAX_IMPORTS_PER_RUN = 100  # Limit to 100 new contacts per import
    
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
        limit_reached = False  # FLAG TO BREAK OUTER LOOP
        
        # Loop through all pages
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
            
            # Process contacts
            for contact in contacts:
                # Check limit before processing each contact
                if imported >= MAX_IMPORTS_PER_RUN:
                    logger.info(f"🛑 Hit import limit of {MAX_IMPORTS_PER_RUN} contacts")
                    limit_reached = True  # SET FLAG
                    break  # Break inner loop
                
                props = contact.get('properties', {})
                hubspot_id = contact.get('id')
                
                # SAFE EXTRACTION - Handles None values properly
                def safe_get(key, default=''):
                    """Safely get and strip a property value"""
                    value = props.get(key)
                    if value is None:
                        return default
                    return str(value).strip()
                
                # Extract contact info using safe getter
                first = safe_get('firstname')
                last = safe_get('lastname')
                email = safe_get('email')
                phone = safe_get('phone')
                company = safe_get('company')
                lead_status = safe_get('hs_lead_status').lower()
                lifecycle_stage = safe_get('lifecyclestage').lower()
                personal_contact = safe_get('personal_contact').lower()
                
                # Build name
                name = f"{first} {last}".strip()
                if not name and email:
                    name = email.split('@')[0]
                if not name:
                    name = f"HubSpot-{hubspot_id}"
                    
                # Filter out personal contacts
                if personal_contact == 'true':
                    filtered += 1
                    logger.warning(f"⚠️ Filtered (personal contact): {name}")
                    continue
                
                # Check required fields - must have email, company, name, and phone
                if not email or not company or not name or not phone:
                    filtered += 1
                    logger.warning(f"⚠️ Filtered (missing required fields): {name}")
                    continue
                
                # Check lead status exclusions
                if lead_status in EXCLUDED_LEAD_STATUSES:
                    filtered += 1
                    logger.warning(f"⚠️ Filtered (lead status: {lead_status}): {name}")
                    continue
                
                # Check lifecycle stage exclusions
                if lifecycle_stage in EXCLUDED_LIFECYCLE_STAGES:
                    filtered += 1
                    logger.warning(f"⚠️ Filtered (lifecycle: {lifecycle_stage}): {name}")
                    continue
                
                # Check if contact already exists by email or hubspot_id
                cursor.execute('SELECT id FROM contacts WHERE email = ? OR hubspot_id = ?', (email, hubspot_id))
                if cursor.fetchone():
                    skipped += 1
                    logger.info(f"⏭️  Skipped (exists): {name}")
                    continue
                
                # Insert new contact
                cursor.execute('''
                    INSERT INTO contacts 
                    (name, firstname, lastname, email, phone, company, title, 
                     hubspot_id, linkedin_url, lead_status, lifecycle_stage, enrichment_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                ''', (
                    name,
                    first,
                    last,
                    email,
                    phone,
                    company,
                    safe_get('jobtitle'),
                    hubspot_id,
                    safe_get('linkedin_url'),
                    safe_get('hs_lead_status'),
                    safe_get('lifecyclestage')
                ))
                
                imported += 1
                logger.info(f"✅ Imported ({imported}/{MAX_IMPORTS_PER_RUN}): {name} - {company}")
                
            # Check for next page (only if we haven't hit the limit)
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
        import traceback
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
    
# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error', 'message': str(error)}), 500

# ============= MAIN =============

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 APEX FLASK API SERVER")
    print("=" * 70)
    print(f"Server: http://localhost:{PORT}")
    print(f"Health: http://localhost:{PORT}/health")
    print(f"Docs: http://localhost:{PORT}/")
    print(f"HubSpot: {'✅ Configured' if HUBSPOT_TOKEN else '❌ Not Configured'}")
    if HUBSPOT_TOKEN:
        print(f"Token: {HUBSPOT_TOKEN[:15]}...")
    print(f"Enrichment: {'✅ Available' if ENRICHMENT_AVAILABLE else '❌ Not Available'}")
    print("=" * 70)
    print("\n📋 HubSpot Import Filters:")
    print("  ✓ Required: Email, Company, Name, Phone")
    print("  ✗ Excluded Lead Status: unqualified, do not contact, unsubscribe")
    print("  ✗ Excluded Lifecycle: unqualified")
    print("=" * 70)
    
    init_db()
    
    app.run(debug=True, host='0.0.0.0', port=PORT)
    