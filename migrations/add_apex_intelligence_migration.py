# migrations/add_apex_intelligence.py
"""
Apex Intelligence Database Migration
Adds MDCP scoring, RSS scoring, lifecycle tracking, and priority scoring
Run with: python migrations/add_apex_intelligence.py
"""

import sqlite3
from datetime import datetime


def migrate_apex_intelligence(db_path='apex.db'):
    """Add Apex Intelligence tables and columns to existing database"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("[APEX INTELLIGENCE] Starting database migration...")
    print(f"  Database: {db_path}\n")
    
    # ============================================
    # 1. Add new columns to contacts table
    # ============================================
    
    print("  [1/7] Adding columns to contacts table...")
    
    new_columns = [
        ("lead_type", "TEXT DEFAULT 'BORROWER'"),
        ("lifecycle_stage", "TEXT DEFAULT 'NEW'"),
        ("stage_changed_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("stage_entered_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("institution_assets", "REAL"),
        ("annual_loan_volume", "REAL"),
        ("lifetime_deals_closed", "INTEGER"),
        ("available_capital", "REAL"),
        ("properties_owned", "INTEGER"),
        ("years_in_business", "INTEGER"),
        ("sba_loans_closed", "INTEGER"),
        ("successful_exits", "INTEGER"),
        ("loan_amount", "REAL"),
        ("equity_percent", "REAL"),
        ("property_type", "TEXT"),
        ("dscr_ratio", "REAL"),
        ("under_contract", "INTEGER DEFAULT 0"),
        ("days_to_close", "INTEGER"),
        ("deal_type", "TEXT"),
        ("num_lenders_contacted", "INTEGER"),
        ("previous_denials", "INTEGER"),
        ("touchpoints_count", "INTEGER DEFAULT 0"),
        ("days_since_last_contact", "INTEGER"),
        ("relationship_type", "TEXT DEFAULT 'PROFESSIONAL'"),
    ]
    
    added = 0
    for column_name, column_def in new_columns:
        try:
            cursor.execute(f"ALTER TABLE contacts ADD COLUMN {column_name} {column_def}")
            added += 1
        except sqlite3.OperationalError as e:
            if "duplicate column" not in str(e).lower():
                raise
    
    print(f"    ✓ Added {added} columns to contacts table")
    
    # ============================================
    # 2. Create lifecycle history table
    # ============================================
    
    print("  [2/7] Creating lead_lifecycle_history table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_lifecycle_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            previous_stage TEXT,
            new_stage TEXT NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            trigger_reason TEXT,
            days_in_previous_stage INTEGER,
            automated_trigger INTEGER DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_contact ON lead_lifecycle_history(contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_stage ON lead_lifecycle_history(new_stage)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_date ON lead_lifecycle_history(changed_at)")
    
    print("    ✓ Created lead_lifecycle_history table")
    
    # ============================================
    # 3. Create MDCP scores table
    # ============================================
    
    print("  [3/7] Creating mdcp_scores table...")
    
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
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            calculation_version TEXT DEFAULT '1.0',
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mdcp_contact ON mdcp_scores(contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mdcp_score ON mdcp_scores(mdcp_total DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mdcp_tier ON mdcp_scores(mdcp_tier)")
    
    print("    ✓ Created mdcp_scores table")
    
    # ============================================
    # 4. Create RSS scores table
    # ============================================
    
    print("  [4/7] Creating rss_scores table...")
    
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
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    
    print("  [5/7] Creating priority_scores table...")
    
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
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority_contact ON priority_scores(contact_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority_score ON priority_scores(priority_score DESC)")
    
    print("    ✓ Created priority_scores table")
    
    # ============================================
    # 6. Create touchpoints table
    # ============================================
    
    print("  [6/7] Creating touchpoints table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS touchpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            touchpoint_type TEXT NOT NULL,
            touchpoint_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    
    print("  [7/7] Creating apex_metadata table...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apex_metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        INSERT OR REPLACE INTO apex_metadata (key, value) VALUES
            ('apex_intelligence_version', '1.0'),
            ('schema_version', '1.0'),
            ('installed_at', ?),
            ('last_calculation', NULL),
            ('total_contacts_scored', '0')
    """, (datetime.now().isoformat(),))
    
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
    print("   • Columns added: 24")
    print("   • Indexes created: 9")
    print("\n   Next steps:")
    print("   1. Set lead_type for your contacts (BANKER, CDC, BROKER, PRIVATE_LENDER, BORROWER)")
    print("   2. Run: python -m apps.backend.intelligence.apex_scoring_engine")
    print("   3. Check scoring results in database tables: mdcp_scores, rss_scores, priority_scores")


if __name__ == '__main__':
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'apex.db'
    migrate_apex_intelligence(db_path)
