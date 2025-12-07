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
# ============= SEARCH =============
@app.route('/api/contacts/search', methods=['GET'])
def search_contacts():
    try:
        q = request.args.get('q', '')
        limit = request.args.get('limit', 50, type=int)
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE name ILIKE %s OR email ILIKE %s OR company ILIKE %s
            ORDER BY match_score DESC NULLS LAST
            LIMIT %s
        """, (f'%{q}%', f'%{q}%', f'%{q}%', limit))
        contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'contacts': contacts, 'query': q, 'count': len(contacts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= COLD CALL QUEUE =============
@app.route('/api/cold-call/queue', methods=['GET'])
def get_cold_call_queue():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE phone IS NOT NULL AND phone != ''
            ORDER BY match_score DESC NULLS LAST
            LIMIT 20
        """)
        contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({'queue': contacts, 'count': len(contacts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cold-call/log', methods=['POST'])
def log_cold_call():
    try:
        data = request.get_json()
        contact_id = data.get('contact_id')
        outcome = data.get('outcome')
        notes = data.get('notes', '')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts SET 
                times_contacted = COALESCE(times_contacted, 0) + 1,
                last_contacted = NOW(),
                notes = COALESCE(notes, '') || %s
            WHERE id = %s
        """, (f'\n[Call {outcome}]: {notes}', contact_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= BULK OPERATIONS =============
@app.route('/api/contacts/bulk-enrich', methods=['POST'])
def bulk_enrich():
    try:
        data = request.get_json()
        contact_ids = data.get('contact_ids', [])
        
        conn = get_db()
        cursor = conn.cursor()
        for cid in contact_ids[:50]:  # Limit to 50
            cursor.execute("UPDATE contacts SET enrichment_status = 'queued' WHERE id = %s", (cid,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'queued': len(contact_ids[:50])})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/bulk-score', methods=['POST'])
def bulk_score():
    try:
        data = request.get_json()
        contact_ids = data.get('contact_ids', [])
        
        # Placeholder - actual scoring would go here
        return jsonify({'success': True, 'scored': len(contact_ids)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= SCRIPTS =============
@app.route('/api/contacts/<int:contact_id>/scripts', methods=['GET'])
def get_contact_scripts(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT call_script_1, call_script_2, call_script_3, 
                   email_1_body, email_2_body, email_3_body
            FROM contacts WHERE id = %s
        """, (contact_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify({
            'call_scripts': [row['call_script_1'], row['call_script_2'], row['call_script_3']],
            'email_scripts': [row['email_1_body'], row['email_2_body'], row['email_3_body']]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/scripts', methods=['POST'])
def generate_scripts(contact_id):
    try:
        # Placeholder for script generation
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'message': 'Script generation queued'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= SCORING =============
@app.route('/api/contacts/<int:contact_id>/score', methods=['POST'])
def score_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return jsonify({'error': 'Contact not found'}), 404
        
        # Simple scoring logic
        score = 50
        tier = 'MEDIUM'
        
        if contact.get('enrichment_status') == 'completed':
            score += 20
        if contact.get('company'):
            score += 10
        if contact.get('title'):
            score += 10
        if contact.get('email'):
            score += 10
        
        if score >= 80:
            tier = 'HIGH'
        elif score < 50:
            tier = 'LOW'
        
        cursor.execute("""
            UPDATE contacts SET match_score = %s, match_tier = %s, last_scored = NOW()
            WHERE id = %s
        """, (score, tier, contact_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'score': score, 'tier': tier})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= WHY ME =============
@app.route('/api/contacts/<int:contact_id>/why-me', methods=['GET'])
def get_why_me(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT why_me_data FROM contacts WHERE id = %s", (contact_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Contact not found'}), 404
        
        if row['why_me_data']:
            import json
            return jsonify(json.loads(row['why_me_data']))
        return jsonify({'generated': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/why-me', methods=['POST'])
def generate_why_me(contact_id):
    try:
        # Placeholder for Why Me generation
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'message': 'Why Me generation queued'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= AI COMMAND =============
@app.route('/api/ai/command', methods=['POST'])
def ai_command():
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        # Placeholder for AI command processing
        return jsonify({
            'success': True,
            'command': command,
            'response': f'Command received: {command}',
            'actions': []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= FILTERS & TAGS =============
@app.route('/api/filters', methods=['GET'])
def get_filters():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get unique values for filters
        cursor.execute("SELECT DISTINCT company FROM contacts WHERE company IS NOT NULL LIMIT 100")
        companies = [row['company'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT title FROM contacts WHERE title IS NOT NULL LIMIT 100")
        titles = [row['title'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT match_tier FROM contacts WHERE match_tier IS NOT NULL")
        tiers = [row['match_tier'] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'companies': companies,
            'titles': titles,
            'tiers': tiers,
            'statuses': ['pending', 'processing', 'completed', 'failed']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= ACTIVITY =============
@app.route('/api/activity', methods=['GET'])
def get_activity():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Recent enrichments
        cursor.execute("""
            SELECT id, name, company, enriched_at, 'enriched' as type
            FROM contacts 
            WHERE enriched_at IS NOT NULL
            ORDER BY enriched_at DESC
            LIMIT 10
        """)
        activities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'activities': activities})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= DASHBOARD STATS =============
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        stats['total_contacts'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
        stats['enriched'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'HIGH'")
        stats['high_priority'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE created_at > NOW() - INTERVAL '7 days'")
        stats['new_this_week'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT AVG(match_score) as avg FROM contacts WHERE match_score IS NOT NULL")
        avg = cursor.fetchone()['avg']
        stats['avg_score'] = round(float(avg), 1) if avg else 0
        
        conn.close()
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= EXPORT =============
@app.route('/api/contacts/export', methods=['GET'])
def export_contacts():
    try:
        format = request.args.get('format', 'json')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts ORDER BY id")
        contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if format == 'csv':
            import csv
            import io
            output = io.StringIO()
            if contacts:
                writer = csv.DictWriter(output, fieldnames=contacts[0].keys())
                writer.writeheader()
                writer.writerows(contacts)
            return output.getvalue(), 200, {'Content-Type': 'text/csv'}
        
        return jsonify({'contacts': contacts, 'count': len(contacts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# ============= BATCH OPERATIONS (Frontend) =============
@app.route('/api/batch/enrich', methods=['POST'])
def batch_enrich():
    try:
        data = request.get_json(silent=True) or {}
        contact_ids = data.get('contact_ids', [])
        
        conn = get_db()
        cursor = conn.cursor()
        
        if contact_ids:
            for cid in contact_ids[:50]:
                cursor.execute("UPDATE contacts SET enrichment_status = 'queued' WHERE id = %s", (cid,))
        else:
            cursor.execute("UPDATE contacts SET enrichment_status = 'queued' WHERE enrichment_status IS NULL OR enrichment_status = 'pending' LIMIT 50")
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Batch enrichment queued'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch/rescore', methods=['POST'])
def batch_rescore():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Simple batch scoring
        cursor.execute("""
            UPDATE contacts SET 
                match_score = 50 + 
                    CASE WHEN enrichment_status = 'completed' THEN 20 ELSE 0 END +
                    CASE WHEN company IS NOT NULL THEN 10 ELSE 0 END +
                    CASE WHEN title IS NOT NULL THEN 10 ELSE 0 END +
                    CASE WHEN email IS NOT NULL THEN 10 ELSE 0 END,
                match_tier = CASE 
                    WHEN match_score >= 80 THEN 'HIGH'
                    WHEN match_score >= 50 THEN 'MEDIUM'
                    ELSE 'LOW'
                END,
                last_scored = NOW()
        """)
        conn.commit()
        count = cursor.rowcount
        conn.close()
        
        return jsonify({'success': True, 'rescored': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= CONTACT TIER =============
@app.route('/api/contacts/<int:contact_id>/tier', methods=['PUT'])
def update_contact_tier(contact_id):
    try:
        data = request.get_json()
        tier = data.get('tier', 'MEDIUM')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE contacts SET match_tier = %s WHERE id = %s", (tier, contact_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'tier': tier})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= COLD CALL QUEUE ACTIONS =============
@app.route('/api/cold-call/queue/<int:contact_id>/attempt', methods=['POST'])
def log_call_attempt(contact_id):
    try:
        data = request.get_json() or {}
        outcome = data.get('outcome', 'attempted')
        notes = data.get('notes', '')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts SET 
                times_contacted = COALESCE(times_contacted, 0) + 1,
                last_contacted = NOW()
            WHERE id = %s
        """, (contact_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'outcome': outcome})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cold-call/queue/<int:contact_id>/status', methods=['PUT'])
def update_call_status(contact_id):
    try:
        data = request.get_json() or {}
        status = data.get('status', 'pending')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE contacts SET cadence_status = %s WHERE id = %s", (status, contact_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cold-call/queue/<int:contact_id>/promote', methods=['POST'])
def promote_contact(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts SET 
                match_tier = 'HIGH',
                match_score = GREATEST(COALESCE(match_score, 0), 80)
            WHERE id = %s
        """, (contact_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'promoted': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# ============= GENERATION ENDPOINTS =============
@app.route('/api/contacts/<int:contact_id>/reset-enrichment', methods=['POST'])
def reset_enrichment(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts SET 
                enrichment_status = NULL,
                enrichment_data = NULL,
                enriched_at = NULL
            WHERE id = %s
        """, (contact_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/generate-persona', methods=['POST'])
def generate_persona(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify({
            'success': True,
            'contact_id': contact_id,
            'persona': {
                'type': contact.get('persona') or 'prospect',
                'confidence': contact.get('persona_confidence') or 50
            },
            'message': 'Persona generated'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/generate-call-script', methods=['POST'])
def generate_call_script(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        name = contact.get('name') or 'there'
        company = contact.get('company') or 'your company'
        
        script = f"""Hi {name}, this is [Your Name] from Harvest Small Business Finance.

I'm reaching out because I noticed {company} might benefit from our SBA financing solutions.

We specialize in helping businesses like yours secure 90% financing for commercial real estate.

Do you have 2 minutes to discuss how we might help?"""
        
        return jsonify({
            'success': True,
            'script': script,
            'contact_id': contact_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/generate-linkedin', methods=['POST'])
def generate_linkedin(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        name = contact.get('name', '').split()[0] if contact.get('name') else 'there'
        
        message = f"""Hi {name},

I came across your profile and was impressed by your work. I help business owners secure SBA financing for commercial real estate with up to 90% LTV.

Would you be open to a brief conversation about how this might benefit your business goals?

Best regards"""
        
        return jsonify({
            'success': True,
            'message': message,
            'contact_id': contact_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/generate-email', methods=['POST'])
def generate_email(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        name = contact.get('name', '').split()[0] if contact.get('name') else 'there'
        company = contact.get('company') or 'your company'
        
        email = {
            'subject': f'SBA Financing Opportunity for {company}',
            'body': f"""Hi {name},

I hope this email finds you well. I'm reaching out from Harvest Small Business Finance because I believe we can help {company} achieve its growth objectives.

We specialize in SBA 504 and 7(a) loans, offering:
• Up to 90% financing
• Competitive rates
• Fast, reliable closings

Would you have 15 minutes this week for a brief call to explore if this could benefit your business?

Best regards,
[Your Name]
Harvest Small Business Finance"""
        }
        
        return jsonify({
            'success': True,
            'email': email,
            'contact_id': contact_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/generate-outreach', methods=['POST'])
def generate_outreach(contact_id):
    try:
        data = request.get_json(silent=True) or {}
        outreach_type = data.get('type', 'email')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify({
            'success': True,
            'type': outreach_type,
            'content': f'Generated {outreach_type} content for {contact.get("name", "contact")}',
            'contact_id': contact_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/generate-sequence', methods=['POST'])
def generate_sequence(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        sequence = [
            {'day': 1, 'type': 'email', 'action': 'Initial outreach'},
            {'day': 3, 'type': 'linkedin', 'action': 'Connection request'},
            {'day': 5, 'type': 'call', 'action': 'Follow-up call'},
            {'day': 7, 'type': 'email', 'action': 'Value-add email'},
            {'day': 10, 'type': 'call', 'action': 'Final attempt'}
        ]
        
        return jsonify({
            'success': True,
            'sequence': sequence,
            'contact_id': contact_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['GET'])
def download_file():
    try:
        path = request.args.get('path', '')
        # Security: only allow specific file types
        if not path or '..' in path:
            return jsonify({'error': 'Invalid path'}), 400
        
        return jsonify({
            'error': 'File downloads not yet implemented',
            'path': path
        }), 501
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# ============= SMART LIST CONTACTS =============
@app.route('/api/smart-lists/<list_id>/contacts', methods=['GET'])
def get_smart_list_contacts(list_id):
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Map list_id to SQL filter
        filters = {
            'hot_leads': "match_tier = 'HIGH'",
            'warm_leads': "match_tier = 'MEDIUM'",
            'cold_leads': "match_tier = 'LOW' OR match_tier IS NULL",
            'enriched': "enrichment_status = 'completed'",
            'needs_enrichment': "enrichment_status IS NULL OR enrichment_status != 'completed'",
            'recent': "created_at > NOW() - INTERVAL '7 days'",
            'all': "1=1"
        }
        
        where_clause = filters.get(list_id, "1=1")
        
        cursor.execute(f"""
            SELECT * FROM contacts 
            WHERE {where_clause}
            ORDER BY match_score DESC NULLS LAST, id DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        contacts = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute(f"SELECT COUNT(*) as count FROM contacts WHERE {where_clause}")
        total = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'contacts': contacts,
            'total': total,
            'list_id': list_id,
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        logger.error(f"Smart list error: {e}")
        return jsonify({'error': str(e)}), 500

# ============= RUN =============
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"🚀 Starting APEX Backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
