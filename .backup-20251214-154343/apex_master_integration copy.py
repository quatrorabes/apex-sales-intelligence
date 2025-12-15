# apex_master_integration.py
# APEX INTELLIGENCE - Complete Production System Integration
# Version: 1.1 FIXED (PostgreSQL + SQLite Compatible) | Date: December 2, 2025

"""
██████╗  █████╗ ██╗     ███████╗███████╗     █████╗ ███╗   ██╗ ██████╗ ███████╗██╗     
██╔══██╗██╔══██╗██║     ██╔════╝██╔════╝    ██╔══██╗████╗  ██║██╔════╝ ██╔════╝██║     
███████║███████║██║     █████╗  ███████╗    ███████║██╔██╗ ██║██║  ███╗█████╗  ██║     
██╔══██║██╔══██║██║     ██╔══╝  ╚════██║    ██╔══██║██║╚██╗██║██║   ██║██╔══╝  ██║     
██║  ██║██║  ██║███████╗███████╗███████║    ██║  ██║██║ ╚████║╚██████╔╝███████╗███████╗
╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝
                                                                                         
           APEX SALES INTELLIGENCE - MASTER INTEGRATION SYSTEM
           Production-Ready Architecture | Full Stack AI Sales Platform
"""

import os
import sys
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from apex_custom_enrichment import ApexCustomEnrichment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("APEX_MASTER")

# ============================================================================
# SECTION 1: CORE CONFIGURATION & ENVIRONMENT
# ============================================================================

class Environment(Enum):
    """Deployment environment types"""
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class ApexConfig:
    """Central configuration for entire APEX system"""
    
    # Environment
    environment: Environment = Environment.LOCAL
    debug_mode: bool = True
    
    # API Configuration
    api_host: str = "localhost"
    api_port: int = 8000
    api_base_url: str = "http://localhost:8000"
    
    # Database Configuration
    db_type: str = "sqlite"
    db_path: str = "./apex.db"
    db_url: Optional[str] = None
    
    # External API Keys
    perplexity_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    hubspot_token: Optional[str] = None
    salesforce_client_id: Optional[str] = None
    salesforce_client_secret: Optional[str] = None
    
    # Intelligence Engine Settings
    enrichment_timeout: int = 60
    scoring_refresh_interval: int = 86400
    persona_confidence_threshold: float = 0.7
    
    # Content Generation Settings
    email_max_length: int = 500
    call_script_max_length: int = 800
    linkedin_message_max_length: int = 300
    
    # Automation Settings
    cadence_max_touches: int = 12
    cadence_days_span: int = 45
    auto_pause_no_response_days: int = 14
    
    # ML Settings
    ml_model_path: str = "./models"
    ml_retrain_threshold: int = 100
    prediction_confidence_threshold: float = 0.6
    
    # Feature Flags
    enable_enrichment: bool = True
    enable_scoring: bool = True
    enable_persona_classification: bool = True
    enable_content_generation: bool = True
    enable_automation: bool = True
    enable_ml_predictions: bool = True
    enable_adaptive_learning: bool = True
    
    @classmethod
    def from_env(cls) -> 'ApexConfig':
        """Load configuration from environment variables"""
        from dotenv import load_dotenv
        load_dotenv()
        
        db_url = os.getenv('DATABASE_URL')
        is_production = db_url is not None and db_url.strip() != ''
        env = Environment.PRODUCTION if is_production else Environment.LOCAL
        
        config = cls(
            environment=env,
            debug_mode=not is_production,
            api_base_url=os.getenv('API_BASE_URL', 'http://localhost:8000'),
            db_url=db_url if is_production else None,
            db_type='postgresql' if is_production else 'sqlite',
            perplexity_api_key=os.getenv('PERPLEXITY_API_KEY'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            hubspot_token=os.getenv('HUBSPOT_ACCESS_TOKEN'),
            salesforce_client_id=os.getenv('SALESFORCE_CLIENT_ID'),
            salesforce_client_secret=os.getenv('SALESFORCE_CLIENT_SECRET'),
        )
        
        logger.info(f"✅ Configuration loaded for {env.value.upper()} environment")
        return config

# ============================================================================
# SECTION 2: DATABASE LAYER (FIXED)
# ============================================================================

class DatabaseManager:
    """Unified database manager supporting SQLite and PostgreSQL"""
    
    def __init__(self, config: ApexConfig):
        self.config = config
        self.conn = None
        self._initialize_connection()
        self._ensure_schema()
    
    def _initialize_connection(self):
        """Initialize database connection with autocommit for PostgreSQL"""
        if self.config.db_type == 'postgresql':
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from psycopg2 import extensions
            
            self.conn = psycopg2.connect(self.config.db_url)
            # CRITICAL: Set autocommit to prevent transaction locks
            self.conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor_factory = RealDictCursor
            logger.info("✅ PostgreSQL connection established (AUTOCOMMIT mode)")
        else:
            import sqlite3
            self.conn = sqlite3.connect(self.config.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.cursor_factory = None
            logger.info(f"✅ SQLite connection established: {self.config.db_path}")
    
    def get_cursor(self):
        """Get database cursor"""
        if self.cursor_factory:
            return self.conn.cursor(cursor_factory=self.cursor_factory)
        return self.conn.cursor()
    
    def rollback(self):
        """Rollback current transaction (SQLite only, PostgreSQL is autocommit)"""
        if self.config.db_type == 'sqlite' and self.conn:
            self.conn.rollback()
            logger.warning("⚠️ Transaction rolled back")
    
    def _ensure_schema(self):
        """Create all required tables with DB-specific syntax"""
        cursor = self.get_cursor()
        
        # Determine correct syntax based on database type
        if self.config.db_type == 'postgresql':
            id_column = "id SERIAL PRIMARY KEY"
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
        else:
            id_column = "id INTEGER PRIMARY KEY AUTOINCREMENT"
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS contacts (
                {id_column},
                first_name TEXT, last_name TEXT, name TEXT UNIQUE, email TEXT UNIQUE,
                phone TEXT, phone_mobile TEXT, company TEXT, title TEXT,
                linkedin_url TEXT, company_domain TEXT, company_website TEXT,
                company_hq_city TEXT, company_hq_state TEXT, industry TEXT,
                profile_content TEXT, enrichment_status TEXT DEFAULT 'pending',
                enrichment_date TEXT, persona_type TEXT, persona_confidence REAL,
                priority_score REAL, mdcp_score REAL, mdcp_tier TEXT,
                rss_score REAL, rss_tier TEXT, urgency_level TEXT, last_scored TEXT,
                conversion_probability REAL,
                email_1_subject TEXT, email_1_body TEXT, email_2_subject TEXT, email_2_body TEXT,
                call_script_1 TEXT, call_script_2 TEXT, linkedin_connect TEXT,
                linkedin_followup TEXT, value_proposition TEXT, pain_points_matched TEXT,
                import_source TEXT, crm_id TEXT, data_completeness_score INTEGER DEFAULT 0,
                enrichment_ready INTEGER DEFAULT 0, last_crm_sync TEXT,
                last_contact_date TEXT, total_touches INTEGER DEFAULT 0,
                response_count INTEGER DEFAULT 0,
                cadence_status TEXT DEFAULT 'not_started', cadence_stage INTEGER DEFAULT 0,
                next_touch_date TEXT, auto_pause INTEGER DEFAULT 0,
                created_at TIMESTAMP {default_timestamp},
                updated_at TIMESTAMP {default_timestamp}
            )
        """)
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS contact_activities (
                {id_column},
                contact_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_date TEXT NOT NULL,
                direction TEXT, channel TEXT, subject TEXT, notes TEXT,
                outcome TEXT, sentiment_score REAL,
                created_at TIMESTAMP {default_timestamp},
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS opportunity_signals (
                {id_column},
                contact_id INTEGER NOT NULL,
                signal_type TEXT NOT NULL,
                signal_date TEXT NOT NULL,
                signal_data TEXT,
                urgency_boost INTEGER DEFAULT 0,
                viewed INTEGER DEFAULT 0,
                created_at TIMESTAMP {default_timestamp},
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            )
        """)
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)",
            "CREATE INDEX IF NOT EXISTS idx_contacts_linkedin ON contacts(linkedin_url)",
            "CREATE INDEX IF NOT EXISTS idx_contacts_enrichment ON contacts(enrichment_status)",
            "CREATE INDEX IF NOT EXISTS idx_contacts_priority ON contacts(priority_score)",
            "CREATE INDEX IF NOT EXISTS idx_activities_contact ON contact_activities(contact_id)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        if self.config.db_type == 'sqlite':
            self.conn.commit()
        
        logger.info("✅ Database schema initialized with all tables and indexes")
    
    def get_contact(self, contact_id: int) -> Optional[Dict]:
        """Retrieve single contact by ID"""
        try:
            cursor = self.get_cursor()
            placeholder = "%s" if self.config.db_type == 'postgresql' else "?"
            cursor.execute(f"SELECT * FROM contacts WHERE id = {placeholder}", (contact_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching contact {contact_id}: {e}")
            return None
    
    def get_contacts(self, limit: int = 100, status: str = None) -> List[Dict]:
        """Retrieve multiple contacts"""
        try:
            cursor = self.get_cursor()
            placeholder = "%s" if self.config.db_type == 'postgresql' else "?"
            
            if status:
                cursor.execute(f"SELECT * FROM contacts WHERE enrichment_status = {placeholder} LIMIT {placeholder}", (status, limit))
            else:
                cursor.execute(f"SELECT * FROM contacts LIMIT {placeholder}", (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching contacts: {e}")
            return []
    
    def upsert_contact(self, contact_data: Dict) -> int:
        """Insert or update contact (FIXED VERSION)"""
        cursor = self.get_cursor()
        email = contact_data.get('email')
        contact_id = contact_data.get('id')
        placeholder = "%s" if self.config.db_type == 'postgresql' else "?"
        
        try:
            existing_id = None
            
            # Check if ID is provided and exists
            if contact_id:
                cursor.execute(f"SELECT id FROM contacts WHERE id = {placeholder}", (contact_id,))
                result = cursor.fetchone()
                if result:
                    existing_id = result[0] if isinstance(result, tuple) else result['id']
            
            # Otherwise check by email
            if not existing_id and email:
                cursor.execute(f"SELECT id FROM contacts WHERE email = {placeholder}", (email,))
                result = cursor.fetchone()
                if result:
                    existing_id = result[0] if isinstance(result, tuple) else result['id']
            
            if existing_id:
                # UPDATE existing contact (remove 'id' from update data)
                update_data = {k: v for k, v in contact_data.items() if k != 'id'}
                
                if not update_data:
                    return existing_id
                
                set_clause = ', '.join([f"{k} = {placeholder}" for k in update_data.keys()])
                values = list(update_data.values())
                values.append(existing_id)
                
                cursor.execute(
                    f"UPDATE contacts SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = {placeholder}",
                    values
                )
                
                if self.config.db_type == 'sqlite':
                    self.conn.commit()
                
                logger.debug(f"✅ Updated contact ID {existing_id}")
                return existing_id
            else:
                # INSERT new contact (remove 'id' if None)
                insert_data = {k: v for k, v in contact_data.items() if k != 'id' or v is not None}
                
                columns = ', '.join(insert_data.keys())
                placeholders_str = ', '.join([placeholder for _ in insert_data])
                values = list(insert_data.values())
                
                if self.config.db_type == 'postgresql':
                    cursor.execute(
                        f"INSERT INTO contacts ({columns}) VALUES ({placeholders_str}) RETURNING id",
                        values
                    )
                    new_id = cursor.fetchone()[0]
                else:
                    cursor.execute(
                        f"INSERT INTO contacts ({columns}) VALUES ({placeholders_str})",
                        values
                    )
                    new_id = cursor.lastrowid
                    self.conn.commit()
                
                logger.debug(f"✅ Inserted new contact ID {new_id}")
                return new_id
                
        except Exception as e:
            logger.error(f"❌ Error in upsert_contact: {e}")
            if self.config.db_type == 'sqlite':
                self.rollback()
            raise
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# ============================================================================
# SECTION 3: INTELLIGENCE ORCHESTRATOR (WITH ERROR HANDLING)
# ============================================================================

class IntelligenceOrchestrator:
    """Master orchestrator for all AI operations"""
    
    def __init__(self, config: ApexConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.enrichment_engine = None
        self.scoring_engine = None
        self.persona_classifier = None
        self.content_generator = None
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Load all intelligence engines"""
        logger.info("🚀 Initializing Intelligence Engines...")
        
        if self.config.enable_enrichment:
            self.enrichment_engine = EnrichmentEngine(self.config)
            logger.info("  ✓ Enrichment Engine loaded")
        
        if self.config.enable_scoring:
            self.scoring_engine = ScoringEngine(self.config)
            logger.info("  ✓ Scoring Engine loaded")
        
        if self.config.enable_persona_classification:
            self.persona_classifier = PersonaClassifier(self.config)
            logger.info("  ✓ Persona Classifier loaded")
        
        if self.config.enable_content_generation:
            self.content_generator = ContentGenerator(self.config)
            logger.info("  ✓ Content Generator loaded")
    
    def process_contact_full_pipeline(self, contact_id: int) -> Dict:
        """Execute complete intelligence pipeline with error recovery"""
        logger.info(f"{'='*80}")
        logger.info(f"🎯 FULL INTELLIGENCE PIPELINE - Contact ID: {contact_id}")
        logger.info(f"{'='*80}")
        
        results = {'contact_id': contact_id, 'timestamp': datetime.now().isoformat(), 'stages': {}}
        contact = self.db.get_contact(contact_id)
        
        if not contact:
            return {'error': 'Contact not found', 'contact_id': contact_id}
        
        try:
            # STAGE 1: Enrichment
            if self.config.enable_enrichment and contact.get('enrichment_status') != 'completed':
                logger.info("📊 STAGE 1: Profile Enrichment")
                enrichment_result = self.enrichment_engine.enrich_contact(contact)
                
                if enrichment_result.get('status') == 'success':
                    self.db.upsert_contact({
                        'id': contact_id,
                        'profile_content': enrichment_result.get('enrichment_data'),
                        'enrichment_status': 'completed',
                        'enrichment_date': datetime.now().isoformat()
                    })
                    results['stages']['enrichment'] = 'success'
                    contact = self.db.get_contact(contact_id)
                    logger.info("  ✅ Enrichment completed")
                else:
                    logger.warning(f"  ⚠️ Enrichment failed: {enrichment_result.get('error')}")
                    results['stages']['enrichment'] = f"failed: {enrichment_result.get('error')}"
            
            # STAGE 2: Persona Classification
            if self.config.enable_persona_classification:
                logger.info("🎭 STAGE 2: Persona Classification")
                persona_result = self.persona_classifier.classify(contact)
                self.db.upsert_contact({
                    'id': contact_id,
                    'persona_type': persona_result.get('persona'),
                    'persona_confidence': persona_result.get('confidence')
                })
                results['stages']['persona'] = persona_result
                logger.info(f"  ✅ Persona: {persona_result.get('persona')}")
            
            # STAGE 3: Scoring
            if self.config.enable_scoring:
                logger.info("📈 STAGE 3: MDCP Scoring")
                scores = self.scoring_engine.score_contact(contact)
                self.db.upsert_contact({
                    'id': contact_id,
                    'mdcp_score': scores.get('mdcp_score'),
                    'mdcp_tier': scores.get('mdcp_tier'),
                    'priority_score': scores.get('priority_score'),
                    'urgency_level': scores.get('urgency_level'),
                    'rss_score': scores.get('rss_score'),
                    'rss_tier': scores.get('rss_tier'),
                    'last_scored': datetime.now().isoformat()
                })
                results['stages']['scoring'] = scores
                logger.info(f"  ✅ MDCP: {scores.get('mdcp_score'):.1f}")
            
            # STAGE 4: Content Generation
            if self.config.enable_content_generation:
                logger.info("✍️ STAGE 4: Content Generation")
                content = self.content_generator.generate_all(contact)
                self.db.upsert_contact({'id': contact_id, **content})
                results['stages']['content'] = 'generated'
                logger.info("  ✅ Content generated")
            
            logger.info(f"{'='*80}")
            logger.info("🎉 FULL PIPELINE COMPLETE!")
            logger.info(f"{'='*80}\n")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Pipeline error for contact {contact_id}: {e}")
            return {
                'error': str(e),
                'contact_id': contact_id,
                'stages': results.get('stages', {})
            }

# ============================================================================
# SECTION 4: INTELLIGENCE ENGINES
# ============================================================================

class EnrichmentEngine:
    """Two-stage enrichment wrapper"""
    
    def __init__(self, config):
        self.custom_engine = ApexCustomEnrichment(config)
        self.db = None
        
    def set_database(self, db):
        """Set database reference"""
        self.db = db
        
    def enrich_contact(self, contact: Dict) -> Dict:
        """Execute two-stage enrichment with post-processing"""
        try:
            result = self.custom_engine.enrich_contact_full(contact)
            
            if result.get('status') == 'success':
                profile_data = result['profile_data']
                
                # The synthesized intelligence (post-GPT)
                enrichment_text = profile_data['synthesized_intelligence']
                
                # The parsed structured fields (post-processing)
                parsed_fields = profile_data['parsed_fields']
                
                # Build update payload
                update_data = {
                    'profile_content': enrichment_text,
                    'enrichment_status': 'completed',
                    'enrichment_date': datetime.now().isoformat(),
                    'data_completeness_score': parsed_fields.get('enrichment_confidence', 90),
                }
                
                # Add personality fields if extracted
                if parsed_fields.get('myers_briggs'):
                    update_data['myers_briggs'] = parsed_fields['myers_briggs']
                    
                if parsed_fields.get('disc_profile'):
                    update_data['disc_profile'] = parsed_fields['disc_profile']
                    
                if parsed_fields.get('strengthsfinder_themes'):
                    update_data['strengthsfinder_themes'] = json.dumps(parsed_fields['strengthsfinder_themes'])
                    
                # Add social profiles
                if parsed_fields.get('instagram_url'):
                    update_data['instagram_url'] = parsed_fields['instagram_url']
                    
                if parsed_fields.get('twitter_url'):
                    update_data['twitter_url'] = parsed_fields['twitter_url']
                    
                if parsed_fields.get('facebook_url'):
                    update_data['facebook_url'] = parsed_fields['facebook_url']
                    
                # Add talking points and pain points
                if parsed_fields.get('talking_points'):
                    update_data['value_proposition'] = '\n'.join(parsed_fields['talking_points'][:3])
                    
                if parsed_fields.get('pain_points'):
                    update_data['pain_points_matched'] = '\n'.join(parsed_fields['pain_points'])
                    
                if parsed_fields.get('best_contact_channel'):
                    update_data['best_contact_channel'] = parsed_fields['best_contact_channel']
                    
                return {
                    'status': 'success',
                    'enrichment_data': enrichment_text,
                    'enrichment_notes': result.get('enrichment_notes', ''),
                    'update_data': update_data
                }
            else:
                return result
            
        except Exception as e:
            logger.error(f"Two-stage enrichment error: {e}")
            return {'status': 'error', 'error': str(e)}
        
        

Generate a comprehensive profile: Overview, Background, Education, Recent Activity, 
Social Media, Personality, Company Details, Pain Points, Opportunities, Insights."""
    
    def _call_perplexity(self, query: str) -> Optional[str]:
        """Call Perplexity API"""
        try:
            import requests
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers={'Authorization': f'Bearer {self.perplexity_key}', 'Content-Type': 'application/json'},
                json={'model': 'sonar-pro', 'messages': [{'role': 'user', 'content': query}],
                      'temperature': 0.2, 'max_tokens': 4000},
                timeout=self.config.enrichment_timeout
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            logger.error(f"Perplexity error: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Perplexity failed: {e}")
            return None
    
    def _call_gpt4(self, raw_profile: str, contact: Dict) -> Optional[str]:
        """Structure with GPT-4"""
        if not self.openai_key:
            return raw_profile
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            prompt = f"""Transform this research into structured profile for {contact.get('name')}:

{raw_profile}

Format with sections: Overview, Background, Education, Social Media, Personality, 
Company Details, Pain Points, Opportunities, Key Insights."""
            
            response = client.chat.completions.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': 'You are a sales intelligence analyst.'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.4, max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"GPT-4 error: {e}")
            return raw_profile

class ScoringEngine:
    """MDCP Scoring"""
    
    TITLE_SCORES = {
        'ceo': 95, 'president': 95, 'owner': 95, 'founder': 95,
        'cfo': 90, 'coo': 90, 'cmo': 90, 'cto': 90,
        'vp': 85, 'vice president': 85, 'director': 85,
        'senior': 75, 'manager': 70, 'lead': 70
    }
    
    def __init__(self, config: ApexConfig):
        self.config = config
    
    def score_contact(self, contact: Dict) -> Dict:
        """Calculate all scores"""
        mdcp = self._calculate_mdcp(contact)
        priority = self._calculate_priority(contact, mdcp)
        rss = 50.0
        
        return {
            'mdcp_score': round(mdcp, 1),
            'mdcp_tier': self._get_mdcp_tier(mdcp),
            'priority_score': round(priority, 1),
            'urgency_level': self._get_urgency(priority),
            'rss_score': round(rss, 1),
            'rss_tier': self._get_rss_tier(rss)
        }
    
    def _calculate_mdcp(self, contact: Dict) -> float:
        title = (contact.get('title') or '').lower()
        title_score = max([score for key, score in self.TITLE_SCORES.items() if key in title], default=50)
        profile_len = len(contact.get('profile_content') or '')
        enrichment_score = min(100, (profile_len / 500) * 100)
        return min(100, (title_score * 0.4) + (enrichment_score * 0.3) + (50 * 0.3))
    
    def _calculate_priority(self, contact: Dict, mdcp: float) -> float:
        return min(100, mdcp * 0.7 + 30)
    
    def _get_mdcp_tier(self, mdcp: float) -> str:
        if mdcp >= 71: return 'HOT'
        elif mdcp >= 41: return 'WARM'
        else: return 'COLD'
    
    def _get_urgency(self, priority: float) -> str:
        if priority >= 85: return 'IMMEDIATE'
        elif priority >= 70: return 'HIGH'
        elif priority >= 50: return 'MEDIUM'
        else: return 'LOW'
    
    def _get_rss_tier(self, rss: float) -> str:
        if rss >= 67: return 'GOLD'
        elif rss >= 34: return 'SILVER'
        else: return 'BRONZE'

class PersonaClassifier:
    """8 Decision Maker Personas"""
    
    def __init__(self, config: ApexConfig):
        self.config = config
    
    def classify(self, contact: Dict) -> Dict:
        title = (contact.get('title') or '').lower()
        
        if 'ceo' in title or 'founder' in title:
            return {'persona': 'VISIONARY_CEO', 'confidence': 0.9}
        elif 'cfo' in title:
            return {'persona': 'ANALYTICAL_CFO', 'confidence': 0.85}
        elif 'cto' in title:
            return {'persona': 'TECHNICAL_CTO', 'confidence': 0.85}
        elif 'cmo' in title:
            return {'persona': 'GROWTH_CMO', 'confidence': 0.85}
        elif 'vp' in title:
            return {'persona': 'STRATEGIC_VP', 'confidence': 0.75}
        else:
            return {'persona': 'TACTICAL_DIRECTOR', 'confidence': 0.6}

class ContentGenerator:
    """Generate emails, scripts, messages"""
    
    def __init__(self, config: ApexConfig):
        self.config = config
    
    def generate_all(self, contact: Dict) -> Dict:
        first_name = contact.get('first_name', contact.get('name', '').split()[0] if contact.get('name') else '')
        company = contact.get('company', 'your company')
        
        return {
            'email_1_subject': f"Quick question about {company}",
            'email_1_body': f"Hi {first_name},\n\nI noticed your work at {company}...\n\nBest regards",
            'call_script_1': f"Hi {first_name}, this is [YOUR NAME]...",
            'linkedin_connect': f"Hi {first_name}, I'd love to connect!",
            'value_proposition': f"For {contact.get('title')} at {company}: [Value prop]"
        }

# ============================================================================
# SECTION 5: REST API
# ============================================================================

from flask import Flask, jsonify, request
from flask_cors import CORS

class ApexAPI:
    """Flask REST API"""
    
    def __init__(self, config: ApexConfig, db: DatabaseManager, intelligence: IntelligenceOrchestrator):
        self.config = config
        self.db = db
        self.intelligence = intelligence
        self.app = Flask(__name__)
        CORS(self.app)
        self._register_routes()
    
    def _register_routes(self):
        @self.app.route('/api/health', methods=['GET'])
        def health():
            return jsonify({
                'status': 'healthy',
                'environment': self.config.environment.value,
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'database': 'connected',
                    'enrichment': 'enabled' if self.config.enable_enrichment else 'disabled',
                    'scoring': 'enabled' if self.config.enable_scoring else 'disabled'
                }
            })
        
        @self.app.route('/api/contacts', methods=['GET'])
        def get_contacts():
            limit = int(request.args.get('limit', 100))
            contacts = self.db.get_contacts(limit=limit)
            return jsonify({'success': True, 'count': len(contacts), 'contacts': contacts})
        
        @self.app.route('/api/contacts/<int:contact_id>', methods=['GET'])
        def get_contact(contact_id):
            contact = self.db.get_contact(contact_id)
            if not contact:
                return jsonify({'success': False, 'error': 'Contact not found'}), 404
            return jsonify({'success': True, 'contact': contact})
        
        @self.app.route('/api/contacts', methods=['POST'])
        def create_contact():
            data = request.json
            try:
                contact_id = self.db.upsert_contact(data)
                return jsonify({'success': True, 'contact_id': contact_id})
            except Exception as e:
                logger.error(f"Error creating contact: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
        def enrich_contact(contact_id):
            try:
                result = self.intelligence.process_contact_full_pipeline(contact_id)
                return jsonify({'success': True, 'result': result})
            except Exception as e:
                logger.error(f"Error enriching contact: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/todays-board', methods=['GET'])
        def todays_board():
            try:
                cursor = self.db.get_cursor()
                query = """
                    SELECT id, name, email, company, title, priority_score, mdcp_tier, urgency_level
                    FROM contacts WHERE enrichment_status = 'completed'
                    ORDER BY priority_score DESC LIMIT 20
                """
                cursor.execute(query)
                contacts = [dict(row) for row in cursor.fetchall()]
                
                return jsonify({
                    'success': True,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'contacts': contacts
                })
            except Exception as e:
                logger.error(f"Error in todays_board: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'contacts': []
                }), 500
    
    def run(self):
        """Start Flask server"""
        port = int(os.getenv('PORT', self.config.api_port))
        logger.info(f"🚀 APEX API Server starting on port {port}...")
        self.app.run(host='0.0.0.0', port=port, debug=self.config.debug_mode)

# ============================================================================
# SECTION 6: MAIN SYSTEM
# ============================================================================

class ApexIntelligenceSystem:
    """Master system orchestrator"""
    
    def __init__(self):
        logger.info("="*80)
        logger.info("🏛️  APEX INTELLIGENCE SYSTEM - INITIALIZING")
        logger.info("="*80)
        
        self.config = ApexConfig.from_env()
        self.db = DatabaseManager(self.config)
        self.intelligence = IntelligenceOrchestrator(self.config, self.db)
        self.api = ApexAPI(self.config, self.db, self.intelligence)
        
        logger.info("="*80)
        logger.info("✅ APEX INTELLIGENCE SYSTEM - READY")
        logger.info("="*80)
    
    def start(self):
        """Start the system"""
        logger.info(f"\n🎯 Environment: {self.config.environment.value.upper()}")
        logger.info(f"🗄️  Database: {self.config.db_type}")
        logger.info(f"🌐 API URL: {self.config.api_base_url}\n")
        self.api.run()
    
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down...")
        self.db.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == '__main__':
    try:
        apex = ApexIntelligenceSystem()
        apex.start()
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        apex.shutdown()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
 