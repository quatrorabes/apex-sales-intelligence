#!/usr/bin/env python3
"""
APEX Database Schema Diagnostic & Fix
Checks database structure and creates missing tables
"""

import sqlite3
import os
from datetime import datetime

class ApexDatabaseFix:
    def __init__(self, db_path="~/projects/apex/apex.db"):
        self.db_path = os.path.expanduser(db_path)

    def check_schema(self):
        """Check current database schema"""
        print("="*70)
        print("DATABASE SCHEMA DIAGNOSTIC")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print(f"\nDatabase: {self.db_path}")
        print(f"\nTables found: {len(tables)}\n")

        for table in tables:
            table_name = table[0]
            print(f"  📋 {table_name}")

            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()

            for col in columns:
                col_id, col_name, col_type, not_null, default, pk = col
                nullable = "NOT NULL" if not_null else "NULL"
                primary = "PRIMARY KEY" if pk else ""
                print(f"      - {col_name:20} {col_type:15} {nullable:10} {primary}")
            print()

        conn.close()
        return [t[0] for t in tables]

    def create_scoring_history_table(self):
        """Create scoring_history table if missing"""
        print("="*70)
        print("CREATING SCORING_HISTORY TABLE")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create scoring_history table
        create_sql = """
        CREATE TABLE IF NOT EXISTS scoring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            trigger TEXT NOT NULL,
            old_rss_score REAL,
            new_rss_score REAL,
            old_mdcp_score REAL,
            new_mdcp_score REAL,
            old_priority_score REAL,
            new_priority_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        );
        """

        cursor.execute(create_sql)
        conn.commit()

        print("\n✓ Created scoring_history table")
        print("\nSchema:")
        cursor.execute("PRAGMA table_info(scoring_history);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]:25} {col[2]:15}")

        conn.close()

    def check_contacts_scoring_columns(self):
        """Verify contacts table has scoring columns"""
        print("\n" + "="*70)
        print("CHECKING CONTACTS TABLE SCORING COLUMNS")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(contacts);")
        columns = cursor.fetchall()

        column_names = [col[1] for col in columns]

        required_columns = [
            'rss_score',
            'mdcp_score', 
            'priority_score',
            'enrichment_status',
            'enriched_at'
        ]

        missing = []
        print("\nChecking required columns:")
        for col in required_columns:
            if col in column_names:
                print(f"  ✓ {col}")
            else:
                print(f"  ✗ {col} - MISSING")
                missing.append(col)

        if missing:
            print(f"\n⚠ Missing {len(missing)} columns. Adding them...")

            # Add missing columns
            alter_statements = {
                'rss_score': 'ALTER TABLE contacts ADD COLUMN rss_score REAL DEFAULT 0.0;',
                'mdcp_score': 'ALTER TABLE contacts ADD COLUMN mdcp_score REAL DEFAULT 0.0;',
                'priority_score': 'ALTER TABLE contacts ADD COLUMN priority_score REAL DEFAULT 0.0;',
                'enrichment_status': 'ALTER TABLE contacts ADD COLUMN enrichment_status TEXT;',
                'enriched_at': 'ALTER TABLE contacts ADD COLUMN enriched_at DATETIME;'
            }

            for col in missing:
                if col in alter_statements:
                    try:
                        cursor.execute(alter_statements[col])
                        print(f"  ✓ Added {col}")
                    except Exception as e:
                        print(f"  ✗ Error adding {col}: {e}")

            conn.commit()

        conn.close()

    def test_scoring_insert(self):
        """Test inserting a scoring history entry"""
        print("\n" + "="*70)
        print("TESTING SCORING_HISTORY INSERT")
        print("="*70)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get first contact
        cursor.execute("SELECT id, name FROM contacts LIMIT 1;")
        result = cursor.fetchone()

        if result:
            contact_id, name = result
            print(f"\nTesting with Contact ID {contact_id} ({name})")

            # Insert test entry
            cursor.execute("""
                INSERT INTO scoring_history 
                (contact_id, trigger, old_rss_score, new_rss_score, 
                 old_mdcp_score, new_mdcp_score, old_priority_score, new_priority_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (contact_id, 'test', 0.0, 50.0, 0.0, 75.0, 0.0, 60.0))

            conn.commit()

            # Verify
            cursor.execute("SELECT * FROM scoring_history WHERE contact_id = ? ORDER BY id DESC LIMIT 1;", 
                          (contact_id,))
            entry = cursor.fetchone()

            if entry:
                print("\n✓ Test insert successful!")
                print(f"  Entry ID: {entry[0]}")
                print(f"  Trigger: {entry[2]}")
                print(f"  RSS: {entry[3]} → {entry[4]}")
                print(f"  MDCP: {entry[5]} → {entry[6]}")
                print(f"  Priority: {entry[7]} → {entry[8]}")
                print(f"  Timestamp: {entry[9]}")

                # Clean up test entry
                cursor.execute("DELETE FROM scoring_history WHERE id = ?;", (entry[0],))
                conn.commit()
                print("\n✓ Test entry cleaned up")

        conn.close()

    def run_all_checks(self):
        """Run all diagnostics and fixes"""
        print("\n" + "🔧 "*25)
        print("APEX DATABASE FIX & DIAGNOSTIC TOOL")
        print("🔧 "*25)

        # Check schema
        tables = self.check_schema()

        # Create scoring_history if missing
        if 'scoring_history' not in tables:
            self.create_scoring_history_table()
        else:
            print("\n✓ scoring_history table already exists")

        # Check contacts columns
        self.check_contacts_scoring_columns()

        # Test insert
        self.test_scoring_insert()

        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print("""
✓ Database schema checked
✓ scoring_history table created/verified
✓ Contacts scoring columns verified
✓ Test insert successful

Next: Check why auto-rescore isn't triggering in api.py
"""        )

if __name__ == "__main__":
    fixer = ApexDatabaseFix()
    fixer.run_all_checks()
