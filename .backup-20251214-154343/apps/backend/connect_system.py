#!/usr/bin/env python3
"""
APEX System Connection Script
Connects all the parts: scoring, enrichment, analytics
"""

import sqlite3
import os
from datetime import datetime

DATABASE = "apex.db"

def main():
    print("🔌 APEX System Connection & Setup")
    print("=" * 70)
    
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Step 1: Check database
    print("\n1️⃣  Checking Database...")
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    print(f"   ✅ Found {total} contacts")
    
    # Step 2: Check scoring columns
    print("\n2️⃣  Checking Scoring Columns...")
    cursor.execute("PRAGMA table_info(contacts)")
    columns = {row[1] for row in cursor.fetchall()}
    
    required = ['mdcp_score', 'rss_score', 'priority_score', 'persona_tier', 'persona_type', 
                'enrichment_status', 'enrichment_data', 'last_scored']
    missing = [c for c in required if c not in columns]
    
    if missing:
        print(f"   ❌ Missing columns: {', '.join(missing)}")
        print("   💡 Adding missing columns...")
        
        for col in missing:
            col_type = "TEXT" if col in ['persona_tier', 'persona_type', 'enrichment_status', 'enrichment_data', 'last_scored'] else "REAL"
            try:
                cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col} {col_type}")
                print(f"      ✅ Added: {col}")
            except Exception as e:
                print(f"      ⏭️  {col} exists or error: {e}")
        
        conn.commit()
    else:
        print("   ✅ All scoring columns present")
    
    # Step 3: Check if contacts are scored
    print("\n3️⃣  Checking Scoring Status...")
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE priority_score IS NOT NULL")
    scored = cursor.fetchone()[0]
    
    print(f"   ✅ Scored: {scored}/{total}")
    
    if scored < total:
        print(f"\n   🎯 Need to score {total - scored} contacts")
        print("   💡 Scoring all contacts now...")
        
        import sys
        sys.path.insert(0, '.')
        from intelligence.engines.scoring.scoring_orchestrator import ScoringOrchestrator
        
        orchestrator = ScoringOrchestrator(conn)
        
        cursor.execute("SELECT id, name FROM contacts WHERE priority_score IS NULL")
        unscored = cursor.fetchall()
        
        for idx, contact in enumerate(unscored, 1):
            contact_id = contact[0]
            name = contact[1] or f"Contact {contact_id}"
            
            try:
                print(f"      [{idx}/{len(unscored)}] {name}...", end=" ")
                result = orchestrator.score_contact(contact_id, trigger='bulk')
                
                if 'error' not in result:
                    print(f"✅ {result.get('priority_score', 0):.1f}")
                else:
                    print(f"❌ {result['error']}")
            except Exception as e:
                print(f"❌ {e}")
        
        # Check final score count
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE priority_score IS NOT NULL")
        final_scored = cursor.fetchone()[0]
        print(f"\n   ✅ Scoring complete! {final_scored}/{total} contacts scored")
    else:
        print("   ✅ All contacts already scored!")
    
    # Step 4: Verify analytics data
    print("\n4️⃣  Checking Analytics...")
    cursor.execute("""
        SELECT 
            AVG(priority_score) as avg_priority,
            AVG(mdcp_score) as avg_mdcp,
            AVG(rss_score) as avg_rss,
            COUNT(CASE WHEN priority_score > 70 THEN 1 END) as high_priority
        FROM contacts
        WHERE priority_score IS NOT NULL
    """)
    
    stats = cursor.fetchone()
    
    if stats[0]:  # If avg_priority exists
        print(f"   ✅ Average Priority Score: {stats[0]:.1f}")
        print(f"   ✅ Average MDCP Score: {stats[1]:.1f}")
        print(f"   ✅ Average RSS Score: {stats[2]:.1f}")
        print(f"   ✅ High Priority Contacts: {stats[3]}")
    else:
        print("   ⚠️  No analytics data yet (contacts not scored)")
    
    # Step 5: Check enrichment setup
    print("\n5️⃣  Checking Enrichment Setup...")
    
    perplexity_key = os.getenv('PERPLEXITY_API_KEY')
    if perplexity_key:
        print(f"   ✅ Perplexity API Key configured")
    else:
        print(f"   ⚠️  Perplexity API Key not set")
        print(f"      Add to .env: PERPLEXITY_API_KEY=your_key")
    
    # Check if enrichment directory exists
    if os.path.exists('intelligence/enrichment'):
        print(f"   ✅ Enrichment directory exists")
    else:
        print(f"   ⚠️  Enrichment directory missing")
        print(f"      Run: mkdir -p intelligence/enrichment")
    
    conn.close()
    
    # Final Summary
    print("\n" + "=" * 70)
    print("✅ System Connection Complete!")
    print("=" * 70)
    
    print("\n📊 Dashboard Status:")
    print(f"   • Total Contacts: {total}")
    print(f"   • Scored Contacts: {scored}")
    print(f"   • Ready for Dashboard: {'✅ Yes' if scored == total else '⚠️  Complete scoring first'}")
    
    print("\n🚀 Next Steps:")
    print("   1. Refresh your dashboard")
    print("   2. Check header metrics are populated")
    print("   3. Test scoring via API: curl -X POST http://localhost:8000/api/contacts/1/score")
    print("   4. For enrichment: Add PERPLEXITY_API_KEY to .env")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()
