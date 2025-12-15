#!/usr/bin/env python3
'''
Database Migration: Add missing columns for Perplexity enrichment
'''

import sqlite3

def add_enrichment_columns():
    '''Add missing columns to contacts table'''

    conn = sqlite3.connect('./apex.db')
    cursor = conn.cursor()

    # Get existing columns
    cursor.execute("PRAGMA table_info(contacts)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    print(f"Existing columns: {existing_columns}")

    # Define columns to add if they don't exist
    columns_to_add = [
        ('talking_points', 'TEXT'),
        ('myers_briggs', 'VARCHAR(10)'),
        ('pain_points', 'TEXT'),
        ('enrichment_data', 'TEXT'),
        ('enrichment_status', 'VARCHAR(50)'),
        ('enriched_at', 'TIMESTAMP'),
    ]

    # Add each column if it doesn't exist
    for column_name, column_type in columns_to_add:
        if column_name not in existing_columns:
            try:
                alter_query = f"ALTER TABLE contacts ADD COLUMN {column_name} {column_type}"
                cursor.execute(alter_query)
                conn.commit()
                print(f"✅ Added column: {column_name} ({column_type})")
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    print(f"❌ Error adding {column_name}: {e}")
        else:
            print(f"⏭️  Column already exists: {column_name}")

    conn.close()
    print("\n✅ Database migration complete!")

if __name__ == "__main__":
    add_enrichment_columns()
