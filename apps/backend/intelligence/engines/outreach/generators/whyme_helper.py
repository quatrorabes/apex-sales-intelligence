#!/usr/bin/env python3
"""
Why Me? Helper - Shared utility for loading user preferences
Used by: email_generator, call_script_generator, generate_content, linkedin_automation
"""

import json
import sqlite3

DB_PATH = '/Users/chrisrabenold/projects/apex/apex.db'

def get_user_preferences():
    """Load Why Me? preferences - shared across all generators"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        row = conn.execute("""
            SELECT products, services, value_propositions, 
                   target_customers, personal_differentiators, 
                   company_differentiators
            FROM user_preferences 
            WHERE user_id = 'default_user'
        """).fetchone()
    except Exception as e:
        print(f"⚠️  Could not load preferences: {e}")
        return None
    finally:
        conn.close()
    
    if not row:
        return {
            'products': [],
            'services': [],
            'value_propositions': [],
            'target_customers': [],
            'personal_differentiators': [],
            'company_differentiators': []
        }
    
    return {
        'products': json.loads(row['products'] or '[]'),
        'services': json.loads(row['services'] or '[]'),
        'value_propositions': json.loads(row['value_propositions'] or '[]'),
        'target_customers': json.loads(row['target_customers'] or '[]'),
        'personal_differentiators': json.loads(row['personal_differentiators'] or '[]'),
        'company_differentiators': json.loads(row['company_differentiators'] or '[]')
    }

def format_business_context():
    """Format user preferences for AI prompts"""
    prefs = get_user_preferences()
    
    if not prefs:
        return "\nYOUR BUSINESS: Not configured (use Why Me? tab)\n"
    
    return f"""
YOUR BUSINESS (from Why Me? preferences):
- Products: {', '.join(prefs['products'][:3]) if prefs['products'] else 'Not specified'}
- Services: {', '.join(prefs['services'][:3]) if prefs['services'] else 'Not specified'}
- Value Props: {'. '.join(prefs['value_propositions'][:3]) if prefs['value_propositions'] else 'Not specified'}
- Target Customers: {', '.join(prefs['target_customers'][:2]) if prefs['target_customers'] else 'Not specified'}
- Your Differentiators: {'. '.join(prefs['personal_differentiators'][:2]) if prefs['personal_differentiators'] else 'Not specified'}
"""

if __name__ == '__main__':
    # Test
    print("Testing whyme_helper...")
    prefs = get_user_preferences()
    
    if prefs:
        print(f"✅ Loaded {len(prefs['products'])} products")
        print(f"✅ Loaded {len(prefs['services'])} services")
        print(f"✅ Loaded {len(prefs['value_propositions'])} value propositions")
        print("\n" + format_business_context())
    else:
        print("❌ No preferences found")
