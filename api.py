#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
APEX SALES INTELLIGENCE API SERVER
Smart Dual-Environment Configuration
- LOCAL: SQLite (fast development)
- PRODUCTION: PostgreSQL on Railway
Date: November 29, 2025
═══════════════════════════════════════════════════════════════════
"""

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import requests

# ================================================================
# ENVIRONMENT SETUP
# ================================================================
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# ================================================================
# SMART ENVIRONMENT DETECTION
# ================================================================
IS_PRODUCTION = os.getenv('DATABASE_URL') is not None  # Railway sets this
ENVIRONMENT = "PRODUCTION" if IS_PRODUCTION else "LOCAL"

logger.info(f"🌍 Environment: {ENVIRONMENT}")

# ================================================================
# PATH CONFIGURATION
# ================================================================
# Point to apps/backend where intelligence modules live
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
# IMPORT ENGINES (with graceful degradation)
# ================================================================
enrichment_engine = None
scoring_engine = None
auto_sequence_engine = None
cadence_router = None

# Enrichment Engine
try:
    from intelligence.engines.enrichment.perplexity_enrichment import PerplexityEnrichment
    enrichment_engine = PerplexityEnrichment
    logger.info("✅ Enrichment engine loaded")
except ImportError as e:
    logger.warning(f"⚠️  Enrichment engine unavailable: {e}")
except Exception as e:
    logger.error(f"❌ Enrichment engine initialization failed: {e}")

# Scoring Engine
try:
    from intelligence.engines.scoring.apex_scoring_engine import ApexScoringEngine
    scoring_engine = ApexScoringEngine
    logger.info("✅ Scoring engine loaded")
except ImportError as e:
    logger.warning(f"⚠️  Scoring engine unavailable: {e}")
except Exception as e:
    logger.error(f"❌ Scoring engine initialization failed: {e}")

# Outreach Engines
try:
    from intelligence.engines.outreach.auto_sequence_engine import AutoSequenceEngine
    from intelligence.engines.scoring.cadence_router import CadenceRouter
    auto_sequence_engine = AutoSequenceEngine
    cadence_router = CadenceRouter
    logger.info("✅ Cadence engines loaded")
except ImportError as e:
    logger.warning(f"⚠️  Cadence engines unavailable: {e}")
except Exception as e:
    logger.error(f"❌ Cadence engines initialization failed: {e}")

# ================================================================
# FLASK APP INITIALIZATION
# ================================================================
app = Flask(__name__)
CORS(app)

# ================================================================
# SMART DATABASE CONFIGURATION
# ================================================================
PORT = int(os.getenv('PORT', 8000))

if IS_PRODUCTION:
    # PRODUCTION: PostgreSQL on Railway
    DATABASE_URL = os.getenv('DATABASE_URL')
    logger.info(f"📊 Database: PostgreSQL (Railway)")

    # Import PostgreSQL adapter
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        def get_db():
            """Get PostgreSQL database connection"""
            conn = psycopg2.connect(DATABASE_URL)
            return conn

        def dict_cursor(conn):
            """Get dictionary cursor for PostgreSQL"""
            return conn.cursor(cursor_factory=RealDictCursor)

        logger.info("✅ PostgreSQL adapter loaded")
    except ImportError:
        logger.error("❌ psycopg2 not installed - install with: pip install psycopg2-binary")
        raise
else:
    # LOCAL: SQLite for development
    import sqlite3

    DATABASE = '/Users/chrisrabenold/projects/apex/apex.db'
    logger.info(f"📊 Database: SQLite ({DATABASE})")

    def get_db():
        """Get SQLite database connection"""
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn

    def dict_cursor(conn):
        """Get cursor for SQLite (returns Row objects that act like dicts)"""
        return conn.cursor()

logger.info(f"🚀 Server Port: {PORT}")

# ================================================================
# DATABASE SCHEMA MANAGEMENT
# ================================================================
def ensure_schema():
    """Ensure all required tables and columns exist"""
    conn = get_db()

    if IS_PRODUCTION:
        cursor = dict_cursor(conn)
    else:
        cursor = conn.cursor()

    # All enrichment and Phase 2 columns
    columns_to_add = [
        # Scoring
        ('mdcp_score', 'REAL' if not IS_PRODUCTION else 'DECIMAL'),
        ('mdcp_tier', 'TEXT' if not IS_PRODUCTION else 'VARCHAR(50)'),
        ('rss_score', 'REAL' if not IS_PRODUCTION else 'DECIMAL'),
        ('rss_tier', 'TEXT' if not IS_PRODUCTION else 'VARCHAR(50)'),
        ('priority_score', 'REAL' if not IS_PRODUCTION else 'DECIMAL'),
        ('urgency_level', 'TEXT' if not IS_PRODUCTION else 'VARCHAR(50)'),
        ('recommended_action', 'TEXT'),
        ('calculation_version', 'TEXT' if not IS_PRODUCTION else 'VARCHAR(50)'),
        ('last_scored', 'TEXT' if not IS_PRODUCTION else 'TIMESTAMP'),
        ('lead_type', 'TEXT' if not IS_PRODUCTION else 'VARCHAR(50)'),
        # Enrichment
        ('profile_content', 'TEXT'),
        ('enrichment_status', 'TEXT' if not IS_PRODUCTION else 'VARCHAR(50)'),
        ('enrichment_date', 'TEXT' if not IS_PRODUCTION else 'TIMESTAMP'),
        ('pain_points', 'TEXT'),
        ('talking_points', 'TEXT'),
        ('product_match', 'TEXT'),
        ('match_reasoning', 'TEXT'),
        # Content generation
        ('email_1_subject', 'TEXT'),
        ('email_1_body', 'TEXT'),
        ('email_2_subject', 'TEXT'),
        ('email_2_body', 'TEXT'),
        ('email_3_subject', 'TEXT'),
        ('email_3_body', 'TEXT'),
        ('call_script_1', 'TEXT'),
        ('call_script_2', 'TEXT'),
        ('call_script_3', 'TEXT'),
        ('linkedin_connect', 'TEXT'),
        ('linkedin_followup', 'TEXT'),
        ('linkedin_inmail', 'TEXT'),
        ('linkedin_warmup', 'TEXT'),
        ('content_generated_at', 'TEXT' if not IS_PRODUCTION else 'TIMESTAMP'),
        # Phase 2
        ('last_contact_date', 'TEXT' if not IS_PRODUCTION else 'DATE'),
        ('linkedin_activity_detected', 'INTEGER' if not IS_PRODUCTION else 'BOOLEAN DEFAULT FALSE'),
        ('company_news_detected', 'INTEGER' if not IS_PRODUCTION else 'BOOLEAN DEFAULT FALSE'),
        ('last_signal_date', 'TEXT' if not IS_PRODUCTION else 'TIMESTAMP'),
        ('signal_count', 'INTEGER DEFAULT 0'),
    ]

    for col_name, col_type in columns_to_add:
        try:
            if IS_PRODUCTION:
                cursor.execute(f'ALTER TABLE contacts ADD COLUMN {col_name} {col_type}')
            else:
                cursor.execute(f'ALTER TABLE contacts ADD COLUMN {col_name} {col_type}')
            logger.info(f"  ✅ Added column: {col_name}")
        except Exception:
            pass  # Column already exists

    # Create Phase 2 tables
    if IS_PRODUCTION:
        # PostgreSQL syntax
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts(id)
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts(id)
            )
        """)
    else:
        # SQLite syntax
        cursor.execute("""
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
        """)

        cursor.execute("""
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
        """)

    # Create indexes
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_contact ON contact_activities(contact_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_contact ON opportunity_signals(contact_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_viewed ON opportunity_signals(viewed)")
    except Exception:
        pass

    conn.commit()
    conn.close()
    logger.info("✅ Database schema verified")

# ================================================================
# API ENDPOINTS - HEALTH & SYSTEM
# ================================================================
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'environment': ENVIRONMENT,
        'timestamp': datetime.now().isoformat(),
        'services': {
            'enrichment': enrichment_engine is not None,
            'scoring': scoring_engine is not None,
            'cadence': auto_sequence_engine is not None,
            'database': 'PostgreSQL' if IS_PRODUCTION else 'SQLite'
        }
    })

# ================================================================
# API ENDPOINTS - CONTACTS
# ================================================================
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts with optional filtering"""
    try:
        conn = get_db()
        cursor = dict_cursor(conn) if IS_PRODUCTION else conn.cursor()

        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)

        query = 'SELECT * FROM contacts'
        params = []

        if status:
            query += ' WHERE enrichment_status = %s' if IS_PRODUCTION else ' WHERE enrichment_status = ?'
            params.append(status)

        query += ' ORDER BY created_at DESC LIMIT %s' if IS_PRODUCTION else ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)

        if IS_PRODUCTION:
            contacts = cursor.fetchall()
        else:
            contacts = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return jsonify(contacts)

    except Exception as e:
        logger.error(f"Get contacts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a single contact by ID"""
    try:
        conn = get_db()
        cursor = dict_cursor(conn) if IS_PRODUCTION else conn.cursor()

        param_style = '%s' if IS_PRODUCTION else '?'
        cursor.execute(f'SELECT * FROM contacts WHERE id = {param_style}', (contact_id,))

        if IS_PRODUCTION:
            contact = cursor.fetchone()
        else:
            row = cursor.fetchone()
            contact = dict(row) if row else None

        conn.close()

        if contact:
            return jsonify(contact)
        else:
            return jsonify({'error': 'Contact not found'}), 404

    except Exception as e:
        logger.error(f"Get contact error: {e}")
        return jsonify({'error': str(e)}), 500

# ================================================================
# API ENDPOINTS - ENRICHMENT (STAGE 2)
# ================================================================
@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
  """Enrich a contact using AI enrichment - STAGE 2"""
  try:
    if not enrichment_engine:
      return jsonify({'success': False, 'error': 'Enrichment engine unavailable'}), 503
    
    conn = get_db()
    cursor = dict_cursor(conn) if IS_PRODUCTION else conn.cursor()
    
    param_style = '%s' if IS_PRODUCTION else '?'
    cursor.execute(f"SELECT * FROM contacts WHERE id = {param_style}", (contact_id,))
    
    if IS_PRODUCTION:
      row = cursor.fetchone()
      contact = row if row else None
    else:
      row = cursor.fetchone()
      contact = dict(row) if row else None
      
    if not contact:
      conn.close()
      return jsonify({"success": False, "error": "Contact not found"}), 404
    
    conn.close()
    
    # Run enrichment
    logger.info(f"🔍 Enriching contact {contact_id}: {contact.get('name')}")
    enricher = enrichment_engine()
    result = enricher.enrich_contact(contact)
    
    # FIX: Check for 'status' instead of 'success'
    if result and result.get('status') == 'success':
      # Save profile content to database
      conn = get_db()
      cursor = dict_cursor(conn) if IS_PRODUCTION else conn.cursor()
      
      # FIX: Get profile from 'enrichment_data' or 'overview'
      profile_text = result.get('enrichment_data', result.get('overview', ''))
      
      # If enrichment_data is a dict, convert to string
      if isinstance(profile_text, dict):
        profile_text = str(profile_text)
        
      if IS_PRODUCTION:
        cursor.execute("""
          UPDATE contacts SET
          profile_content = %s,
          enrichment_status = 'completed',
          enrichment_date = %s
          WHERE id = %s
        """, (profile_text, datetime.now(), contact_id))
      else:
        cursor.execute("""
          UPDATE contacts SET
          profile_content = ?,
          enrichment_status = 'completed',
          enrichment_date = ?
          WHERE id = ?
        """, (profile_text, datetime.now().isoformat(), contact_id))
        
      conn.commit()
      conn.close()
      
      logger.info(f"✅ Enrichment complete for contact {contact_id}")
      
      return jsonify({
        'success': True,
        'contact_id': contact_id,
        'profile_length': len(profile_text)
      }), 200
    else:
      error_msg = result.get('error', 'Enrichment failed') if result else 'No result returned'
      logger.error(f"❌ Enrichment failed: {error_msg}")
      return jsonify({'success': False, 'error': error_msg}), 500
    
  except Exception as e:
    logger.error(f"Enrichment error: {e}")
    logger.error(traceback.format_exc())
    return jsonify({'success': False, 'error': str(e)}), 500
  
# ================================================================
# API ENDPOINTS - TODAY'S BOARD (PHASE 2)
# ================================================================
@app.route('/api/todays-board', methods=['GET'])
def get_todays_board():
    """Generate daily prioritized action list"""
    try:
        conn = get_db()
        cursor = dict_cursor(conn) if IS_PRODUCTION else conn.cursor()

        # Date calculation differs between PostgreSQL and SQLite
        if IS_PRODUCTION:
            date_calc = "EXTRACT(DAY FROM (CURRENT_DATE - last_contact_date::date))"
        else:
            date_calc = "CAST(julianday('now') - julianday(last_contact_date) AS INTEGER)"

        # RELATIONSHIPS QUERY
        query = f"""
            SELECT 
                id, name, email, company, title, priority_score,
                enrichment_status, last_contact_date,
                CASE 
                    WHEN last_contact_date IS NULL THEN 0
                    ELSE {date_calc}
                END AS days_since_contact
            FROM contacts
            WHERE enrichment_status = 'completed'
              AND last_contact_date IS NOT NULL
              AND last_contact_date {'!=' if not IS_PRODUCTION else '<>'} ''
            LIMIT 30
        """

        cursor.execute(query)

        if IS_PRODUCTION:
            relationships = cursor.fetchall()
        else:
            relationships = [dict(row) for row in cursor.fetchall()]

        # Process relationships
        for c in relationships:
            days = c.get('days_since_contact', 0)

            if days >= 365:
                c['urgency_tier'] = 'urgent'
                c['urgency_label'] = '🔥 ACT TODAY'
                c['why_now'] = f"Last spoke {days} days ago - going cold"
            elif days >= 180:
                c['urgency_tier'] = 'warm'
                c['urgency_label'] = '⏰ THIS WEEK'
                c['why_now'] = f"Last spoke {days} days ago"
            elif days >= 90:
                c['urgency_tier'] = 'nurture'
                c['urgency_label'] = '🌱 NURTURE'
                c['why_now'] = f"Last spoke {days} days ago"
            else:
                c['urgency_tier'] = 'stable'
                c['urgency_label'] = '✅ STABLE'
                c['why_now'] = "Recent contact"

            c['contact_type'] = 'relationship'

        # PROSPECTS QUERY
        cursor.execute("""
            SELECT 
                id, name, email, company, title, priority_score,
                enrichment_status
            FROM contacts
            WHERE enrichment_status = 'completed'
              AND (last_contact_date IS NULL OR last_contact_date = '')
              AND priority_score >= 60
            LIMIT 15
        """)

        if IS_PRODUCTION:
            prospects = cursor.fetchall()
        else:
            prospects = [dict(row) for row in cursor.fetchall()]

        # Process prospects
        for c in prospects:
            p = c.get('priority_score', 0)

            if p >= 85:
                c['urgency_tier'] = 'hot_prospect'
                c['urgency_label'] = '🔥 HOT'
            elif p >= 75:
                c['urgency_tier'] = 'qualified_prospect'
                c['urgency_label'] = '✅ QUALIFIED'
            else:
                c['urgency_tier'] = 'potential_prospect'
                c['urgency_label'] = '🎯 POTENTIAL'

            c['contact_type'] = 'prospect'

        # Organize by tiers
        urgent = [c for c in relationships if c['urgency_tier'] == 'urgent']
        warm = [c for c in relationships if c['urgency_tier'] == 'warm']

        hot = [c for c in prospects if c['urgency_tier'] == 'hot_prospect']
        qualified = [c for c in prospects if c['urgency_tier'] == 'qualified_prospect']

        conn.close()

        return jsonify({
            "success": True,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%I:%M %p"),
            "environment": ENVIRONMENT,
            "relationships": {
                "total": len(relationships),
                "tiers": {
                    "urgent": urgent[:5],
                    "warm": warm[:5]
                }
            },
            "new_prospects": {
                "total": len(prospects),
                "tiers": {
                    "hot": hot[:5],
                    "qualified": qualified[:5]
                }
            }
        })
    except Exception as e:
        logger.error(f"Today's Board error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

# ================================================================
# MAIN
# ================================================================
if __name__ == '__main__':
    ensure_schema()
    logger.info(f"")
    logger.info(f"═══════════════════════════════════════════════════════")
    logger.info(f"🚀 APEX API SERVER STARTING")
    logger.info(f"═══════════════════════════════════════════════════════")
    logger.info(f"   Environment: {ENVIRONMENT}")
    logger.info(f"   Database: {'PostgreSQL (Railway)' if IS_PRODUCTION else 'SQLite (Local)'}")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Enrichment: {'Available' if enrichment_engine else 'Unavailable'}")
    logger.info(f"   Scoring: {'Available' if scoring_engine else 'Unavailable'}")
    logger.info(f"═══════════════════════════════════════════════════════")
    logger.info(f"")

    app.run(host='0.0.0.0', port=PORT, debug=(not IS_PRODUCTION))
  