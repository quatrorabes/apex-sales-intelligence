"""
Complete scoring wrapper with all required functions
"""
import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def score_contact_from_db(conn, contact_id: int, trigger: str = 'manual', user_id: str = None):
    """Score a contact with CRE-specific logic"""
    
    if not user_id:
        user_id = os.getenv('CURRENT_USER_ID', 'default')
    
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
    row = cursor.fetchone()
    
    if not row:
        return {'error': 'Contact not found'}
    
    columns = [desc[0] for desc in cursor.description]
    contact = dict(zip(columns, row))
    
    # Import and use CRE scoring engine
    try:
        from user_scoring_engine import UserSpecificScoringEngine
        user_engine = UserSpecificScoringEngine(user_id)
        rss_result = user_engine.calculate_personalized_rss(contact)
        rss_score = rss_result['total']
        print(f"DEBUG: CRE RSS Score: {rss_score} for {contact.get('name')}")
    except Exception as e:
        print(f"ERROR in scoring: {e}")
        # Fallback - but with CRE logic
        title = (contact.get('title') or '').lower()
        
        # CRE-specific fallback
        if any(word in title for word in ['broker', 'commercial', 'real estate', 'leasing']):
            rss_score = 75
        elif any(word in title for word in ['vp', 'director', 'principal']):
            rss_score = 70
        elif any(word in title for word in ['hr', 'marketing', 'it', 'legal']):
            rss_score = 15  # Very low for non-targets
        else:
            rss_score = 40
    
    # MDCP calculation (simpler)
    mdcp_score = 40.0  # Start lower
    if contact.get('company'):
        mdcp_score += 15
    if contact.get('email'):
        mdcp_score += 15
    if contact.get('phone'):
        mdcp_score += 10
    if contact.get('linkedin_url'):
        mdcp_score += 10
    
    # Priority calculation - RSS matters more for CRE
    priority_score = (mdcp_score * 0.3) + (rss_score * 0.7)  # 70% weight on role
    
    # Urgency levels
    if priority_score >= 80:
        urgency = 'IMMEDIATE'
        tier = 'HOT'
    elif priority_score >= 65:
        urgency = 'HIGH'
        tier = 'WARM'
    elif priority_score >= 50:
        urgency = 'MEDIUM'
        tier = 'QUALIFIED'
    else:
        urgency = 'LOW'
        tier = 'COLD'
    
    print(f"  Final scores - MDCP: {mdcp_score}, RSS: {rss_score}, Priority: {priority_score}")
    
    # UPDATE DATABASE
    try:
        cursor.execute('''
            UPDATE contacts
            SET mdcp_score = ?, 
                mdcp_tier = ?, 
                rss_score = ?, 
                rss_tier = ?,
                priority_score = ?, 
                urgency_level = ?,
                recommended_action = ?,
                last_scored = ?
            WHERE id = ?
        ''', (
            mdcp_score, tier, rss_score, tier, priority_score, urgency,
            f'{urgency} priority contact',
            datetime.now().isoformat(),
            contact_id
        ))
        
        conn.commit()
        print(f"  ✅ Saved to database")
        
    except Exception as e:
        print(f"ERROR saving to database: {e}")
        conn.rollback()
    
    return {
        'success': True,
        'contact_id': contact_id,
        'scores': {
            'mdcp_score': mdcp_score,
            'rss_score': rss_score,
            'priority_score': priority_score,
            'urgency_level': urgency
        }
    }

def bulk_score_contacts(conn, contact_ids, trigger='batch'):
    """Bulk score multiple contacts"""
    results = []
    for cid in contact_ids:
        try:
            result = score_contact_from_db(conn, cid, trigger)
            results.append(result)
        except Exception as e:
            print(f"Error scoring {cid}: {e}")
            results.append({'contact_id': cid, 'error': str(e)})
    return results

def get_apex_scores(conn):
    """Get all scored contacts for display"""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, company, email, title,
               mdcp_score, mdcp_tier,
               rss_score, rss_tier,
               priority_score, urgency_level,
               recommended_action, last_scored
        FROM contacts
        WHERE priority_score IS NOT NULL
        ORDER BY priority_score DESC
    ''')
    
    columns = [desc[0] for desc in cursor.description]
    contacts = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    return {
        'status': 'success',
        'count': len(contacts),
        'contacts': contacts
    }
