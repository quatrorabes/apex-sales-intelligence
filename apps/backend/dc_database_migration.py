"""
Database Migration Script for APEX Intelligence Integration
Adds scoring and persona columns to contacts table
"""

import sqlite3
import os
from datetime import datetime

def migrate_database(db_path: str = "./apex.db"):
    """Add APEX Intelligence columns to contacts table"""
    
    print("🔄 Starting database migration...")
    print(f"Database: {db_path}")
    
    # Backup database first
    backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
    
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    # List of columns to add
    migrations = [
        ("persona_tier", "TEXT", "Persona tier classification (Tier 1 or Tier 2)"),
        ("persona_type", "TEXT", "Detailed persona type"),
        ("persona_confidence", "REAL", "Persona classification confidence score"),
        ("mdcp_score", "REAL", "Money, Decision, Credibility, Pain score"),
        ("mdcp_tier", "TEXT", "MDCP tier (HOT/WARM/QUALIFIED/COLD)"),
        ("rss_score", "REAL", "Relationship Strength Score"),
        ("rss_tier", "TEXT", "RSS tier (PLATINUM/GOLD/SILVER/BRONZE)"),
        ("priority_score", "REAL", "Combined priority score"),
        ("urgency_level", "TEXT", "Urgency level (IMMEDIATE/HIGH/MEDIUM/LOW)"),
        ("last_scored_at", "TEXT", "Timestamp of last scoring"),
        ("lifecycle_stage", "TEXT", "Contact lifecycle stage"),
        ("lead_type", "TEXT", "Lead type for MDCP weighting")
    ]
    
    added_count = 0
    skipped_count = 0
    
    for column_name, column_type, description in migrations:
        try:
            # Check if column already exists
            cursor.execute(f"PRAGMA table_info(contacts)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if column_name in columns:
                print(f"⏭️  Column '{column_name}' already exists - skipping")
                skipped_count += 1
                continue
            
            # Add the column
            cursor.execute(f"ALTER TABLE contacts ADD COLUMN {column_name} {column_type}")
            print(f"✅ Added column: {column_name} ({column_type}) - {description}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ Error adding column {column_name}: {e}")
    
    # Create index for better query performance
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_contacts_persona 
            ON contacts(persona_tier, persona_type)
        """)
        print("✅ Created index: idx_contacts_persona")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_contacts_scores 
            ON contacts(mdcp_score, rss_score, priority_score)
        """)
        print("✅ Created index: idx_contacts_scores")
        
    except Exception as e:
        print(f"⚠️  Index creation: {e}")
    
    db.commit()
    db.close()
    
    print(f"\n{'='*60}")
    print(f"✅ Migration complete!")
    print(f"   Added: {added_count} columns")
    print(f"   Skipped: {skipped_count} columns (already exist)")
    print(f"   Backup: {backup_path if os.path.exists(db_path) else 'N/A'}")
    print(f"{'='*60}")

def verify_migration(db_path: str = "./apex.db"):
    """Verify all columns were added successfully"""
    
    print("\n🔍 Verifying migration...")
    
    db = sqlite3.connect(db_path)
    cursor = db.cursor()
    
    cursor.execute("PRAGMA table_info(contacts)")
    columns = cursor.fetchall()
    
    expected_columns = [
        "persona_tier", "persona_type", "persona_confidence",
        "mdcp_score", "mdcp_tier", "rss_score", "rss_tier",
        "priority_score", "urgency_level", "last_scored_at",
        "lifecycle_stage", "lead_type"
    ]
    
    found_columns = [col[1] for col in columns]
    missing_columns = [col for col in expected_columns if col not in found_columns]
    
    if missing_columns:
        print(f"⚠️  Missing columns: {', '.join(missing_columns)}")
        return False
    else:
        print(f"✅ All {len(expected_columns)} APEX Intelligence columns present")
        
        # Show sample of table structure
        print("\n📋 Table structure:")
        for col in columns:
            if col[1] in expected_columns:
                print(f"   {col[1]:25} {col[2]:10}")
        
        return True

if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else "./apex.db"
    
    print("="*60)
    print("APEX INTELLIGENCE DATABASE MIGRATION")
    print("="*60)
    print()
    
    # Run migration
    migrate_database(db_path)
    
    # Verify
    verify_migration(db_path)
    
    print("\n✅ Database ready for APEX Intelligence!")
    print("\n📝 Next steps:")
    print("   1. Place intelligence engines in /intelligence/engines/enrichment/")
    print("   2. Update main.py with integration code")
    print("   3. Restart FastAPI server")
    print("   4. Test with: POST /api/contacts/{id}/deep-enrich")