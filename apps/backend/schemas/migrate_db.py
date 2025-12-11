"""
Database migration script - Clean slate for APEX v1.0
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'apex.db')
BACKUP_PATH = f"{DB_PATH}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def migrate():
    # Backup existing
    if os.path.exists(DB_PATH):
        import shutil
        shutil.copy(DB_PATH, BACKUP_PATH)
        print(f"✅ Backed up to {BACKUP_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Drop old tables (clean slate)
    cursor.execute("DROP TABLE IF EXISTS contacts")
    cursor.execute("DROP TABLE IF EXISTS enrichments")
    
    # Create new schema
    cursor.execute("""
        CREATE TABLE contacts (
            id TEXT PRIMARY KEY,
            hubspot_id TEXT UNIQUE,
            salesforce_id TEXT UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            title TEXT,
            company TEXT,
            enrichment JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            enriched_at TIMESTAMP
        )
    """)
    
    # Indexes
    cursor.execute("CREATE INDEX idx_contacts_company ON contacts(company)")
    cursor.execute("CREATE INDEX idx_contacts_email ON contacts(email)")
    cursor.execute("CREATE INDEX idx_contacts_hubspot ON contacts(hubspot_id)")
    cursor.execute("CREATE INDEX idx_contacts_enriched ON contacts(enriched_at)")
    
    conn.commit()
    conn.close()
    
    print("✅ Database migrated to v1.0 schema!")
    print("   - Old data backed up")
    print("   - New contacts table created")
    print("   - Ready for fresh enrichment")

if __name__ == "__main__":
    migrate()
