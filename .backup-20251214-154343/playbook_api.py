"""
Playbook API Module - Handles all playbook/ICP functionality
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

# File path for playbook storage
PLAYBOOK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'playbook.json')

def load_playbook() -> dict:
    """Load playbook from JSON file"""
    try:
        logger.info(f"Loading playbook from: {PLAYBOOK_FILE}")
        if os.path.exists(PLAYBOOK_FILE):
            with open(PLAYBOOK_FILE, 'r') as f:
                data = json.load(f)
                logger.info(f"✅ Loaded playbook: {data.get('companyName', 'NO NAME')}")
                return data
        logger.warning("Playbook file not found")
    except Exception as e:
        logger.error(f"Error loading playbook: {e}")
    return {}

def save_playbook(data: dict) -> bool:
    """Save playbook to JSON file"""
    try:
        logger.info(f"Saving playbook to: {PLAYBOOK_FILE}")
        with open(PLAYBOOK_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"✅ Saved playbook for: {data.get('companyName', 'NO NAME')}")
        return True
    except Exception as e:
        logger.error(f"Error saving playbook: {e}")
        return False

def is_playbook_configured(playbook: dict) -> bool:
    """Check if playbook has meaningful data"""
    if not playbook:
        return False
    
    has_company = bool(playbook.get('companyName'))
    has_industries = bool(playbook.get('icp', {}).get('industries'))
    has_value_props = bool(playbook.get('valueProps'))
    has_products = bool(playbook.get('products'))
    
    configured = has_company or has_industries or has_value_props or has_products
    logger.info(f"Playbook configured check: {configured} (company={has_company}, industries={has_industries}, vp={has_value_props})")
    return configured

def calculate_icp_match(contact: dict, profile_text: str, playbook: dict) -> dict:
    """Calculate ICP match score"""
    if not playbook or not is_playbook_configured(playbook):
        return {'score': 0, 'reasons': [], 'match_level': 'Unknown'}
    
    icp = playbook.get('icp', {})
    score = 50
    reasons = []
    
    # Combine all searchable text
    all_text = ' '.join([
        (profile_text or '').lower(),
        (contact.get('industry') or '').lower(),
        (contact.get('title') or '').lower(),
        (contact.get('company') or '').lower(),
    ])
    
    # Industry matching
    for industry in icp.get('industries', []):
        if industry.lower() in all_text:
            score += 15
            reasons.append(f"Industry: {industry}")
            break
    
    # Title matching
    for title in icp.get('titles', []):
        if title.lower() in all_text:
            score += 15
            reasons.append(f"Title: {title}")
            break
    
    # Pain point matching
    pain_count = sum(1 for p in icp.get('painPoints', []) 
                     if any(w.lower() in all_text for w in p.split() if len(w) > 4))
    if pain_count:
        score += min(pain_count * 5, 15)
        reasons.append(f"Pain points: {pain_count} matches")
    
    # Tech stack matching
    tech_count = sum(1 for t in icp.get('techStack', []) if t.lower() in all_text)
    if tech_count:
        score += min(tech_count * 3, 10)
        reasons.append(f"Tech: {tech_count} matches")
    
    # Region matching
    for region in icp.get('regions', []):
        if region.lower() in all_text:
            score += 5
            reasons.append(f"Region: {region}")
            break
    
    score = min(score, 100)
    
    match_level = (
        'Excellent' if score >= 85 else
        'Strong' if score >= 70 else
        'Moderate' if score >= 55 else
        'Low'
    )
    
    return {'score': score, 'reasons': reasons, 'match_level': match_level}

def generate_why_us_fit(playbook: dict) -> dict:
    """Generate fit points from playbook"""
    if not playbook:
        return {'summary': '', 'points': []}
    
    points = []
    
    # Add value props
    for vp in playbook.get('valueProps', [])[:3]:
        points.append({
            'type': 'value_prop',
            'title': vp.get('headline', ''),
            'detail': vp.get('description', ''),
            'proof': vp.get('proofPoint', '')
        })
    
    # Add pain points
    for pp in playbook.get('painPoints', [])[:2]:
        points.append({
            'type': 'pain_point',
            'title': f"We solve: {pp.get('problem', '')[:60]}",
            'detail': pp.get('solution', ''),
            'impact': pp.get('impact', '')
        })
    
    company = playbook.get('companyName', 'We')
    return {'summary': f"{company} is positioned to help.", 'points': points[:5]}


def register_playbook_routes(app, get_db):
    """Register all playbook-related routes with the Flask app"""
    
    from flask import jsonify, request
    
    @app.route('/api/settings/playbook', methods=['GET'])
    def api_get_playbook():
        return jsonify(load_playbook())
    
    @app.route('/api/settings/playbook', methods=['POST'])
    def api_save_playbook():
        data = request.json
        if save_playbook(data):
            return jsonify({'success': True})
        return jsonify({'error': 'Failed to save'}), 500
    
    @app.route('/api/contacts/<int:contact_id>/icp-match', methods=['GET'])
    def api_icp_match(contact_id):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return jsonify({'error': 'Contact not found'}), 404
            
            contact = dict(row)
            profile_text = contact.get('enrichment_data', '') or ''
            playbook = load_playbook()
            
            configured = is_playbook_configured(playbook)
            icp_match = calculate_icp_match(contact, profile_text, playbook)
            why_us = generate_why_us_fit(playbook)
            
            logger.info(f"ICP Match API: contact={contact_id}, configured={configured}, score={icp_match['score']}")
            
            return jsonify({
                'contact_id': contact_id,
                'icp_match': icp_match,
                'why_us_fit': why_us,
                'playbook_configured': configured
            })
        except Exception as e:
            logger.error(f"ICP match error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    logger.info("✅ Playbook routes registered")

