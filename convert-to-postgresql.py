#!/usr/bin/env python3
"""
Convert SQLite api.py to PostgreSQL api.py
"""

import re
import sys

def convert_sqlite_to_postgresql(content):
    """Convert SQLite syntax to PostgreSQL"""
    
    # 1. Replace sqlite3 import with psycopg2
    content = content.replace('import sqlite3', 'import psycopg2\nfrom psycopg2.extras import RealDictCursor')
    
    # 2. Replace DATABASE constant
    content = re.sub(
        r"DATABASE\s*=\s*['\"].*?apex\.db['\"]",
        "DATABASE_URL = os.environ.get('DATABASE_URL')",
        content
    )
    
    # 3. Replace get_db() function
    old_getdb = r"""def get_db\(\):
    conn = sqlite3\.connect\(DATABASE\)
    conn\.row_factory = sqlite3\.Row
    return conn"""
    
    new_getdb = """def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = RealDictCursor
    return conn"""
    
    content = re.sub(old_getdb, new_getdb, content, flags=re.DOTALL)
    
    # 4. Replace ? placeholders with %s
    # This is the critical one - match SQL queries
    def replace_placeholders(match):
        query = match.group(0)
        # Count the number of ? in the query
        count = query.count('?')
        if count > 0:
            # Replace ? with %s
            return query.replace('?', '%s')
        return query
    
    # Match SQL queries (rough pattern)
    content = re.sub(
        r'(cursor\.execute\(["\'].*?["\'].*?\))',
        replace_placeholders,
        content,
        flags=re.DOTALL
    )
    
    # 5. Fix dict() calls - RealDictCursor returns dicts directly
    # Replace dict(row) with just row (where row is from cursor.fetchone/fetchall)
    content = re.sub(
        r'dict\(row\)',
        'row',
        content
    )
    
    # 6. Replace cursor.lastrowid with RETURNING id pattern
    # This is more complex - need to handle case by case
    
    # 7. Fix INTEGER PRIMARY KEY AUTOINCREMENT → SERIAL
    content = content.replace(
        'INTEGER PRIMARY KEY AUTOINCREMENT',
        'SERIAL PRIMARY KEY'
    )
    
    # 8. Fix date('now') → NOW() or CURRENT_DATE
    content = content.replace("date('now')", "CURRENT_DATE")
    content = content.replace("datetime('now')", "NOW()")
    
    # 9. Fix NULLS LAST syntax (PostgreSQL supports this)
    # Already correct
    
    return content

def main():
    # Read api.py
    with open('api.py', 'r') as f:
        content = f.read()
    
    print("🔄 Converting SQLite → PostgreSQL...")
    
    converted = convert_sqlite_to_postgresql(content)
    
    # Write back
    with open('api.py', 'w') as f:
        f.write(converted)
    
    print("✅ Conversion complete!")
    print("📊 Changes made:")
    print("   - sqlite3 → psycopg2")
    print("   - ? → %s placeholders")
    print("   - DATABASE path → DATABASE_URL")
    print("   - get_db() function updated")
    print("   - dict(row) → row (RealDictCursor)")

if __name__ == '__main__':
    main()
