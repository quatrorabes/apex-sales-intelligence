"""
Why Me? Helper - Provides user preferences for content generation
"""
import sqlite3
import json
import os

DB_PATH = os.getenv('DB_PATH', '/Users/chrisrabenold/projects/apex/apex.db')

def get_user_preferences(user_id: str = 'default_user') -> dict:
    """Get user preferences from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            def safe_json(val, default='[]'):
                if not val:
                    return json.loads(default)
                try:
                    return json.loads(val)
                except:
                    return json.loads(default)
            
            return {
                'products': safe_json(row['products']),
                'services': safe_json(row['services']),
                'value_propositions': safe_json(row['value_propositions']),
                'target_customers': safe_json(row['target_customers']),
                'personal_differentiators': safe_json(row['personal_differentiators']),
                'company_differentiators': safe_json(row['company_differentiators']),
            }
    except Exception as e:
        print(f"Error loading preferences: {e}")
    
    # Return defaults if no preferences found
    return {
        'products': ['SBA 504 Loans', 'SBA 7a Loans', 'Commercial Real Estate Financing'],
        'services': ['Fast closing', 'Flexible underwriting', 'Competitive rates'],
        'value_propositions': ['Certainty of close', '25+ years experience', 'Personalized service'],
        'target_customers': ['Commercial real estate investors', 'Business owners', 'Entrepreneurs'],
        'personal_differentiators': ['Deep industry expertise', 'Relationship-focused approach'],
        'company_differentiators': ['Direct lender', 'In-house underwriting', 'Quick decisions'],
    }

def format_business_context(preferences: dict) -> str:
    """Format preferences into a context string for AI prompts"""
    parts = []
    
    if preferences.get('products'):
        parts.append(f"Products/Services: {', '.join(preferences['products'][:3])}")
    
    if preferences.get('value_propositions'):
        parts.append(f"Value Props: {', '.join(preferences['value_propositions'][:3])}")
    
    if preferences.get('personal_differentiators'):
        parts.append(f"Differentiators: {', '.join(preferences['personal_differentiators'][:2])}")
    
    return '. '.join(parts) if parts else "Commercial real estate financing specialist"

def get_whyme_context(user_id: str = 'default_user') -> str:
    """Get formatted Why Me context for content generation"""
    prefs = get_user_preferences(user_id)
    return format_business_context(prefs)
