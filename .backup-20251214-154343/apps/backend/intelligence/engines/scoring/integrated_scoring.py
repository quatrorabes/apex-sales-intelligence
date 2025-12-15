#!/usr/bin/env python3
"""
APEX Scoring Integration - Phase 1 & 2
Deploys apex_scoring_engine.py + user_scoring_engine.py into production pipeline

Run from: projects/apex/apps/backend/intelligence/engines/scoring/
"""

import os
import shutil
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# ============================================================================
# PATH DETECTION (HARDCODED)
# ============================================================================

SCRIPT_DIR = Path("/Users/chrisrabenold/projects/apex/apps/backend/intelligence/engines/scoring")
PROJECT_ROOT = Path("/Users/chrisrabenold/projects/apex")
ENGINES_DIR = SCRIPT_DIR
DB_PATH = Path("/Users/chrisrabenold/projects/apex/apex.db")

print(f"\n{'='*80}")
print(f"APEX SCORING INTEGRATION - PHASES 1 & 2")
print(f"{'='*80}")
print(f"Script location: {SCRIPT_DIR}")
print(f"Project root: {PROJECT_ROOT}")
print(f"Engines directory: {ENGINES_DIR}")
print(f"Database: {DB_PATH}")
print(f"Database exists: {DB_PATH.exists()}")
print(f"{'='*80}\n")

# Verify paths
if not PROJECT_ROOT.exists():
    print(f"❌ ERROR: Project root not found: {PROJECT_ROOT}")
    sys.exit(1)

if not DB_PATH.exists():
    print(f"❌ ERROR: Database not found: {DB_PATH}")
    print(f"   Expected: {DB_PATH}")
    print(f"   Please verify apex.db location")
    sys.exit(1)

if not SCRIPT_DIR.exists():
    print(f"❌ ERROR: Script directory not found: {SCRIPT_DIR}")
    sys.exit(1)

print("✅ All paths verified\n")


# ============================================================================
# PHASE 1: DEPLOY FOUNDATION SCORING ENGINE
# ============================================================================

def phase1_deploy_foundation():
    """Deploy apex_scoring_engine.py as primary scorer"""
    
    print("="*80)
    print("PHASE 1: DEPLOYING FOUNDATION SCORING ENGINE")
    print("="*80 + "\n")
    
    # Check if apex_scoring_engine.py exists in current directory
    source_file = ENGINES_DIR / "apex_scoring_engine.py"
    
    if not source_file.exists():
        print(f"❌ ERROR: apex_scoring_engine.py not found in {ENGINES_DIR}")
        print(f"   Please copy it to this directory first.")
        return False
    
    print(f"✅ apex_scoring_engine.py found in {ENGINES_DIR}")
    
    # Verify database schema
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check for required columns
    cursor.execute("PRAGMA table_info(contacts)")
    columns = [row[1] for row in cursor.fetchall()]
    
    required_columns = {
        'mdcp_score': 'REAL',
        'mdcp_tier': 'TEXT',
        'rss_score': 'REAL',
        'rss_tier': 'TEXT',
        'priority_score': 'REAL',
        'urgency_level': 'TEXT',
        'recommended_action': 'TEXT',
        'last_scored': 'TEXT',
        'calculation_version': 'TEXT'
    }
    
    missing_columns = [col for col in required_columns.keys() if col not in columns]
    
    if missing_columns:
        print(f"\n⚠️  Adding {len(missing_columns)} missing columns to contacts table...")
        for col in missing_columns:
            col_type = required_columns[col]
            try:
                cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col} {col_type}")
                print(f"   ✅ Added column: {col} ({col_type})")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    print(f"   ⚠️  Warning for {col}: {e}")
        
        conn.commit()
        print(f"\n✅ Database schema updated")
    else:
        print("✅ All required columns present in contacts table")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ PHASE 1 COMPLETE - Foundation scoring engine deployed")
    print("="*80 + "\n")
    return True


# ============================================================================
# PHASE 2: DEPLOY CRE INTELLIGENCE LAYER
# ============================================================================

def phase2_deploy_cre_intelligence():
    """Deploy user_scoring_engine.py as CRE vertical booster"""
    
    print("="*80)
    print("PHASE 2: DEPLOYING CRE INTELLIGENCE LAYER")
    print("="*80 + "\n")
    
    # Check if user_scoring_engine.py exists
    source_file = ENGINES_DIR / "user_scoring_engine.py"
    
    if not source_file.exists():
        print(f"❌ ERROR: user_scoring_engine.py not found in {ENGINES_DIR}")
        print(f"   Please copy it to this directory first.")
        return False
    
    print(f"✅ user_scoring_engine.py found in {ENGINES_DIR}")
    
    # Verify user_preferences table exists
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='user_preferences'
    """)
    
    if not cursor.fetchone():
        print("\n⚠️  Creating user_preferences table...")
        cursor.execute("""
            CREATE TABLE user_preferences (
                user_id TEXT PRIMARY KEY,
                scoring_profile TEXT DEFAULT 'CRE_MORTGAGE',
                custom_ideal_titles TEXT DEFAULT '[]',
                custom_avoid_titles TEXT DEFAULT '[]',
                ideal_company_size_min INTEGER DEFAULT 10,
                ideal_company_size_max INTEGER DEFAULT 5000,
                target_seniority_levels TEXT DEFAULT '[]',
                exclude_c_suite INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default CRE preferences
        cursor.execute("""
            INSERT INTO user_preferences (
                user_id, 
                scoring_profile, 
                custom_ideal_titles, 
                custom_avoid_titles, 
                target_seniority_levels
            )
            VALUES (
                'default', 
                'CRE_MORTGAGE',
                '["broker", "commercial", "real estate", "leasing", "investment", "loan officer", "mortgage banker", "relationship manager"]',
                '["residential", "personal", "hr", "human resources", "marketing", "it", "legal", "compliance"]',
                '["VP", "SVP", "Director", "Manager", "Associate", "Partner", "Principal"]'
            )
        """)
        
        conn.commit()
        print("✅ Created user_preferences table with CRE defaults")
    else:
        print("✅ user_preferences table already exists")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ PHASE 2 COMPLETE - CRE intelligence layer deployed")
    print("="*80 + "\n")
    return True


# ============================================================================
# CREATE UNIFIED SCORING FUNCTION
# ============================================================================

def create_unified_scorer():
    """Create unified scoring function that combines both engines"""
    
    print("="*80)
    print("CREATING UNIFIED SCORING FUNCTION")
    print("="*80 + "\n")
    
    unified_scorer_code = f'''"""
APEX Unified Scoring - Phase 1 & 2 Integration
Combines ApexScoringEngine (foundation) + UserSpecificScoringEngine (CRE intelligence)

Auto-generated: {datetime.now().isoformat()}
"""

import sys
import os
from typing import Dict, Optional
from pathlib import Path

# Ensure we can import sibling modules
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from apex_scoring_engine import ApexScoringEngine
from user_scoring_engine import UserSpecificScoringEngine

# HARDCODED DATABASE PATH
DEFAULT_DB_PATH = "/Users/chrisrabenold/projects/apex/apex.db"


class UnifiedApexScorer:
    """Unified scorer combining foundation MDCP/RSS + CRE vertical intelligence"""
    
    def __init__(self, db_path: str = None, user_id: str = None):
        """Initialize both scoring engines"""
        # Always use absolute path
        if db_path is None:
            db_path = DEFAULT_DB_PATH
        
        # Verify database exists
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"❌ Database not found: {{db_path}}")
        
        self.db_path = db_path
        self.user_id = user_id or os.getenv('CURRENT_USER_ID', 'default')
        
        print(f"Initializing scoring engines...")
        print(f"  Database: {{self.db_path}}")
        print(f"  User: {{self.user_id}}")
        
        # Initialize engines with explicit path
        self.apex_engine = ApexScoringEngine(db_path=self.db_path)
        self.cre_engine = UserSpecificScoringEngine(self.user_id, self.db_path)
        
        print(f"✅ Unified scorer initialized")
    
    def score_contact_unified(self, contact_id: int, save_to_db: bool = True) -> Dict:
        """
        Complete unified scoring pipeline
        
        1. Run foundation MDCP + RSS scoring
        2. Apply CRE vertical intelligence boost/penalty
        3. Generate final priority score
        4. Save to database
        """
        
        print(f"\\n{{'='*60}}")
        print(f"UNIFIED SCORING: Contact {{contact_id}}")
        print(f"{{'='*60}}")
        
        # STEP 1: Foundation scoring (MDCP + generic RSS)
        print("\\n[1/3] Running foundation MDCP + RSS scoring...")
        foundation_result = self.apex_engine.score_contact(contact_id, save_to_db=False)
        
        print(f"   Foundation MDCP: {{foundation_result['mdcp_score']:.2f}}")
        print(f"   Foundation RSS:  {{foundation_result['rss_score']:.2f}}")
        print(f"   Foundation Priority: {{foundation_result['priority_score']:.2f}}")
        
        # STEP 2: CRE vertical intelligence boost
        print("\\n[2/3] Applying CRE vertical intelligence...")
        
        # Fetch contact for CRE analysis
        contact = dict(self.apex_engine.fetch_contact_data(contact_id))
        
        # Get CRE-specific RSS score
        cre_rss_result = self.cre_engine.calculate_personalized_rss(contact)
        cre_rss_score = cre_rss_result['total']
        
        print(f"   CRE RSS Score: {{cre_rss_score:.2f}}")
        print(f"   Reason: {{cre_rss_result['breakdown']['reason']}}")
        
        # Determine if CRE boost or penalty applies
        rss_delta = cre_rss_score - foundation_result['rss_score']
        
        if rss_delta > 0:
            print(f"   ✅ CRE BOOST: +{{rss_delta:.2f}} points")
        elif rss_delta < 0:
            print(f"   ⚠️  CRE PENALTY: {{rss_delta:.2f}} points")
        else:
            print(f"   → No CRE adjustment needed")
        
        # STEP 3: Recalculate priority with CRE-enhanced RSS
        print("\\n[3/3] Calculating final priority score...")
        
        lifecycle_stage = foundation_result['lifecycle_stage']
        mdcp_score = foundation_result['mdcp_score']
        
        # Use CRE RSS instead of foundation RSS
        final_priority_result = self.apex_engine.calculate_priority_score(
            mdcp_score,
            cre_rss_score,  # CRE-enhanced RSS
            lifecycle_stage,
            foundation_result['lead_type']
        )
        
        # Assemble final result
        final_result = {{
            **foundation_result,
            'rss_score': cre_rss_score,  # Override with CRE RSS
            'rss_tier': self.apex_engine.classify_rss_tier(cre_rss_score),
            'priority_score': final_priority_result['score'],
            'urgency_level': final_priority_result['urgency'],
            'recommended_action': final_priority_result['action'],
            'cre_vertical_applied': True,
            'cre_vertical_data': cre_rss_result['breakdown']
        }}
        
        print(f"\\n   Final MDCP: {{final_result['mdcp_score']:.2f}} ({{final_result['mdcp_tier']}})")
        print(f"   Final RSS:  {{final_result['rss_score']:.2f}} ({{final_result['rss_tier']}})")
        print(f"   Final Priority: {{final_result['priority_score']:.2f}} ({{final_result['urgency_level']}})")
        print(f"   Action: {{final_result['recommended_action']}}")
        
        # STEP 4: Save to database
        if save_to_db:
            print("\\n   💾 Saving to database...")
            self.apex_engine.save_scores_to_db(final_result)
        
        print(f"\\n{{'='*60}}")
        print(f"✅ UNIFIED SCORING COMPLETE")
        print(f"{{'='*60}}\\n")
        
        return final_result
    
    def bulk_score_unified(self, contact_ids: list) -> list:
        """Score multiple contacts with unified pipeline"""
        results = []
        
        print(f"\\n🎯 Starting bulk unified scoring for {{len(contact_ids)}} contacts\\n")
        
        for i, contact_id in enumerate(contact_ids, 1):
            try:
                print(f"[{{i}}/{{len(contact_ids)}}] Scoring contact {{contact_id}}...")
                result = self.score_contact_unified(contact_id)
                results.append(result)
            except Exception as e:
                print(f"❌ Error scoring contact {{contact_id}}: {{e}}")
                results.append({{'contact_id': contact_id, 'error': str(e)}})
        
        print(f"\\n✅ Bulk unified scoring complete: {{len(results)}} contacts processed\\n")
        return results


# ============================================================================
# QUICK SCORING FUNCTIONS
# ============================================================================

def score_contact_unified(contact_id: int, db_path: str = None, user_id: str = None) -> Dict:
    """Quick function to score a single contact with unified pipeline"""
    scorer = UnifiedApexScorer(db_path, user_id)
    return scorer.score_contact_unified(contact_id)


def bulk_score_unified(contact_ids: list, db_path: str = None, user_id: str = None) -> list:
    """Quick function to score multiple contacts with unified pipeline"""
    scorer = UnifiedApexScorer(db_path, user_id)
    return scorer.bulk_score_unified(contact_ids)


# ============================================================================
# CLI INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python unified_apex_scorer.py tact_id>          # Score single contact")
        print("  python unified_apex_scorer.py <id1> <id2> <id3>...  # Score multiple contacts")
        sys.exit(1)
    
    contact_ids = [int(cid) for cid in sys.argv[1:]]
    
    if len(contact_ids) == 1:
        result = score_contact_unified(contact_ids[0])
        print(f"\\n📊 FINAL RESULT:")
        print(f"   Contact: {{result['contact_name']}}")
        print(f"   Priority: {{result['priority_score']:.2f}}")
        print(f"   Urgency: {{result['urgency_level']}}")
        print(f"   Action: {{result['recommended_action']}}")
    else:
        results = bulk_score_unified(contact_ids)
        print(f"\\n📊 BULK RESULTS:")
        for r in results:
            if 'error' not in r:
                print(f"   {{r['contact_id']:3d}} | {{r['contact_name']:30s}} | Priority: {{r['priority_score']:5.2f}} | {{r['urgency_level']}}")
'''
    
    # Write unified scorer
    unified_file = ENGINES_DIR / "unified_apex_scorer.py"
    unified_file.write_text(unified_scorer_code)
    print(f"✅ Created unified scorer: {unified_file}")
    
    print("\n" + "="*80)
    print("✅ UNIFIED SCORING FUNCTION READY")
    print("="*80 + "\n")
    return True


# ============================================================================
# GENERATE API INTEGRATION SNIPPET
# ============================================================================

def generate_api_integration():
    """Generate code snippet for api.py integration"""
    
    print("="*80)
    print("GENERATING API.PY INTEGRATION SNIPPET")
    print("="*80 + "\n")
    
    api_snippet = '''
# ============================================================================
# APEX UNIFIED SCORING INTEGRATION
# Add this to api.py after imports and before Flask app routes
# ============================================================================

import sys
import os

# Import unified scorer
scoring_path = os.path.join(os.path.dirname(__file__), 'apps', 'backend', 'intelligence', 'engines', 'scoring')
sys.path.insert(0, scoring_path)

try:
    from unified_apex_scorer import UnifiedApexScorer
    SCORING_AVAILABLE = True
    unified_scorer = UnifiedApexScorer()
    print("✅ Unified Apex Scoring Engine loaded")
except ImportError as e:
    print(f"⚠️  Scoring engine not available: {e}")
    SCORING_AVAILABLE = False
    unified_scorer = None


# ============================================================================
# NEW ENDPOINT: Score Contact
# ============================================================================

@app.route('/api/contacts/<int:contact_id>/score', methods=['POST'])
def score_contact_endpoint(contact_id):
    """Score a contact with unified MDCP + CRE intelligence"""
    
    if not SCORING_AVAILABLE:
        return jsonify({'error': 'Scoring engine not available'}), 503
    
    try:
        result = unified_scorer.score_contact_unified(contact_id, save_to_db=True)
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'contact_name': result['contact_name'],
            'company': result['company'],
            'scores': {
                'mdcp': result['mdcp_score'],
                'mdcp_tier': result['mdcp_tier'],
                'rss': result['rss_score'],
                'rss_tier': result['rss_tier'],
                'priority': result['priority_score'],
                'urgency': result['urgency_level']
            },
            'action': result['recommended_action'],
            'cre_applied': result.get('cre_vertical_applied', False),
            'lifecycle_stage': result['lifecycle_stage'],
            'timestamp': result['calculated_at']
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# ============================================================================
# NEW ENDPOINT: Bulk Score
# ============================================================================

@app.route('/api/contacts/score/bulk', methods=['POST'])
def bulk_score_endpoint():
    """Score multiple contacts"""
    
    if not SCORING_AVAILABLE:
        return jsonify({'error': 'Scoring engine not available'}), 503
    
    data = request.json
    contact_ids = data.get('contact_ids', [])
    
    if not contact_ids:
        return jsonify({'error': 'No contact_ids provided'}), 400
    
    try:
        results = unified_scorer.bulk_score_unified(contact_ids)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# MODIFY: Auto-score after enrichment
# Find your /api/contacts/<int:contact_id>/enrich endpoint and add this
# at the end, before returning success response:
# ============================================================================

# AUTO-SCORE after enrichment completes
if SCORING_AVAILABLE:
    try:
        print(f"🎯 Auto-scoring contact {contact_id} after enrichment...")
        score_result = unified_scorer.score_contact_unified(contact_id, save_to_db=True)
        print(f"✅ Scored: Priority {score_result['priority_score']:.2f} ({score_result['urgency_level']})")
    except Exception as e:
        print(f"⚠️  Scoring failed (non-fatal): {e}")
        # Don't fail enrichment if scoring fails


# ============================================================================
# MODIFY: Today's Board endpoint to use scored priorities
# Replace your existing /api/todays-board query with:
# ============================================================================

@app.route('/api/todays-board', methods=['GET'])
def todays_board():
    """Get today's prioritized contacts based on unified scoring"""
    
    cursor = get_db_cursor()
    
    # Get top-priority scored contacts
    cursor.execute("""
        SELECT 
            id, name, email, company, title,
            mdcp_score, mdcp_tier,
            rss_score, rss_tier,
            priority_score, urgency_level,
            recommended_action, last_scored,
            last_contact_date
        FROM contacts 
        WHERE priority_score IS NOT NULL 
        ORDER BY priority_score DESC, last_scored DESC
        LIMIT 50
    """)
    
    contacts = [dict(row) for row in cursor.fetchall()]
    
    # Group by urgency
    board = {
        'IMMEDIATE': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    }
    
    for contact in contacts:
        urgency = contact.get('urgency_level', 'LOW')
        board.get(urgency, board['LOW']).append(contact)
    
    return jsonify({
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'board': board,
        'total_contacts': len(contacts)
    })
'''
    
    # Save snippet
    snippet_file = PROJECT_ROOT / "api_scoring_integration.txt"
    snippet_file.write_text(api_snippet)
    
    print(f"✅ API integration snippet saved to: {snippet_file}\n")
    
    print("="*80)
    print("📋 NEXT STEPS FOR API INTEGRATION")
    print("="*80)
    print(f"1. Open {PROJECT_ROOT / 'api.py'}")
    print(f"2. Copy contents from {snippet_file}")
    print("3. Paste after imports, before Flask routes")
    print("4. Find /api/contacts/<int:contact_id>/enrich endpoint")
    print("5. Add auto-scoring snippet at the end")
    print("6. Update /api/todays-board endpoint with new query")
    print("7. Restart Flask server")
    print("8. Test: curl -X POST http://localhost:8000/api/contacts/7555/score\n")
    
    return True


# ============================================================================
# RUN INTEGRATION TESTS
# ============================================================================

def run_integration_tests():
    """Test the integrated scoring system"""
    
    print("="*80)
    print("RUNNING INTEGRATION TESTS")
    print("="*80 + "\n")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(ENGINES_DIR))
        
        from unified_apex_scorer import UnifiedApexScorer
        
        # Use contact 7555 (Bart Hutchins @ California Bank & Trust)
        test_id = 7555
        
        print(f"TEST: Scoring contact {test_id} (Bart Hutchins @ California Bank & Trust)")
        
        # Run unified scoring
        scorer = UnifiedApexScorer()
        result = scorer.score_contact_unified(test_id)
        
        print(f"\n📊 TEST RESULTS:")
        print(f"   Contact: {result['contact_name']}")
        print(f"   Company: {result['company']}")
        print(f"   Lead Type: {result['lead_type']}")
        print(f"   Lifecycle: {result['lifecycle_stage']}")
        print(f"   MDCP: {result['mdcp_score']:.2f} ({result['mdcp_tier']})")
        print(f"   RSS: {result['rss_score']:.2f} ({result['rss_tier']})")
        print(f"   Priority: {result['priority_score']:.2f}")
        print(f"   Urgency: {result['urgency_level']}")
        print(f"   Action: {result['recommended_action']}")
        print(f"   CRE Applied: {result.get('cre_vertical_applied', False)}")
        
        print("\n✅ INTEGRATION TEST PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n❌ INTEGRATION TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Execute Phase 1 & 2 deployment"""
    
    print(f"\nStarting deployment at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Phase 1: Foundation
    if not phase1_deploy_foundation():
        print("\n❌ Phase 1 failed. Aborting.")
        return False
    
    # Phase 2: CRE Intelligence
    if not phase2_deploy_cre_intelligence():
        print("\n❌ Phase 2 failed. Aborting.")
        return False
    
    # Create unified scorer
    if not create_unified_scorer():
        print("\n❌ Unified scorer creation failed. Aborting.")
        return False
    
    # Generate API integration snippet
    if not generate_api_integration():
        print("\n❌ API integration generation failed. Aborting.")
        return False
    
    # Run tests
    print("\n")
    if run_integration_tests():
        print("="*80)
        print("✅ PHASES 1 & 2 DEPLOYMENT COMPLETE - READY FOR PRODUCTION")
        print("="*80)
        print("\n📋 DEPLOYMENT SUMMARY:")
        print("   ✅ Foundation scoring engine (apex_scoring_engine.py)")
        print("   ✅ CRE intelligence layer (user_scoring_engine.py)")
        print("   ✅ Unified scorer (unified_apex_scorer.py)")
        print("   ✅ Database schema verified/updated")
        print("   ✅ User preferences table created")
        print("   ✅ Integration tests passed on contact 7555")
        print(f"   ✅ API integration snippet: {PROJECT_ROOT / 'api_scoring_integration.txt'}")
        print("\n🚀 NEXT STEPS:")
        print("   1. Integrate snippet into api.py (see instructions above)")
        print("   2. Restart Flask: cd {PROJECT_ROOT} && python3 api.py")
        print("   3. Test scoring: curl -X POST http://localhost:8000/api/contacts/7555/score")
        print("   4. Commit and push to Railway")
        print(f"\n   git add .")
        print(f"   git commit -m 'Deploy Apex unified scoring - Phases 1 & 2'")
        print(f"   git push origin main\n")
        return True
    else:
        print("\n⚠️  Tests failed. Review errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
