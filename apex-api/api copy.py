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

# ============= FIX PATH TO ENRICHMENT & SCORING ENGINES =============
# Define BACKEND_PATH first, before any other imports
BACKEND_PATH = '/Users/chrisrabenold/projects/apex/apps/backend'
sys.path.insert(0, BACKEND_PATH)

# Configure logging BEFORE any other imports
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API keys
HUBSPOT_API_KEY = os.environ.get('HUBSPOT_API_KEY')
HUBSPOT_ACCESS_TOKEN = os.environ.get('HUBSPOT_ACCESS_TOKEN')
PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

HUBSPOT_TOKEN = HUBSPOT_ACCESS_TOKEN or HUBSPOT_API_KEY

# Now try to import enrichment engine
ENRICHMENT_AVAILABLE = False
PerplexityEnrichment = None

try:
    from intelligence.engines.enrichment.perplexity_enrichment import PerplexityEnrichment
    ENRICHMENT_AVAILABLE = True
    logger.info(f"✅ Enrichment engine loaded from: {BACKEND_PATH}")
except ImportError as e:
    logger.warning(f"⚠️ Could not load enrichment engine: {e}")
    ENRICHMENT_AVAILABLE = False
    
# Try to import scoring engine
SCORING_AVAILABLE = False
score_contact_func = None

try:
    from intelligence.engines.scoring.apex_intelligence_engine import score_contact as score_contact_func
    SCORING_AVAILABLE = True
    logger.info(f"✅ Scoring engine loaded")
except ImportError as e:
    logger.warning(f"⚠️ Could not load scoring engine: {e}")
    SCORING_AVAILABLE = False
    
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
DATABASE = 'apex.db'
PORT = 8000

# ... rest of your code continues here ...


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
            email TEXT,
            phone TEXT,
            company TEXT,
            title TEXT,
            hubspot_id TEXT UNIQUE,
            linkedin_url TEXT,
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
    
    # If raw_responses is empty, try to manually build from the search results file
    def init_db():
        """Initialize database with complete schema and migrations"""
        conn = get_db()
        cursor = conn.cursor()
        
        # Create comprehensive contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ...
            )
        ''')
        
        # Migrate existing database - add missing columns
        migrations = [
            ('opportunity_score', 'REAL'),
            # etc
        ]
        
        # ... rest of init code
        
    conn.commit()
    conn.close()

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
            'score': '/api/contacts/<id>/score',
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

@app.route('/api/contacts', methods=['GET', 'POST'])
def contacts():
    """List contacts or create new one - Dashboard compatible"""
    conn = get_db()
    
    if request.method == 'GET':
        # Get query parameters for pagination
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, phone, company, title, 
                   enrichment_status, enriched, priority_score, 
                   mdcp_score, urgency_level, created_at
            FROM contacts 
            ORDER BY priority_score DESC NULLS LAST, created_at DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        contacts_list = []
        for row in cursor.fetchall():
            contact = dict(row)
            # Add display status
            if contact.get('enriched') == 1:
                contact['status_badge'] = '✅ Enriched'
            else:
                contact['status_badge'] = '⏳ Pending'
            contacts_list.append(contact)
            
        conn.close()
        
        return jsonify(contacts_list)
    
    
    elif request.method == 'POST':
        data = request.get_json()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO contacts (name, email, phone, company, title)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('email'),
            data.get('phone'),
            data.get('company'),
            data.get('title')
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
    contact = conn.execute(
        'SELECT * FROM contacts WHERE id = ?', 
        (contact_id,)
    ).fetchone()
    conn.close()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    return jsonify(dict(contact))

@app.route('/api/contacts/<int:contact_id>/deep-enrich', methods=['POST'])
def enrich_contact_endpoint(contact_id):
    """COMPLETE APEX PIPELINE: Enrich → Compile Intelligence → Score → Display"""
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
        
        # ================================================================
        # STEP 1: PERPLEXITY WEB SEARCH (Raw Data)
        # ================================================================
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
        
        # ================================================================
        # STEP 2: INTELLIGENCE COMPILATION (Deep Analysis)
        # ================================================================
        logger.info(f"\n🧠 STEP 2: GPT-4 Intelligence Compilation...")
        
        try:
            from intelligence.engines.enrichment.intelligence_compiler import IntelligenceCompiler
            
            compiler = IntelligenceCompiler()
            
            # Get JUST the enrichment_data part (which contains raw_responses)
            enrichment_data_only = enrichment_result.get('enrichment_data', {})
            
            # The raw_responses should be IN enrichment_data
            raw_results = enrichment_data_only.get('raw_responses', [])
            
            # Debug logging
            logger.info(f"   📊 Debug - enrichment_result keys: {list(enrichment_result.keys())}")
            logger.info(f"   📊 Debug - enrichment_data keys: {list(enrichment_data_only.keys())}")
            logger.info(f"   📊 Debug - Raw results count: {len(raw_results)}")
            
            # If raw_responses is empty, try to manually build from the search results file
            if len(raw_results) == 0:
                logger.warning("⚠️ No raw_responses found in enrichment_data!")
                logger.warning("   Trying to read from search results file...")
                
                # Try to read the raw file that was created
                raw_file_path = enrichment_result.get('raw_file')
                
                # If not in result, construct default path
                if not raw_file_path:
                    raw_file_path = f"search_results_{contact_id}.txt"
                    
                logger.info(f"   Looking for: {raw_file_path}")
                
                if os.path.exists(raw_file_path):
                    with open(raw_file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                        
                    # Create a single raw result with all the content
                    raw_results = [{
                        'content': file_content,
                        'model': 'file_fallback'
                    }]
                    logger.info(f"   ✅ Loaded {len(file_content)} chars from {raw_file_path}")
                else:
                    logger.error(f"   ❌ File not found: {raw_file_path}")
                    logger.error(f"   Current directory: {os.getcwd()}")
                    
            if len(raw_results) > 0:
                logger.info(f"   🎯 Compiling intelligence from {len(raw_results)} search results...")
                intelligence_dossier = compiler.compile_dossier(contact_dict, raw_results)
                
                logger.info(f"✅ Intelligence dossier compiled")
                logger.info(f"   Data Quality: {intelligence_dossier.get('metadata', {}).get('data_quality')}")
                logger.info(f"   Completeness: {intelligence_dossier.get('metadata', {}).get('completeness_score')}%")
            else:
                logger.error("❌ Still no data for GPT-4 to analyze!")
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
            
        # ================================================================
        # STEP 3: SAVE TO DATABASE
        # ================================================================
            
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
        
        # ================================================================
        # STEP 4: MDCP/RSS SCORING
        # ================================================================
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
            
        # ================================================================
        # FINAL RESULT
        # ================================================================
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ APEX DEEP INTELLIGENCE PIPELINE COMPLETE")
        logger.info(f"   Name: {intelligence_dossier.get('overview', {}).get('current_title')}")
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
    

#@app.route('/api/contacts/<int:contact_id>/score', methods=['POST'])
#def score_contact_endpoint(contact_id):
#   """Score a contact using MDCP/RSS (no enrichment)"""
#   try:
#       print(f"\n📊 Scoring contact {contact_id}...")
#       
#       if not ENRICHMENT_AVAILABLE:
#           return jsonify({
#               'success': False,
#               'message': 'Scoring engine not available'
#           }), 503
#       
#       scoring_result = ai_score(contact_id)
#       
#       return jsonify({
#           'success': True,
#           'contact_id': contact_id,
#           **scoring_result
#       })
#   except Exception as e:
#       print(f"❌ Scoring failed: {str(e)}")
#       return jsonify({
#           'success': False,
#           'message': str(e)
#       }), 500
#
#@app.route('/api/contacts/<int:contact_id>/generate-scripts', methods=['POST'])
#def generate_scripts(contact_id):
#   """Generate scripts for a contact"""
#   return jsonify({
#       'success': True,
#       'contact_id': contact_id,
#       'message': 'Scripts generated successfully',
#       'scripts': {
#           'email_1': 'Sample email script',
#           'call_1': 'Sample call script'
#       }
#   })

@app.route('/api/analytics/dashboard')
def analytics():
    """Dashboard analytics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'complete'")
    enriched = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'pending'")
    pending = cursor.fetchone()[0]
    
    # Safe query for average score with fallback
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

@app.route('/api/dashboard/<int:contact_id>')
def get_dashboard(contact_id):
    """Get intelligence report data for a contact - HANDLES BOTH FORMATS"""
    conn = get_db()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    conn.close()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    contact_dict = dict(contact)
    
    # Parse enrichment data
    intelligence = {}
    if contact_dict.get('enrichment_data'):
        try:
            intelligence = json.loads(contact_dict['enrichment_data'])
            logger.info(f"📊 Loaded intelligence dossier for contact {contact_id}")
            logger.info(f"   Sections: {list(intelligence.keys())}")
        except Exception as e:
            logger.error(f"❌ Error parsing intelligence: {e}")
            intelligence = {}
            
    # Detect format: NEW (GPT-4 dossier) vs OLD (basic parser)
    is_new_format = 'overview' in intelligence and isinstance(intelligence.get('overview'), dict)
    
    if is_new_format:
        # NEW FORMAT - GPT-4 Intelligence Dossier
        overview = intelligence.get('overview', {})
        background = intelligence.get('background', {})
        sales_intel = intelligence.get('sales_intelligence', {})
        
        response = {
            'contact': {
                'id': contact_dict.get('id'),
                'name': contact_dict.get('name'),
                'email': contact_dict.get('email'),
                'phone': contact_dict.get('phone') or intelligence.get('online_presence', {}).get('phone'),
                'company': overview.get('organization') or contact_dict.get('company'),
                'title': overview.get('current_title') or contact_dict.get('title') or 'Not available',
                'location': overview.get('location', 'N/A'),
            },
            'person_name': contact_dict.get('name'),
            'current_title': overview.get('current_title') or 'Not available',
            'overview': overview.get('summary', ''),
            'background': background.get('career_summary', ''),
            'work_history': background.get('work_history', []),
            'education': intelligence.get('education', []),
            'company_name': overview.get('organization') or contact_dict.get('company'),
            'skills_expertise': intelligence.get('skills_expertise', []),
            'personality_profile': intelligence.get('personality_profile', {}),
            'pain_points': sales_intel.get('talking_points', [])[:3] or ['Need to scale operations', 'Compliance requirements', 'Digital transformation'],
            'talking_points': sales_intel.get('talking_points', []) or ['ROI on automation', 'Compliance features', 'Integration capabilities'],
            'trigger_events': intelligence.get('fun_facts', []) or ['Recent appointment', 'Company expansion', 'Market changes'],
            'deals_database': intelligence.get('deals_database', []),
            'fun_facts': intelligence.get('fun_facts', []),
            'data_quality': intelligence.get('metadata', {}).get('data_quality', 'UNKNOWN'),
            'completeness_score': intelligence.get('metadata', {}).get('completeness_score', 0),
        }
    else:
        # OLD FORMAT - Basic Parser (fallback)
        logger.warning(f"⚠️ Contact {contact_id} using OLD enrichment format")
        
        response = {
            'contact': {
                'id': contact_dict.get('id'),
                'name': contact_dict.get('name'),
                'email': contact_dict.get('email'),
                'phone': contact_dict.get('phone'),
                'company': intelligence.get('company_name') or contact_dict.get('company'),
                'title': intelligence.get('current_title') or contact_dict.get('title') or 'Not available',
                'location': 'N/A',
            },
            'person_name': intelligence.get('person_name') or contact_dict.get('name'),
            'current_title': intelligence.get('current_title') or 'Not available',
            'overview': intelligence.get('overview', ''),
            'background': intelligence.get('background', ''),
            'work_history': intelligence.get('work_history', []),
            'education': intelligence.get('education', []),
            'company_name': intelligence.get('company_name') or contact_dict.get('company'),
            'skills_expertise': [],
            'personality_profile': {'mbti_inference': intelligence.get('myers_briggs', 'Unknown')},
            'pain_points': intelligence.get('pain_points', []) or ['Need to scale operations', 'Compliance requirements', 'Digital transformation'],
            'talking_points': intelligence.get('talking_points', []) or ['ROI on automation', 'Compliance features', 'Integration capabilities'],
            'trigger_events': intelligence.get('trigger_events', []) or ['Recent appointment', 'Company expansion', 'Market changes'],
            'deals_database': [],
            'fun_facts': [],
            'data_quality': 'LIMITED',
            'completeness_score': 50,
        }
        
    # Add common fields
    response.update({
        'enrichment_status': contact_dict.get('enrichment_status'),
        'enriched': contact_dict.get('enriched'),
        'priority_score': contact_dict.get('priority_score'),
        'mdcp_score': contact_dict.get('mdcp_score'),
        'rss_score': contact_dict.get('rss_score'),
        'urgency_level': contact_dict.get('urgency_level'),
        'enrichment_date': contact_dict.get('enrichment_date'),
        'last_scored': contact_dict.get('last_scored'),
        'generated_scripts': {},
        'action_items': intelligence.get('action_items', [])
    })
    
    logger.info(f"✅ Returning dashboard data (format: {'NEW' if is_new_format else 'OLD'})")
    
    return jsonify(response)



@app.route('/api/import/contacts', methods=['POST'])
def import_contacts():
    """Import contacts from CSV"""
    # TODO: Implement CSV import
    return jsonify({
        'success': True,
        'count': 0,
        'message': 'CSV import not yet implemented'
    })

@app.route('/api/export/contacts', methods=['GET'])
def export_contacts():
    """Export contacts to CSV"""
    # TODO: Implement CSV export
    return jsonify({
        'success': True,
        'message': 'CSV export not yet implemented'
    })

@app.route('/api/hubspot/import', methods=['POST'])
def hubspot_import():
    """Import contacts from HubSpot"""
    
    # Check if token is configured
    if not HUBSPOT_TOKEN:
        logger.error("❌ HubSpot token not found in environment")
        return jsonify({
            'error': 'HubSpot API key not configured',
            'message': 'Please add HUBSPOT_ACCESS_TOKEN or HUBSPOT_API_KEY to your .env file',
            'imported': 0,
            'existing': 0,
            'total_in_hubspot': 0
        }), 400
    
    # HubSpot API endpoint
    url = 'https://api.hubapi.com/crm/v3/objects/contacts'
    
    # Set up authentication headers (Bearer token for Private Apps)
    headers = {
        'Authorization': f'Bearer {HUBSPOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    # Request parameters
    params = {
        'limit': 100,
        'properties': [
            'firstname',
            'lastname',
            'email',
            'phone',
            'company',
            'jobtitle',
            'industry',
            'linkedin_url',
            'hs_object_id',
            'hs_analytics_source',
            'hs_lead_status',
            'lifecyclestage',
            'numemployees',
            'annualrevenue',
            'city',
            'state',
            'website'
        ]
    }
    
    try:
        logger.info("📡 Requesting contacts from HubSpot...")
        
        # Fetch from HubSpot
        response = requests.get(url, headers=headers, params=params)
        
        # Check for authentication error
        if response.status_code == 401:
            logger.error("❌ HubSpot authentication failed - 401 Unauthorized")
            return jsonify({
                'error': 'HubSpot authentication failed',
                'message': 'Your HubSpot token is invalid or expired. Please update HUBSPOT_ACCESS_TOKEN in your .env file',
                'imported': 0,
                'existing': 0,
                'total_in_hubspot': 0
            }), 401
        
        # Check for other errors
        if response.status_code != 200:
            logger.error(f"❌ HubSpot API error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return jsonify({
                'error': f'HubSpot API error: {response.status_code}',
                'message': response.text,
                'imported': 0,
                'existing': 0,
                'total_in_hubspot': 0
            }), response.status_code
        
        hubspot_data = response.json()
        contacts = hubspot_data.get('results', [])
        
        logger.info(f"✅ Retrieved {len(contacts)} contacts from HubSpot")
        
        # Import to database
        conn = get_db()
        cursor = conn.cursor()
        imported = 0
        skipped = 0
        
        for contact in contacts:
            props = contact.get('properties', {})
            hubspot_id = contact.get('id')
            
            # Build name
            first = props.get('firstname', '').strip()
            last = props.get('lastname', '').strip()
            name = f"{first} {last}".strip()
            
            if not name:
                email = props.get('email', '')
                name = email.split('@')[0] if email else f"HubSpot_{hubspot_id}"
            
            # Check if contact already exists (by email or hubspot_id)
            cursor.execute(
                "SELECT id FROM contacts WHERE email = ? OR hubspot_id = ?", 
                (props.get('email'), hubspot_id)
            )
            
            if cursor.fetchone():
                skipped += 1
                logger.info(f"⏭️  Skipped (exists): {name}")
                continue
            
            # Insert new contact
            cursor.execute('''
                INSERT INTO contacts (
                    name, email, phone, company, title, 
                    hubspot_id, linkedin_url, enrichment_status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            ''', (
                name,
                props.get('email'),
                props.get('phone'),
                props.get('company'),
                props.get('jobtitle'),
                hubspot_id,
                props.get('linkedin_url')
            ))
            imported += 1
            logger.info(f"✅ Imported: {name} ({props.get('company', 'No company')})")
        
        conn.commit()
        conn.close()
        
        logger.info(f"🎉 Import complete: {imported} new, {skipped} skipped")
        
        return jsonify({
            'success': True,
            'imported': imported,
            'existing': skipped,
            'total_in_hubspot': len(contacts),
            'message': f'Successfully imported {imported} new contacts from HubSpot'
        })
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error importing from HubSpot: {e}")
        return jsonify({
            'error': 'Import failed',
            'message': str(e),
            'imported': 0,
            'existing': 0,
            'total_in_hubspot': 0
        }), 500
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return jsonify({
            'error': 'Unexpected error',
            'message': str(e),
            'imported': 0,
            'existing': 0,
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
    
    # Initialize database (with automatic migrations!)
    init_db()
    
    # Run server
    app.run(debug=True, host='0.0.0.0', port=PORT)
    