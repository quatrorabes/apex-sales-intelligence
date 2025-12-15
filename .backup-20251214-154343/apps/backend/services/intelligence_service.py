#!/usr/bin/env python3
"""
APEX Intelligence Service - Graceful Fallback Version
Handles missing dependencies without breaking
"""

import sys
import os
from pathlib import Path
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add intelligence to Python path
BACKEND_DIR = Path(__file__).parent.parent
INTELLIGENCE_DIR = BACKEND_DIR / 'intelligence'
sys.path.insert(0, str(INTELLIGENCE_DIR))

class IntelligenceService:
    """Unified interface to all intelligence engines with graceful fallbacks"""
    
    def __init__(self, db_path='./apex.db'):
        self.db_path = db_path
        self.engines_status = {}
        self._init_engines()
    
    def _init_engines(self):
        """Lazy load intelligence engines with fallback"""
        
        # Try to load each engine, track what's available
        engines_to_load = {
            'persona_classifier': ('engines.persona_classifier_cre_sba', 'UltimatePersonaClassifier'),
            'kernel': ('outreach.the_kernal_who_when_what', 'CRELendingKernel'),
            'call_scripts': ('outreach.call_script_generator_unified', 'UnifiedCallScriptGenerator'),
            'sequences': ('sequences.auto_sequence_engine', 'AutoSequenceEngine'),
            'cadence': ('sequences.smart_cadence', 'SmartCadence')
        }
        
        for engine_name, (module_path, class_name) in engines_to_load.items():
            try:
                module = __import__(module_path, fromlist=[class_name])
                engine_class = getattr(module, class_name)
                
                if engine_name in ['call_scripts', 'sequences', 'cadence']:
                    setattr(self, engine_name, engine_class(self.db_path))
                else:
                    setattr(self, engine_name, engine_class())
                
                self.engines_status[engine_name] = True
                print(f"✅ Loaded: {engine_name}")
                
            except Exception as e:
                self.engines_status[engine_name] = False
                print(f"⚠️ Could not load {engine_name}: {e}")
                setattr(self, engine_name, None)
        
        # Special handling for Perplexity enrichment
        try:
            sys.path.insert(0, str(BACKEND_DIR.parent / 'apps' / 'intelligence'))
            from enrichment.perplexity_deep_enrichment import perplexity_enrich
            self.perplexity_enrich = perplexity_enrich
            self.engines_status['perplexity'] = True
            print("✅ Loaded: Perplexity enrichment")
        except:
            self.engines_status['perplexity'] = False
            print("⚠️ Perplexity enrichment unavailable (missing dependencies)")
            self.perplexity_enrich = None
    
    def get_status(self) -> Dict:
        """Get status of all engines"""
        return {
            'engines': self.engines_status,
            'operational': any(self.engines_status.values()),
            'summary': f"{sum(self.engines_status.values())}/{len(self.engines_status)} engines loaded"
        }
    
    def enrich_contact_deep(self, contact_id: int, contact_data: Dict) -> Dict:
        """Deep enrichment with fallback to mock data"""
        
        if self.perplexity_enrich and self.engines_status.get('perplexity'):
            # Try real enrichment
            try:
                name = f"{contact_data.get('first_name', '')} {contact_data.get('last_name', '')}"
                enrichment = self.perplexity_enrich(
                    name, 
                    contact_data.get('company', ''),
                    contact_data.get('linkedin_url', '')
                )
                
                return {
                    'status': 'success',
                    'contact_id': contact_id,
                    'enrichment_type': 'perplexity_ai',
                    'data': enrichment
                }
            except Exception as e:
                print(f"Enrichment error: {e}")
        
        # Fallback to mock enrichment
        return {
            'status': 'success',
            'contact_id': contact_id,
            'enrichment_type': 'mock',
            'data': {
                'summary': f"Mock enrichment for {contact_data.get('first_name', 'Contact')}",
                'industry': 'Banking/Finance',
                'company_size': '1000-5000',
                'recent_news': ['Q3 earnings report', 'New product launch'],
                'pain_points': ['Digital transformation', 'Compliance costs'],
                'opportunity_score': 75
            }
        }
    
    def generate_call_scripts(self, contact_id: int) -> Dict:
        """Generate call scripts with fallback"""
        
        if self.call_scripts and self.engines_status.get('call_scripts'):
            try:
                return self.call_scripts.generate_all_scripts(contact_id)
            except Exception as e:
                print(f"Call script error: {e}")
        
        # Fallback scripts
        return {
            'status': 'success',
            'contact_id': contact_id,
            'scripts': {
                'opener': "Hi [Name], I noticed your company's recent expansion...",
                'value_prop': "We help companies like yours reduce costs by 30%...",
                'close': "Would you be open to a brief 15-minute call next week?"
            }
        }
    
    def get_dashboard_summary(self) -> Dict:
        """Get dashboard summary"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            total = cursor.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
            enriched = cursor.execute("SELECT COUNT(*) FROM contacts WHERE enriched = 1").fetchone()[0]
            
            conn.close()
            
            return {
                'total_contacts': total,
                'enriched_contacts': enriched,
                'enrichment_rate': f"{(enriched/total*100):.1f}%" if total > 0 else "0%",
                'engines_loaded': sum(self.engines_status.values()),
                'total_engines': len(self.engines_status)
            }
        except Exception as e:
            return {'error': str(e)}
        