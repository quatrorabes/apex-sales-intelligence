#!/usr/bin/env python3
"""
APEX SALES INTELLIGENCE - MASTER INTEGRATION SYSTEM
Production-Ready Architecture | Full Stack AI Sales Platform
Version: 2.2 | Date: December 3, 2025
"""

import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Custom modules
sys.path.append('.')
from apex_custom_enrichment import ApexCustomEnrichment

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("APEX_MASTER")

# ============================================================================
# CONFIGURATION
# ============================================================================

class Environment(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class ApexConfig:
    environment: Environment = Environment.LOCAL
    debug_mode: bool = True
    api_base_url: str = "http://localhost:8000"
    db_type: str = "sqlite"
    db_path: str = "./apex.db"
    db_url: Optional[str] = None
    perplexity_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'ApexConfig':
        """Load configuration from environment variables"""
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
        )
        
        logger.info(f"✅ Configuration loaded for {env.value.upper()} environment")
        return config

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Unified database manager supporting SQLite and PostgreSQL"""
    
    def __init__(self, config: ApexConfig):
        self.config = config
        self.conn = None
        self._initialize_connection()
        self._ensure_schema()
    
    def _initialize_connection(self):
        """Initialize database connection"""
        if self.config.db_type == 'postgresql':
            import psycopg2
            from psycopg2.extras import RealDictCursor
            from psycopg2 import extensions
            self.conn = psycopg2.connect(self.config.db_url)
            self.conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            self.cursor_factory = RealDictCursor
            logger.info("✅ PostgreSQL connection established (AUTOCOMMIT mode)")
        else:
            import sqlite3
            self.conn = sqlite3.connect(
                self.config.db_path,
                check_same_thread=False,
                timeout=30.0,
                isolation_level=None  # Autocommit
            )
            self.conn.row_factory = sqlite3.Row
            self.cursor_factory = None
            logger.info(f"✅ SQLite connection established: {self.config.db_path}")
    
    def get_cursor(self):
        """Get database cursor"""
        if self.cursor_factory:
            return self.conn.cursor(cursor_factory=self.cursor_factory)
        return self.conn.cursor()
    
    def _ensure_schema(self):
        """Create all required tables"""
        cursor = self.get_cursor()
        
        if self.config.db_type == 'postgresql':
            id_column = "id SERIAL PRIMARY KEY"
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
        else:
            id_column = "id INTEGER PRIMARY KEY AUTOINCREMENT"
            default_timestamp = "DEFAULT CURRENT_TIMESTAMP"
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS contacts (
                {id_column},
                first_name TEXT, last_name TEXT, name TEXT, email TEXT UNIQUE,
                phone TEXT, phone_mobile TEXT, company TEXT, title TEXT,
                linkedin_url TEXT, company_domain TEXT, company_website TEXT,
                profile_content TEXT, enrichment_status TEXT DEFAULT 'pending',
                enrichment_date TEXT, persona_type TEXT, persona_confidence REAL,
                priority_score REAL, mdcp_score REAL, mdcp_tier TEXT,
                urgency_level TEXT, last_scored TEXT,
                email_1_subject TEXT, email_1_body TEXT,
                call_script_1 TEXT, linkedin_connect TEXT,
                value_proposition TEXT, pain_points_matched TEXT,
                data_completeness_score INTEGER DEFAULT 0,
                myers_briggs TEXT, disc_profile TEXT, strengthsfinder_themes TEXT,
                instagram_url TEXT, twitter_url TEXT, facebook_url TEXT,
                best_contact_channel TEXT,
                created_at TIMESTAMP {default_timestamp},
                updated_at TIMESTAMP {default_timestamp}
            )
        """)
        
        if self.config.db_type != 'postgresql':
            self.conn.commit()
        
        logger.info("✅ Database schema initialized")
    
    def get_contact(self, contact_id: int) -> Optional[Dict]:
        """Retrieve single contact by ID"""
        cursor = self.get_cursor()
        placeholder = "%s" if self.config.db_type == 'postgresql' else "?"
        cursor.execute(f"SELECT * FROM contacts WHERE id = {placeholder}", (contact_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_contacts(self, limit: int = 100) -> List[Dict]:
        """Retrieve multiple contacts"""
        cursor = self.get_cursor()
        placeholder = "%s" if self.config.db_type == 'postgresql' else "?"
        cursor.execute(f"SELECT * FROM contacts LIMIT {placeholder}", (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def upsert_contact(self, contact_data: Dict) -> int:
        """Insert or update contact"""
        cursor = self.get_cursor()
        email = contact_data.get('email')
        placeholder = "%s" if self.config.db_type == 'postgresql' else "?"
        
        existing_id = None
        if email:
            cursor.execute(f"SELECT id FROM contacts WHERE email = {placeholder}", (email,))
            result = cursor.fetchone()
            if result:
                existing_id = result[0] if isinstance(result, tuple) else result['id']
        
        if existing_id:
            # Update
            set_clause = ', '.join([f"{k} = {placeholder}" for k in contact_data.keys() if k != 'id'])
            values = [v for k, v in contact_data.items() if k != 'id']
            values.append(existing_id)
            cursor.execute(
                f"UPDATE contacts SET {set_clause} WHERE id = {placeholder}",
                values
            )
            if self.config.db_type != 'postgresql':
                self.conn.commit()
            return existing_id
        else:
            # Insert
            columns = ', '.join(contact_data.keys())
            placeholders = ', '.join([placeholder for _ in contact_data])
            values = list(contact_data.values())
            cursor.execute(f"INSERT INTO contacts ({columns}) VALUES ({placeholders})", values)
            if self.config.db_type != 'postgresql':
                self.conn.commit()
            return cursor.lastrowid if self.config.db_type != 'postgresql' else existing_id
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# ============================================================================
# ENRICHMENT ENGINE
# ============================================================================

class EnrichmentEngine:
    """Two-stage enrichment wrapper"""
    
    def __init__(self, config):
        self.config = config
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
                enrichment_text = profile_data['synthesized_intelligence']
                parsed_fields = profile_data['parsed_fields']
                
                # Build update payload
                update_data = {
                    'profile_content': enrichment_text,
                    'enrichment_status': 'completed',
                    'enrichment_date': datetime.now().isoformat(),
                    'data_completeness_score': parsed_fields.get('enrichment_confidence', 90),
                }
                
                # Add optional fields if present
                if parsed_fields.get('myers_briggs'):
                    update_data['myers_briggs'] = parsed_fields['myers_briggs']
                if parsed_fields.get('disc_profile'):
                    update_data['disc_profile'] = parsed_fields['disc_profile']
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

# ============================================================================
# SCORING & PERSONA
# ============================================================================

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
        
        return {
            'mdcp_score': round(mdcp, 1),
            'mdcp_tier': self._get_mdcp_tier(mdcp),
            'priority_score': round(priority, 1),
            'urgency_level': self._get_urgency(priority)
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

# ============================================================================
# INTELLIGENCE ORCHESTRATOR
# ============================================================================

class IntelligenceOrchestrator:
    """Master orchestrator for all AI operations"""
    
    def __init__(self, config: ApexConfig, db: DatabaseManager):
        self.config = config
        self.db = db
        self.enrichment_engine = EnrichmentEngine(config)
        self.scoring_engine = ScoringEngine(config)
        self.persona_classifier = PersonaClassifier(config)
        self.enrichment_engine.set_database(db)
        logger.info("🚀 Intelligence Orchestrator initialized")
    
    def process_contact_full_pipeline(self, contact_id: int) -> Dict:
        """Execute complete intelligence pipeline"""
        logger.info(f"{'='*80}")
        logger.info(f"🎯 FULL INTELLIGENCE PIPELINE - Contact ID: {contact_id}")
        logger.info(f"{'='*80}")
        
        results = {'contact_id': contact_id, 'timestamp': datetime.now().isoformat(), 'stages': {}}
        contact = self.db.get_contact(contact_id)
        
        if not contact:
            return {'error': 'Contact not found'}
        
        # STAGE 1: Enrichment
        if contact.get('enrichment_status') != 'completed':
            logger.info("📊 STAGE 1: Two-Stage Enrichment")
            enrichment_result = self.enrichment_engine.enrich_contact(contact)
            
            if enrichment_result.get('status') == 'success':
                update_data = enrichment_result.get('update_data', {})
                update_data['id'] = contact_id
                self.db.upsert_contact(update_data)
                results['stages']['enrichment'] = 'success'
                contact = self.db.get_contact(contact_id)
                logger.info("  ✅ Enrichment completed")
        
        # STAGE 2: Persona
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
        logger.info("📈 STAGE 3: MDCP Scoring")
        scores = self.scoring_engine.score_contact(contact)
        self.db.upsert_contact({
            'id': contact_id,
            'mdcp_score': scores.get('mdcp_score'),
            'mdcp_tier': scores.get('mdcp_tier'),
            'priority_score': scores.get('priority_score'),
            'urgency_level': scores.get('urgency_level'),
            'last_scored': datetime.now().isoformat()
        })
        results['stages']['scoring'] = scores
        logger.info(f"  ✅ MDCP: {scores.get('mdcp_score'):.1f}")
        
        logger.info(f"{'='*80}")
        logger.info("🎉 FULL PIPELINE COMPLETE!")
        logger.info(f"{'='*80}\n")
        
        return results

# ============================================================================
# FLASK API
# ============================================================================

def create_app(config: ApexConfig, db: DatabaseManager, intelligence: IntelligenceOrchestrator):
    """Flask app factory"""
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/health', methods=['GET'])
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'environment': config.environment.value,
            'timestamp': datetime.now().isoformat()
        })
    
    @app.route('/api/contacts', methods=['GET'])
    def get_contacts():
        limit = int(request.args.get('limit', 100))
        contacts = db.get_contacts(limit=limit)
        return jsonify({'success': True, 'count': len(contacts), 'contacts': contacts})
    
    @app.route('/api/contacts/<int:contact_id>', methods=['GET'])
    def get_contact(contact_id):
        contact = db.get_contact(contact_id)
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'}), 404
        return jsonify({'success': True, 'contact': contact})
    
    @app.route('/api/contacts', methods=['POST'])
    def create_contact():
        data = request.json
        contact_id = db.upsert_contact(data)
        return jsonify({'success': True, 'contact_id': contact_id})
    
    @app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
    def enrich_contact(contact_id):
        try:
            contact = db.get_contact(contact_id)
            if not contact:
                return jsonify({'success': False, 'error': 'Contact not found'}), 404
            
            # Enrich
            result = intelligence.enrichment_engine.enrich_contact(contact)
            
            if result.get('status') == 'success':
                update_data = result.get('update_data', {})
                update_data['id'] = contact_id
                db.upsert_contact(update_data)
                
                return jsonify({
                    'success': True,
                    'status': 'success',
                    'contact_id': contact_id,
                    'message': 'Two-stage enrichment completed',
                    'fields_updated': list(update_data.keys()),
                    'notes': result.get('enrichment_notes')
                })
            else:
                return jsonify({
                    'success': False,
                    'status': 'error',
                    'error': result.get('error', 'Enrichment failed')
                }), 500
                
        except Exception as e:
            logger.error(f"Enrichment endpoint error: {e}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/contacts/<int:contact_id>/pipeline', methods=['POST'])
    def run_pipeline(contact_id):
        result = intelligence.process_contact_full_pipeline(contact_id)
        return jsonify({'success': True, 'result': result})
    
    @app.route('/api/todays-board', methods=['GET'])
    def todays_board():
        try:
            cursor = db.get_cursor()
            placeholder = "%s" if db.config.db_type == 'postgresql' else "?"
            query = f"""
                SELECT id, name, email, company, title, priority_score, mdcp_tier, urgency_level
                FROM contacts
                WHERE enrichment_status = 'completed'
                ORDER BY priority_score DESC
                LIMIT {placeholder}
            """
            cursor.execute(query, (20,))
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
    
    return app

# ============================================================================
# MAIN SYSTEM
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
        self.app = create_app(self.config, self.db, self.intelligence)
        
        logger.info("="*80)
        logger.info("✅ APEX INTELLIGENCE SYSTEM - READY")
        logger.info("="*80)
    
    def start(self):
        """Start the system"""
        port = int(os.getenv('PORT', 8000))
        logger.info(f"\n🎯 Environment: {self.config.environment.value.upper()}")
        logger.info(f"🗄️  Database: {self.config.db_type}")
        logger.info(f"🌐 API URL: {self.config.api_base_url}")
        logger.info(f"🚀 Starting server on port {port}...\n")
        
        self.app.run(host='0.0.0.0', port=port, debug=self.config.debug_mode)
    
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
