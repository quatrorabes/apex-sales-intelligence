#!/usr/bin/env python3
"""
Fix user_preferences table schema for Why Me? tab
Adds missing columns without destroying existing data
"""

import sqlite3
import sys

DATABASE = '/Users/chrisrabenold/projects/apex/apex.db'

def fix_schema():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute("PRAGMA table_info(user_preferences)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    
    print(f"📊 Current columns: {existing_cols}")
    
    # Define required Why Me? columns
    required_columns = [
        ('products', 'TEXT DEFAULT "[]"'),
        ('services', 'TEXT DEFAULT "[]"'),
        ('value_propositions', 'TEXT DEFAULT "[]"'),
        ('target_customers', 'TEXT DEFAULT "[]"'),
        ('personal_differentiators', 'TEXT DEFAULT "[]"'),
        ('company_differentiators', 'TEXT DEFAULT "[]"'),
    ]
    
    added = 0
    for col_name, col_type in required_columns:
        if col_name not in existing_cols:
            try:
                cursor.execute(f'ALTER TABLE user_preferences ADD COLUMN {col_name} {col_type}')
                print(f"✅ Added column: {col_name}")
                added += 1
            except sqlite3.OperationalError as e:
                print(f"⚠️ Could not add {col_name}: {e}")
        else:
            print(f"⏭️ Column already exists: {col_name}")
    
    # Ensure default_user exists
    cursor.execute("""
        INSERT OR IGNORE INTO user_preferences (user_id) 
        VALUES ('default_user')
    """)
    
    conn.commit()
    
    # Verify final schema
    cursor.execute("PRAGMA table_info(user_preferences)")
    final_cols = [row[1] for row in cursor.fetchall()]
    
    print(f"\n📋 Final schema ({len(final_cols)} columns):")
    for col in final_cols:
        print(f"  - {col}")
    
    conn.close()
    
    print(f"\n✅ Schema fix complete! Added {added} columns.")
    return 0

if __name__ == '__main__':
    sys.exit(fix_schema())
