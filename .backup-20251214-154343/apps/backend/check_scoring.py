#!/usr/bin/env python3
"""
Diagnostic Script - Check Scoring Status
"""

import sqlite3
import sys

DATABASE = "apex.db"

def check_scoring_status():
    """Check if contacts are scored and diagnose issues"""
    
    print("🔍 APEX Scoring Diagnostic")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Check total contacts
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total contacts in database: {total}")
    
    # 2. Check scored contacts
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE priority_score IS NOT NULL")
    scored = cursor.fetchone()[0]
    print(f"✅ Scored contacts: {scored}")
    print(f"❌ Unscored contacts: {total - scored}")
    
    # 3. Check if scoring columns exist
    cursor.execute("PRAGMA table_info(contacts)")
    columns = {row[1] for row in cursor.fetchall()}
    
    required_cols = ['mdcp_score', 'rss_score', 'priority_score', 'persona_tier', 'persona_type']
    missing_cols = [col for col in required_cols if col not in columns]
    
    if missing_cols:
        print(f"\n❌ Missing columns: {', '.join(missing_cols)}")
        print("   Run: python migrate_scoring_columns.py")
    else:
        print(f"\n✅ All scoring columns present")
    
    # 4. Show sample scored contacts
    if scored > 0:
        print(f"\n📋 Sample scored contacts:")
        cursor.execute("""
            SELECT id, name, priority_score, mdcp_score, rss_score, persona_tier
            FROM contacts 
            WHERE priority_score IS NOT NULL 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"   ID {row[0]}: {row[1]}")
            print(f"      Priority: {row[2]:.1f} | MDCP: {row[3]:.1f} | RSS: {row[4]:.1f} | Persona: {row[5]}")
    
    # 5. Show sample unscored contacts
    if total - scored > 0:
        print(f"\n📋 Sample UNSCORED contacts:")
        cursor.execute("""
            SELECT id, name, company, title
            FROM contacts 
            WHERE priority_score IS NULL 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            print(f"   ID {row[0]}: {row[1]} - {row[2]} - {row[3]}")
    
    # 6. Test scoring on one contact
    if total - scored > 0:
        print(f"\n🧪 Testing scoring on contact ID 1...")
        try:
            sys.path.insert(0, '.')
            from intelligence.engines.scoring.scoring_orchestrator import ScoringOrchestrator
            
            orchestrator = ScoringOrchestrator(conn)
            result = orchestrator.score_contact(1, trigger='test')
            
            if 'error' in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                print(f"   ✅ Success! Priority Score: {result.get('priority_score', 0):.1f}")
                
        except Exception as e:
            print(f"   ❌ Error during test scoring: {e}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    
    # 7. Recommendations
    print("\n💡 Recommendations:")
    if missing_cols:
        print("   1. Run: python migrate_scoring_columns.py")
    if total - scored > 0:
        print("   2. Run: python bulk_score_all.py")
    if scored == total:
        print("   ✅ All contacts are scored! Check your dashboard.")

if __name__ == "__main__":
    check_scoring_status()
