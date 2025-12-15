"""
Apex Intelligence Migration - Fixed for SQLite constraints
"""

import sqlite3
from datetime import datetime

def migrate_apex_intelligence_fixed(db_path='apex.db'):
    """Add Apex Intelligence to existing database - SQLite compatible"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("[APEX INTELLIGENCE] Starting migration...")
    print(f"  Database: {db_path}\n")
    
    # ============================================
    # 1. Add columns to contacts table
    # ============================================
    
    print("  [1/7] Adding columns to contacts table...")
    
    new_columns = [
        # Core fields
        ("lead_type", "TEXT DEFAULT 'BORROWER'"),
        ("lifecycle_stage", "TEXT DEFAULT 'NEW'"),
        ("stage_changed_at", "TIMESTAMP"),  # No DEFAULT CURRENT_TIMESTAMP
        ("stage_entered_at", "TIMESTAMP"),  # No DEFAULT CURRENT_TIMESTAMP
        
        # Type-specific fields
        ("institution_assets", "REAL"),
        ("annual_loan_volume", "REAL"),
        ("lifetime_deals_closed", "INTEGER"),
        ("available_capital", "REAL"),
        ("properties_owned", "INTEGER"),
        ("years_in_business", "INTEGER"),
        ("sba_loans_closed", "INTEGER"),
        ("successful_exits", "INTEGER"),
        
        # Deal fields
        ("loan_amount", "REAL"),
        ("equity_percent", "REAL"),
        ("property_type", "TEXT"),
        ("dscr_ratio", "REAL"),
        ("under_contract", "INTEGER DEFAULT 0"),
        ("days_to_close", "INTEGER"),
        ("deal_type", "TEXT"),
        ("num_lenders_contacted", "INTEGER"),
        ("previous_denials", "INTEGER"),
        
        # Engagement tracking
        ("touchpoints_count", "INTEGER DEFAULT 0"),
        ("days_since_last_contact", "INTEGER"),
        ("relationship_type", "TEXT DEFAULT 'PROFESSIONAL'"),
        
        # Deal tracking
        ("total_deals_referred", "INTEGER DEFAULT 0"),
        ("total_deals_closed", "INTEGER DEFAULT 0"),
        ("total_deals_funded_amount", "REAL DEFAULT 0"),
    ]
    
    added = 0
    skipped = 0
    for column_name, column_def in new_columns:
        try:
            cursor.execute(f"ALTER TABLE contacts ADD COLUMN {column_name} {column_def}")
            added += 1
            print(f"    ✓ Added: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                skipped += 1
            else:
                print(f"    ✗ Error adding {column_name}: {e}")
    
    print(f"    → Added {added} columns, skipped {skipped} existing")
    
    # Set timestamps for existing records
    cursor.execute("""
        UPDATE contacts 
        SET stage_changed_at = datetime('now'),
            stage_entered_at = datetime('now')
        WHERE stage_changed_at IS NULL
    """)
    
    # ============================================
    # 2. Create lifecycle history table
    # ============================================
    
    print("\n  [2/7] Creating lead_lifecycle_history table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_lifecycle_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            previous_stage TEXT,
            new_stage TEXT NOT NULL,
            changed_at TIMESTAMP,
            trigger_reason TEXT,
            days_in_previous_stage INTEGER,
            automated_trigger INTEGER DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_contact ON lead_lifecycle_history(contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_stage ON lead_lifecycle_history(new_stage)")
    
    print("    ✓ Created lead_lifecycle_history table")
    
    # ============================================
    # 3. Create MDCP scores table
    # ============================================
    
    print("\n  [3/7] Creating mdcp_scores table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mdcp_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            lead_type TEXT NOT NULL,
            lifecycle_stage TEXT NOT NULL,
            mdcp_total REAL NOT NULL,
            money_score REAL,
            decision_score REAL,
            credibility_score REAL,
            pain_score REAL,
            money_weight REAL,
            decision_weight REAL,
            credibility_weight REAL,
            pain_weight REAL,
            mdcp_tier TEXT,
            calculated_at TIMESTAMP,
            calculation_version TEXT DEFAULT '1.0',
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mdcp_contact ON mdcp_scores(contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mdcp_score ON mdcp_scores(mdcp_total DESC)")
    
    print("    ✓ Created mdcp_scores table")
    
    # ============================================
    # 4. Create RSS scores table
    # ============================================
    
    print("\n  [4/7] Creating rss_scores table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rss_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            rss_total REAL NOT NULL,
            familiarity_score REAL,
            engagement_score REAL,
            productivity_score REAL,
            rss_tier TEXT,
            years_known REAL,
            touchpoints_last_12mo INTEGER,
            deals_closed_together INTEGER,
            close_rate_pct REAL,
            total_funded_amount REAL,
            lifecycle_stage TEXT,
            can_calculate_full_rss INTEGER DEFAULT 0,
            calculated_at TIMESTAMP,
            calculation_version TEXT DEFAULT '1.0',
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rss_contact ON rss_scores(contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_rss_score ON rss_scores(rss_total DESC)")
    
    print("    ✓ Created rss_scores table")
    
    # ============================================
    # 5. Create priority scores table
    # ============================================
    
    print("\n  [5/7] Creating priority_scores table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS priority_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            mdcp_score REAL NOT NULL,
            rss_score REAL,
            priority_score REAL NOT NULL,
            lead_type TEXT,
            lifecycle_stage TEXT,
            recommended_action TEXT,
            urgency_level TEXT,
            calculated_at TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority_contact ON priority_scores(contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority_score ON priority_scores(priority_score DESC)")
    
    print("    ✓ Created priority_scores table")
    
    # ============================================
    # 6. Create touchpoints table
    # ============================================
    
    print("\n  [6/7] Creating touchpoints table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS touchpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            touchpoint_type TEXT NOT NULL,
            touchpoint_date TIMESTAMP,
            duration_minutes INTEGER,
            outcome TEXT,
            quality_score INTEGER,
            strategic_discussion INTEGER DEFAULT 0,
            subject TEXT,
            notes TEXT,
            crm_activity_id TEXT,
            imported_from TEXT,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_touchpoint_contact ON touchpoints(contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_touchpoint_date ON touchpoints(touchpoint_date DESC)")
    
    print("    ✓ Created touchpoints table")
    
    # ============================================
    # 7. Create metadata table
    # ============================================
    
    print("\n  [7/7] Creating apex_metadata table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apex_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP
        )
    """)
    
    # Insert metadata
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO apex_metadata (key, value, updated_at) VALUES
            ('apex_intelligence_version', '1.0', ?),
            ('schema_version', '1.0', ?),
            ('installed_at', ?, ?),
            ('last_calculation', NULL, ?),
            ('total_contacts_scored', '0', ?)
    """, (now, now, now, now, now, now))
    
    print("    ✓ Created apex_metadata table")
    
    # ============================================
    # Commit changes
    # ============================================
    
    conn.commit()
    conn.close()
    
    print("\n✅ [APEX INTELLIGENCE] Migration completed successfully!")
    print("\n   Summary:")
    print("   • Database: apex.db")
    print("   • Tables created: 6")
    print(f"   • Columns added: {added}")
    print(f"   • Columns skipped: {skipped}")
    print("\n   Next steps:")
    print("   1. Copy Apex Intelligence files to apps/backend/intelligence/")
    print("   2. Set lead_type for your contacts")
    print("   3. Run: python -m apps.backend.intelligence.apex_scoring_engine")

if __name__ == '__main__':
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'apex.db'
    migrate_apex_intelligence_fixed(db_path)
