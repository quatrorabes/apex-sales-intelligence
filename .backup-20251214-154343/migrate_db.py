#!/usr/bin/env python3
"""
Database Migration Script
Migrates existing apex.db to new schema with enrichment tracking
"""

import sqlite3
import os
from datetime import datetime

DATABASE = './apex.db'
BACKUP_DB = f'./apex_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

def backup_database():
    """Create backup of existing database"""
    if os.path.exists(DATABASE):
        import shutil
        shutil.copy2(DATABASE, BACKUP_DB)
        print(f"✅ Database backed up to: {BACKUP_DB}")
        return True
    return False

def migrate_database():
    """Migrate database to new schema"""
    print("\n" + "="*70)
    print("🔄 APEX DATABASE MIGRATION")
    print("="*70 + "\n")
    
    # Backup existing database
    if backup_database():
        print("📦 Existing database backed up")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if contacts table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='contacts'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            print("📋 Checking existing schema...")
            
            # Get existing columns
            cursor.execute("PRAGMA table_info(contacts)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            print(f"   Found {len(existing_columns)} existing columns")
            
            # Define new columns to add
            new_columns = {
                'first_name': 'TEXT',
                'last_name': 'TEXT',
                'industry': 'TEXT',
                'mobile_phone': 'TEXT',
                'linkedin_url': 'TEXT',
                'lifecycle_stage': 'TEXT',
                'lead_status': 'TEXT',
                'hubspot_owner_id': 'TEXT',
                'enrichment_status': "TEXT DEFAULT 'pending'",
                'enriched_at': 'TIMESTAMP',
                'enrichment_data': 'TEXT',
                'tier': 'INTEGER',
                'persona_name': 'TEXT',
                'personality_type': 'TEXT',
                'disc_profile': 'TEXT',
                'opportunity_score': 'REAL',
                'urgency_level': 'TEXT',
                'lead_tier': 'TEXT',
                'relationship_data': 'TEXT',
                'vertical_intelligence': 'TEXT',
                'pain_points': 'TEXT',
                'email_variant_1': 'TEXT',
                'email_variant_2': 'TEXT',
                'email_variant_3': 'TEXT',
                'call_script_1': 'TEXT',
                'call_script_2': 'TEXT',
                'call_script_3': 'TEXT',
                'last_contacted': 'TIMESTAMP',
                'outreach_stage': 'TEXT',
                'conversion_probability': 'REAL',
                'imported_at': 'TIMESTAMP',
                'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'
            }
            
            # Add missing columns
            print("\n🔧 Adding new columns...")
            added_count = 0
            for col_name, col_type in new_columns.items():
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE contacts ADD COLUMN {col_name} {col_type}")
                        print(f"   ✅ Added: {col_name}")
                        added_count += 1
                    except sqlite3.OperationalError as e:
                        print(f"   ⚠️  Column {col_name} already exists or error: {e}")
            
            print(f"\n✅ Added {added_count} new columns")
            
            # Create indexes
            print("\n📊 Creating indexes...")
            indexes = [
                ("idx_email", "email"),
                ("idx_hubspot_id", "hubspot_id"),
                ("idx_enrichment_status", "enrichment_status"),
                ("idx_lifecycle_stage", "lifecycle_stage")
            ]
            
            for idx_name, idx_column in indexes:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON contacts({idx_column})")
                    print(f"   ✅ Created index: {idx_name}")
                except sqlite3.OperationalError as e:
                    print(f"   ℹ️  Index {idx_name} already exists")
            
            # Update existing records with default enrichment_status
            cursor.execute("""
                UPDATE contacts 
                SET enrichment_status = 'pending' 
                WHERE enrichment_status IS NULL
            """)
            updated_rows = cursor.rowcount
            print(f"\n✅ Updated {updated_rows} existing contacts with default status")
            
        else:
            print("📋 No existing contacts table found, creating new schema...")
            create_fresh_schema(cursor)
        
        # Create other tables
        print("\n📋 Creating additional tables...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                content TEXT,
                sent_at TIMESTAMP,
                response TEXT,
                success BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
        """)
        print("   ✅ outreach_history table ready")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                metric_type TEXT,
                metric_value REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
        """)
        print("   ✅ analytics table ready")
        
        conn.commit()
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        cursor.execute("PRAGMA table_info(contacts)")
        final_columns = [row[1] for row in cursor.fetchall()]
        print(f"   ✅ Contacts table now has {len(final_columns)} columns")
        
        cursor.execute("SELECT COUNT(*) FROM contacts")
        contact_count = cursor.fetchone()[0]
        print(f"   ✅ Preserved {contact_count} existing contacts")
        
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        print(f"💾 Backup saved to: {BACKUP_DB}")
        print(f"📊 Database ready with {contact_count} contacts")
        print("\n🚀 You can now run: python main.py\n")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"💾 Your original database is backed up at: {BACKUP_DB}")
        conn.rollback()
        raise
    finally:
        conn.close()

def create_fresh_schema(cursor):
    """Create fresh database schema"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hubspot_id TEXT UNIQUE,
            
            -- Basic Info
            name TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            title TEXT,
            company TEXT,
            industry TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            mobile_phone TEXT,
            linkedin_url TEXT,
            
            -- HubSpot Metadata
            lifecycle_stage TEXT,
            lead_status TEXT,
            hubspot_owner_id TEXT,
            
            -- Enrichment Status
            enrichment_status TEXT DEFAULT 'pending',
            enriched_at TIMESTAMP,
            enrichment_data TEXT,
            
            -- AI Intelligence
            tier INTEGER,
            persona_name TEXT,
            personality_type TEXT,
            disc_profile TEXT,
            opportunity_score REAL,
            urgency_level TEXT,
            lead_tier TEXT,
            
            -- Advanced Data
            relationship_data TEXT,
            vertical_intelligence TEXT,
            pain_points TEXT,
            
            -- Outreach Content
            email_variant_1 TEXT,
            email_variant_2 TEXT,
            email_variant_3 TEXT,
            call_script_1 TEXT,
            call_script_2 TEXT,
            call_script_3 TEXT,
            
            -- Tracking
            last_contacted TIMESTAMP,
            outreach_stage TEXT,
            conversion_probability REAL,
            
            -- Timestamps
            imported_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ Created contacts table with full schema")

if __name__ == "__main__":
    migrate_database()
