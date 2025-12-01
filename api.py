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
import openai
from openai import OpenAI
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


# ═══════════════════════════════════════════════════════════════════════════
# INLINE PROFILE BUILDER ENRICHMENT ENGINE (3-Stage Intelligence)

# ═══════════════════════════════════════════════════════════════════════════
# INLINE PROFILE BUILDER ENRICHMENT ENGINE (3-Stage Intelligence)
# ═══════════════════════════════════════════════════════════════════════════
class EnhancedEnrichment:
    """
    Profile Builder - Three-stage enrichment pipeline:
      Stage 1: Perplexity sonar-pro comprehensive research
      Stage 2: GPT-4 intelligence interpolation & structuring
      Stage 3: Database persistence (handled by endpoint)
    
    Output matches "Profile Builder" Perplexity Space format
    """
    
    def __init__(self):
        self.perplexity_key = PERPLEXITY_API_KEY
        self.openai_key = OPENAI_API_KEY
        
        if not self.perplexity_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set")
        
        # NEW: OpenAI v1.0+ - No global api_key setting needed
        self.output_dir = 'enrichment_profiles'
        
        try:
            import os
            os.makedirs(self.output_dir, exist_ok=True)
        except:
            pass  # Directory creation is optional
        
        logger.info("✅ EnhancedEnrichment initialized (Profile Builder 3-stage)")
    
    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment pipeline - returns dict with status and enrichment_data"""
        name = contact.get('name', 'Unknown')
        company = contact.get('company', '')
        contact_id = contact.get('id', 'unknown')
        
        logger.info("=" * 80)
        logger.info(f"PROFILE BUILDER ENRICHMENT: {name} at {company}")
        logger.info("=" * 80)
        
        # STAGE 1: Perplexity Research
        query = self._build_profile_builder_query(contact)
        logger.info("🔍 STAGE 1: PERPLEXITY RESEARCH (sonar-pro)")
        
        raw_profile = self._call_perplexity(query)
        if not raw_profile:
            logger.error("❌ No result from Perplexity")
            return {'status': 'error', 'error': 'Perplexity returned no data'}
        
        logger.info(f"✅ STAGE 1 COMPLETE: {len(raw_profile)} characters")
        
        # STAGE 2: GPT-4 Intelligence Layer
        logger.info("✨ STAGE 2: GPT-4 INTELLIGENCE INTERPOLATION...")
        
        polished_profile = self._gpt4_intelligence_layer(raw_profile, contact)
        if not polished_profile:
            logger.warning("⚠️  Stage 2 failed, using raw profile")
            polished_profile = raw_profile
        else:
            logger.info(f"✅ STAGE 2 COMPLETE: {len(polished_profile)} characters")
        
        # Save debug files
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/profile_{contact_id}_{timestamp}_polished.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Profile for {name}\n")
                f.write("=" * 80 + "\n")
                f.write(polished_profile)
            logger.info(f"📄 Saved: {filename}")
        except Exception as e:
            logger.warning(f"Could not save debug file: {e}")
        
        logger.info("=" * 80)
        logger.info("THREE-STAGE ENRICHMENT COMPLETE!")
        logger.info("=" * 80)
        
        return {
            'status': 'success',
            'enrichment_data': polished_profile,
            'overview': polished_profile[:500],
            'character_count': len(polished_profile)
        }
    
    def _build_profile_builder_query(self, contact: dict) -> str:
        """Build comprehensive query based on Profile Builder instructions"""
        name = contact.get('name', '')
        title = contact.get('title', '')
        company = contact.get('company', '')
        linkedin_url = contact.get('linkedin_url', '')
        
        context = f"{name}, {title} at {company}"
        if linkedin_url:
            context += f"\nLinkedIn: {linkedin_url} (use as PRIMARY source)"
        
        query = f"""{context}

You are a professional profile-building assistant. Generate a comprehensive profile using LinkedIn and public sources.

**FOR THE PERSON ({name}):**
1. Overview – Current role, organization summary
2. Background – Career trajectory with years and companies
3. Education – Degrees, institutions, years, honors
4. Recent Mentions – News, LinkedIn posts, appearances
5. Social Media – LinkedIn, Twitter, Facebook, Instagram handles
6. Personality Detail – Myers-Briggs assessment (infer from behavior)
7. Myers-Briggs Summary – How it relates to work style

**FOR THE COMPANY ({company}):**
8. Company Overview – Mission, founding, HQ
8.1. Products & Services
8.2. Leadership
8.3. Market & Competitors
8.4. Recent News
8.5. Fun Facts

**STRATEGIC INTELLIGENCE:**
9. Pain Points – 5 specific challenges for {title} role
10. Business Needs – 5 ways sales tools/financing could help
11. Key Insights – 3 non-obvious insights for conversations
12. Final Note – Strategic summary for outreach

Be thorough, cite sources, include dates and context.
"""
        return query.strip()
    
    def _gpt4_intelligence_layer(self, raw_profile: str, contact: dict) -> str:
        """Stage 2: GPT-4 adds intelligence and structures output"""
        name = contact.get('name', '')
        title = contact.get('title', '')
        company = contact.get('company', '')
        
        prompt = f"""You are an expert sales intelligence analyst.

Transform this research into a structured profile with added intelligence.

**CONTACT:** {name}, {title} at {company}

**RAW RESEARCH:**
{raw_profile}

**OUTPUT FORMAT (EXACT STRUCTURE):**

## 1. Overview
[2-3 sentence executive summary]

## 2. Professional Background
[Career trajectory with companies, roles, years, achievements]

## 3. Education & Credentials
[Degrees, institutions, years, honors - e.g., UC Berkeley BA Economics 1976-1980]

## 4. Recent Mentions
[News, LinkedIn activity, speaking - with dates]

## 5. Social Media Profiles
- **LinkedIn:** [URL or "Not found"]
- **Twitter/X:** [Handle or "Not publicly available"]
- **Facebook:** ["Not publicly available"]
- **Instagram:** ["Not publicly available"]

## 6. Personality Detail
[Myers-Briggs assessment inferred from leadership style, communication, career choices]

## 7. Myers-Briggs Personality Assessment Summary
[How personality manifests in work: decision-making, leadership, communication, engagement approach]

## 8. Company Overview – {company}
[Mission, founding, HQ, size]

### 8.1. Products & Services
[Offerings, markets, value proposition]

### 8.2. Leadership
[Key executives, founders]

### 8.3. Market & Competitors
[Industry position, competitors]

### 8.4. Recent News
[Announcements, deals, launches - with dates]

### 8.5. Company Fun Facts
[Culture, volunteer work, awards, unique details]

## 9. Pain Points & Challenges
[5 specific pain points for {title}:]
- [Pain 1]
- [Pain 2]
- [Pain 3]
- [Pain 4]
- [Pain 5]

## 10. Sales Opportunities & Talking Points
[5 actionable talking points:]
- [Point 1]
- [Point 2]
- [Point 3]
- [Point 4]
- [Point 5]

## 11. Key Insights (Deep Intelligence)
[3 non-obvious insights:]
- [Insight 1]
- [Insight 2]
- [Insight 3]

## 12. Final Note – Strategic Summary
[One paragraph: who they are, what they care about, how to engage, why now]

**INSTRUCTIONS:**
- Use EXACT structure above
- Add intelligence beyond raw data
- Include dates, numbers, specifics
- If data missing, say "Not publicly available"
- Be professional and actionable
"""
        
        try:
            # NEW: OpenAI v1.0+ syntax
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': 'You are a professional business intelligence analyst specializing in sales enablement.'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.4,
                max_tokens=4000
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"❌ GPT-4 error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _call_perplexity(self, query: str) -> str:
        """Call Perplexity API with sonar-pro"""
        url = 'https://api.perplexity.ai/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.perplexity_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'sonar-pro',
            'messages': [{'role': 'user', 'content': query}],
            'temperature': 0.2,
            'max_tokens': 4000
        }
        
        try:
            import requests
            logger.info("🌐 Calling Perplexity API...")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Perplexity API successful!")
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"❌ Perplexity API Error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
            
        except Exception as e:
            logger.error(f"❌ Perplexity request error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZE ENRICHMENT ENGINE
# ═══════════════════════════════════════════════════════════════════════════
try:
    enrichment_engine = EnhancedEnrichment
    logger.info("✅ EnhancedEnrichment class loaded (Profile Builder)")
except Exception as e:
    logger.error(f"❌ Failed to load EnhancedEnrichment: {e}")
    enrichment_engine = None
  
# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZE SCORING ENGINE
# ═══════════════════════════════════════════════════════════════════════════

try:
    from apps.backend.intelligence.engines.scoring import ApexScoringEngine
    scoring_engine = ApexScoringEngine()
    logger.info("✅ ApexScoringEngine loaded")
except Exception as e:
    logger.warning(f"⚠️ Scoring engine not available: {e}")
    scoring_engine = None
  
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

  ## ================================================================
  # API ENDPOINTS - ENRICHMENT (STAGE 2 + SCORING STAGE 3)
  # ================================================================
@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
  """
  3-Stage Enrichment Pipeline:
  STAGE 1: Perplexity raw research
  STAGE 2: GPT-4 structuring + intelligence layers
  STAGE 3: Database save + MDCP scoring
  """
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
    
    # ===== STAGE 1: Run enrichment engine =====
    logger.info(f"🔍 STAGE 1: Enriching contact {contact_id}: {contact.get('name')}")
    enricher = enrichment_engine()
    result = enricher.enrich_contact(contact)
    
    # Check for 'status' instead of 'success'
    if result and result.get('status') == 'success':
      # Get raw Perplexity output
      raw_profile = result.get('enrichment_data', result.get('overview', ''))
      
      if isinstance(raw_profile, dict):
        raw_profile = str(raw_profile)
        
        # ===== STAGE 2: Polish with GPT-4 =====
      logger.info(f"✨ STAGE 2: GPT-4 polishing {len(raw_profile)} chars...")
      profile_text = raw_profile  # fallback if GPT-4 fails
      
      try:
        polish_response = openai.ChatCompletion.create(
          model='gpt-4',
          messages=[{
            'role': 'user',
            'content': f"""
Transform this sales research into a structured dossier with clear sections.

CONTACT: {contact.get('name')}

RAW RESEARCH:
{raw_profile}

Add these sections at the end:

## 9. Pain Points & Challenges
[3-5 bullet points of likely frustrations in their role]

## 10. Product Fit Analysis
[How sales intelligence/CRM tools align with their needs]

## 11. Outreach Strategy
[Best channels, timing, messaging angles]

## 12. Key Talking Points
[3-5 specific conversation starters based on their background]

Include all the original research, then add these structured sections.
            """.strip()
          }],
          temperature=0.3,
          max_tokens=3500
        )
        profile_text = polish_response.choices[0].message.content
        logger.info(f"✅ STAGE 2 COMPLETE: {len(profile_text)} chars")
      except Exception as e:
        logger.warning(f"⚠️  Stage 2 GPT-4 polish failed, using raw profile: {e}")
        # profile_text already set to raw_profile above
        
        # ===== STAGE 3A: Save to database =====
      conn = get_db()
      cursor = dict_cursor(conn) if IS_PRODUCTION else conn.cursor()
      
      if IS_PRODUCTION:
        cursor.execute("""
          UPDATE contacts SET
          profile_content = %s,
          enrichment_status = 'completed',
          enrichment_date = %s,
          updated_at = %s
          WHERE id = %s
        """, (profile_text, datetime.now(), datetime.now(), contact_id))
      else:
        cursor.execute("""
          UPDATE contacts SET
          profile_content = ?,
          enrichment_status = 'completed',
          enrichment_date = ?,
          updated_at = ?
          WHERE id = ?
        """, (profile_text, datetime.now().isoformat(), datetime.now().isoformat(), contact_id))
        
      conn.commit()
      logger.info(f"💾 STAGE 3A: Profile saved to database")
      
      # ===== STAGE 3B: Calculate MDCP Scoring =====
      scores = None
      if scoring_engine:
        logger.info(f"🎯 STAGE 3B: Running MDCP scoring...")
        
        # Re-fetch contact with enriched profile
        param_style = '%s' if IS_PRODUCTION else '?'
        cursor.execute(f"SELECT * FROM contacts WHERE id = {param_style}", (contact_id,))
        
        if IS_PRODUCTION:
          enriched_contact = cursor.fetchone()
        else:
          row = cursor.fetchone()
          enriched_contact = dict(row) if row else None
          
        if enriched_contact:
          try:
            scores = scoring_engine.score_contact(enriched_contact)
            
            if scores:
              if IS_PRODUCTION:
                cursor.execute("""
                  UPDATE contacts SET
                  mdcp_score = %s,
                  priority_score = %s,
                  rss_score = %s,
                  mdcp_tier = %s,
                  urgency_level = %s,
                  last_scored = %s,
                  updated_at = %s
                  WHERE id = %s
                """, (
                    scores.get('mdcp_score'),
                    scores.get('priority_score'),
                    scores.get('rss_score'),
                    scores.get('mdcp_tier'),
                    scores.get('urgency_level'),
                    datetime.now(),
                    datetime.now(),
                    contact_id
                  ))
              else:
                cursor.execute("""
                  UPDATE contacts SET
                  mdcp_score = ?,
                  priority_score = ?,
                  rss_score = ?,
                  mdcp_tier = ?,
                  urgency_level = ?,
                  last_scored = ?,
                  updated_at = ?
                  WHERE id = ?
                """, (
                    scores.get('mdcp_score'),
                    scores.get('priority_score'),
                    scores.get('rss_score'),
                    scores.get('mdcp_tier'),
                    scores.get('urgency_level'),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    contact_id
                  ))
                
              conn.commit()
              logger.info(f"✅ STAGE 3B COMPLETE: MDCP={scores.get('mdcp_score'):.1f}, Priority={scores.get('priority_score'):.1f}")
              
          except Exception as score_error:
            logger.warning(f"⚠️  Scoring failed (enrichment still saved): {score_error}")
            # Don't fail the whole enrichment if scoring errors
            
      conn.close()
      
      logger.info(f"✅ ✅ ✅ ENRICHMENT COMPLETE for contact {contact_id}")
      
      return jsonify({
    'success': True,
    'contact_id': contact_id,
    'profile_length': len(profile_text),
    'enrichment_status': 'completed',
    'scoring': {
      'mdcp_score': scores.get('mdcp_score') if scores else None,
      'priority_score': scores.get('priority_score') if scores else None,
      'tier': scores.get('mdcp_tier') if scores else None
    } if scores else None
    }), 200
    
    else:
      error_msg = result.get('error', 'Enrichment failed') if result else 'No result returned'
      logger.error(f"❌ Enrichment failed: {error_msg}")
      return jsonify({'success': False, 'error': error_msg}), 500
    
  except Exception as e:
    logger.error(f"❌ Enrichment error: {e}")
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
# ================================================================
# HUBSPOT IMPORT ENDPOINT (WITH PAGINATION + FILTERS)
# ================================================================
@app.route("/api/hubspot/import", methods=["POST", "OPTIONS"])
def hubspot_import():
    """Import qualified contacts from HubSpot CRM with pagination"""
    import requests as req
    
    if request.method == "OPTIONS":
        return "", 204
    
    HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
    if not HUBSPOT_API_KEY:
        return jsonify({"success": False, "error": "HUBSPOT_API_KEY not configured"}), 400
    
    # Lead statuses to EXCLUDE
    EXCLUDED_LEAD_STATUS = {'unqualified', 'do not contact', 'unsubscribed', 'bad timing', 'dq'}
    EXCLUDED_LIFECYCLE = {'unqualified'}
    
    try:
        headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
        all_contacts = []
        after = None
        page = 0
        
        while True:
            page += 1
            params = {
                "limit": 100, 
                "properties": "firstname,lastname,email,phone,mobilephone,company,jobtitle,hs_linkedinbio,linkedin,hs_lead_status,lifecyclestage"
            }
            if after:
                params["after"] = after
            
            print(f"📥 Fetching HubSpot page {page}...")
            response = req.get("https://api.hubapi.com/crm/v3/objects/contacts", headers=headers, params=params)
            
            if response.status_code != 200:
                return jsonify({"success": False, "error": f"HubSpot API error: {response.status_code}"}), 400
            
            data = response.json()
            results = data.get("results", [])
            all_contacts.extend(results)
            
            paging = data.get("paging", {})
            next_page = paging.get("next", {})
            after = next_page.get("after")
            
            if not after:
                break
        
        print(f"📊 Total HubSpot contacts fetched: {len(all_contacts)}")
        
        imported, updated, skipped, filtered = 0, 0, 0, 0
        conn = get_db()
        cursor = conn.cursor()
        
        for hs_contact in all_contacts:
            props = hs_contact.get("properties", {})
            
            # FILTER: Must have email
            email = (props.get("email") or "").strip().lower()
            if not email:
                skipped += 1
                continue
            
            # FILTER: Must have company
            company = (props.get("company") or "").strip()
            if not company:
                filtered += 1
                continue
            
            # FILTER: Exclude bad lead statuses
            lead_status = (props.get("hs_lead_status") or "").strip().lower()
            if lead_status in EXCLUDED_LEAD_STATUS:
                filtered += 1
                continue
            
            # FILTER: Exclude unqualified lifecycle
            lifecycle = (props.get("lifecyclestage") or "").strip().lower()
            if lifecycle in EXCLUDED_LIFECYCLE:
                filtered += 1
                continue
            
            first = props.get("firstname") or ""
            last = props.get("lastname") or ""
            name = f"{first} {last}".strip() or email.split("@")[0]
            
            cursor.execute("SELECT id FROM contacts WHERE email = ?", (email,))
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute(
                    "UPDATE contacts SET name=?, title=?, company=?, phone=?, phone_mobile=?, linkedin_url=?, hubspot_id=?, updated_at=CURRENT_TIMESTAMP WHERE email=?",
                    (name, props.get("jobtitle") or "", company, props.get("phone") or "", props.get("mobilephone") or "", props.get("hs_linkedinbio") or props.get("linkedin") or "", hs_contact.get("id"), email)
                )
                updated += 1
            else:
                cursor.execute(
                    "INSERT INTO contacts (name, email, title, company, phone, phone_mobile, linkedin_url, hubspot_id, created_at) VALUES (?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)",
                    (name, email, props.get("jobtitle") or "", company, props.get("phone") or "", props.get("mobilephone") or "", props.get("hs_linkedinbio") or props.get("linkedin") or "", hs_contact.get("id"))
                )
                imported += 1
        
        conn.commit()
        conn.close()
        
        print(f"✅ Import complete: {imported} new, {updated} updated, {skipped} no email, {filtered} filtered out")
        return jsonify({
            "success": True, 
            "imported": imported, 
            "updated": updated, 
            "skipped": skipped,
            "filtered": filtered,
            "total": len(all_contacts)
        })
    
    except Exception as e:
        print(f"❌ HubSpot import error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
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
  
