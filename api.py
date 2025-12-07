"""
APEX Backend API - Clean Rebuild
December 7, 2025
"""
import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

# ============= SETUP =============
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.environ.get('DATABASE_URL')
logger.info(f"Database URL configured: {'Yes' if DATABASE_URL else 'No'}")

def get_db():
    """Get PostgreSQL connection"""
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = RealDictCursor
    return conn

# ============= HEALTH =============
@app.route('/', methods=['GET'])
def root():
    return jsonify({'status': 'running', 'service': 'apex-backend'})

@app.route('/api/health', methods=['GET'])
def health():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        count = cursor.fetchone()['count']
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'contacts': count,
            'service': 'apex-backend',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

# ============= CONTACTS =============
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    try:
        conn = get_db()
        cursor = conn.cursor()
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        cursor.execute("SELECT * FROM contacts ORDER BY id DESC LIMIT %s OFFSET %s", (limit, offset))
        contacts = [dict(row) for row in cursor.fetchall()]
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        total = cursor.fetchone()['count']
        conn.close()
        return jsonify({'contacts': contacts, 'total': total})
    except Exception as e:
        logger.error(f"Error in get_contacts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        if contact:
            return jsonify(dict(contact))
        return jsonify({'error': 'Contact not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= TODAY'S BOARD =============
@app.route('/api/todays-board', methods=['GET'])
def todays_board():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get top contacts by score
        cursor.execute("""
            SELECT * FROM contacts 
            ORDER BY COALESCE(match_score, 0) DESC, id DESC 
            LIMIT 20
        """)
        contacts = [dict(row) for row in cursor.fetchall()]
        
        # Get stats
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        total = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
        enriched = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'contacts': contacts,
            'count': len(contacts),
            'stats': {
                'total_contacts': total,
                'enriched': enriched
            }
        })
    except Exception as e:
        logger.error(f"Error in todays_board: {e}")
        return jsonify({'error': str(e)}), 500

# ============= ANALYTICS =============
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        total_contacts = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
        enriched = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'HIGH'")
        high_tier = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'MEDIUM'")
        medium_tier = cursor.fetchone()['count']
        
        cursor.execute("SELECT AVG(match_score) as avg FROM contacts WHERE match_score IS NOT NULL")
        avg_score = cursor.fetchone()['avg'] or 0
        
        conn.close()
        
        return jsonify({
            'total_contacts': total_contacts,
            'enriched_contacts': enriched,
            'high_tier': high_tier,
            'medium_tier': medium_tier,
            'average_score': round(float(avg_score), 2),
            'pipeline': {
                'total': total_contacts,
                'qualified': high_tier + medium_tier,
                'enriched': enriched
            }
        })
    except Exception as e:
        logger.error(f"Error in analytics: {e}")
        return jsonify({'error': str(e)}), 500

# ============= SMART LISTS =============
@app.route('/api/smart-lists', methods=['GET'])
def get_smart_lists():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        lists = []
        
        # Hot Leads
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'HIGH'")
        lists.append({'id': 'hot_leads', 'name': 'Hot Leads', 'count': cursor.fetchone()['count']})
        
        # Warm Leads
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'MEDIUM'")
        lists.append({'id': 'warm_leads', 'name': 'Warm Leads', 'count': cursor.fetchone()['count']})
        
        # Enriched
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
        lists.append({'id': 'enriched', 'name': 'Enriched', 'count': cursor.fetchone()['count']})
        
        # Needs Enrichment
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status IS NULL OR enrichment_status != 'completed'")
        lists.append({'id': 'needs_enrichment', 'name': 'Needs Enrichment', 'count': cursor.fetchone()['count']})
        
        # Recent
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE created_at > NOW() - INTERVAL '7 days'")
        lists.append({'id': 'recent', 'name': 'Added This Week', 'count': cursor.fetchone()['count']})
        
        conn.close()
        
        return jsonify({'lists': lists})
    except Exception as e:
        logger.error(f"Error in smart_lists: {e}")
        return jsonify({'error': str(e)}), 500

# ============= DEBUG =============
@app.route('/api/debug/routes', methods=['GET'])
def debug_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'path': str(rule.rule),
            'methods': sorted(list(rule.methods - {'HEAD', 'OPTIONS'})),
            'endpoint': rule.endpoint
        })
    return jsonify({
        'total': len(routes),
        'routes': sorted(routes, key=lambda x: x['path'])
    })

# ============= USER PROFILE =============
@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    user_id = request.args.get('user_id', 'default')
    # Return default profile for now
    return jsonify({
        'user_id': user_id,
        'full_name': 'Sales User',
        'company': 'Apex Sales',
        'configured': False
    })

# ============= RUN =============
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"🚀 Starting APEX Backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# ============= CONTACT CRUD =============
@app.route('/api/contacts', methods=['POST'])
def create_contact():
    try:
        data = request.get_json()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO contacts (name, email, company, title, phone)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('name'),
            data.get('email'),
            data.get('company'),
            data.get('title'),
            data.get('phone')
        ))
        contact_id = cursor.fetchone()['id']
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'id': contact_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    try:
        data = request.get_json()
        conn = get_db()
        cursor = conn.cursor()
        
        # Build dynamic update
        fields = []
        values = []
        for key in ['name', 'email', 'company', 'title', 'phone', 'notes']:
            if key in data:
                fields.append(f"{key} = %s")
                values.append(data[key])
        
        if fields:
            values.append(contact_id)
            cursor.execute(f"UPDATE contacts SET {', '.join(fields)} WHERE id = %s", values)
            conn.commit()
        
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= ENRICHMENT =============
@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return jsonify({'error': 'Contact not found'}), 404
        
        # Mark as processing
        cursor.execute("UPDATE contacts SET enrichment_status = 'processing' WHERE id = %s", (contact_id,))
        conn.commit()
        conn.close()
        
        # TODO: Actual enrichment logic
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'message': 'Enrichment started'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/enrichment-status', methods=['GET'])
def get_enrichment_status(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT enrichment_status, enriched_at FROM contacts WHERE id = %s", (contact_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify({
            'status': row['enrichment_status'] or 'pending',
            'enriched_at': row['enriched_at']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= CADENCES =============
@app.route('/api/cadences', methods=['GET'])
def get_cadences():
    # Return default cadences for now
    return jsonify({
        'cadences': [
            {'id': 1, 'name': 'Default Outreach', 'steps': 5, 'contacts': 0},
            {'id': 2, 'name': 'High Priority', 'steps': 3, 'contacts': 0},
            {'id': 3, 'name': 'Nurture', 'steps': 7, 'contacts': 0}
        ]
    })

@app.route('/api/cadences/<int:cadence_id>', methods=['GET'])
def get_cadence(cadence_id):
    return jsonify({
        'id': cadence_id,
        'name': 'Default Cadence',
        'steps': [],
        'contacts': []
    })

# ============= PLAYBOOK =============
@app.route('/api/playbook', methods=['GET'])
def get_playbook():
    try:
        import json
        playbook_file = os.path.join(os.path.dirname(__file__), 'playbook.json')
        if os.path.exists(playbook_file):
            with open(playbook_file, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({'configured': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/playbook', methods=['POST'])
def save_playbook():
    try:
        import json
        data = request.get_json()
        playbook_file = os.path.join(os.path.dirname(__file__), 'playbook.json')
        with open(playbook_file, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

