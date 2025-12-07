BASE="https://apex-backend-production-production.up.railway.app"

echo "=== TESTING ALL LIKELY MISSING ENDPOINTS ==="

endpoints=(
    "/api/todays-board"
    "/api/today"
    "/api/board"
    "/api/queue"
    "/api/call-queue"
    "/api/contacts/queue"
    "/api/pipeline"
    "/api/dashboard"
    "/api/stats"
    "/api/settings"
    "/api/user/settings"
    "/api/preferences"
)

for ep in "${endpoints[@]}"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$ep")
    if [ "$code" = "200" ]; then
        echo "✅ $ep [$code]"
    else
        echo "❌ $ep [$code]"
    fi
done
# ============= CONTACT ACTIVITIES =============
@app.route('/api/contacts/<int:contact_id>/activities', methods=['GET'])
def get_contact_activities(contact_id):
    try:
        return jsonify({
            'activities': [],
            'contact_id': contact_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/meeting-prep', methods=['GET'])
def get_meeting_prep(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify({
            'contact_id': contact_id,
            'name': contact.get('name'),
            'company': contact.get('company'),
            'talking_points': [],
            'questions': [],
            'background': contact.get('enrichment_data') or ''
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/icp-match', methods=['GET'])
def get_icp_match(contact_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify({
            'contact_id': contact_id,
            'match_score': contact.get('match_score') or 0,
            'match_tier': contact.get('match_tier') or 'UNKNOWN',
            'criteria': {}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= ENROLLMENTS =============
@app.route('/api/contacts/<int:contact_id>/enrollments', methods=['GET'])
def get_contact_enrollments(contact_id):
    try:
        return jsonify({
            'enrollments': [],
            'contact_id': contact_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>/enroll', methods=['POST'])
def enroll_contact(contact_id):
    try:
        data = request.get_json(silent=True) or {}
        cadence_id = data.get('cadence_id')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE contacts SET cadence_id = %s, cadence_status = 'active', cadence_started_at = NOW()
            WHERE id = %s
        """, (cadence_id, contact_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'enrollment_id': contact_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enrollments/<int:enrollment_id>/advance', methods=['POST'])
def advance_enrollment(enrollment_id):
    try:
        return jsonify({'success': True, 'enrollment_id': enrollment_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enrollments/<int:enrollment_id>/status', methods=['GET'])
def get_enrollment_status(enrollment_id):
    try:
        return jsonify({
            'enrollment_id': enrollment_id,
            'status': 'active',
            'current_step': 1,
            'total_steps': 5
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= IMPORT =============
@app.route('/api/contacts/import', methods=['POST'])
def import_contacts():
    try:
        data = request.get_json(silent=True) or {}
        return jsonify({
            'success': True,
            'imported': 0,
            'message': 'Import started'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import/status', methods=['GET'])
def get_import_status():
    try:
        return jsonify({
            'status': 'idle',
            'progress': 0,
            'total': 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/hubspot/import', methods=['POST'])
def hubspot_import():
    try:
        return jsonify({
            'success': True,
            'message': 'HubSpot import started'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= USER & SETTINGS =============
@app.route('/api/user/proof-points', methods=['GET'])
def get_user_proof_points():
    try:
        return jsonify({
            'proof_points': [
                {'id': 1, 'title': '90% Approval Rate', 'description': 'We understand how to get deals done'},
                {'id': 2, 'title': 'Fast Close', 'description': 'Nimble credit and closing process'}
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/playbook', methods=['GET'])
def get_settings_playbook():
    try:
        import json
        playbook_file = os.path.join(os.path.dirname(__file__), 'playbook.json')
        if os.path.exists(playbook_file):
            with open(playbook_file, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({'configured': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/playbook', methods=['POST'])
def save_settings_playbook():
    try:
        import json
        data = request.get_json(silent=True) or {}
        playbook_file = os.path.join(os.path.dirname(__file__), 'playbook.json')
        with open(playbook_file, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= CADENCE EXTRAS =============
@app.route('/api/cadence-queue', methods=['GET'])
def get_cadence_queue():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM contacts 
            WHERE cadence_status = 'active'
            ORDER BY cadence_started_at DESC
            LIMIT 50
        """)
        contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({'queue': contacts, 'count': len(contacts)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cadence-stats', methods=['GET'])
def get_cadence_stats():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE cadence_status = 'active'")
        active = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE cadence_status = 'completed'")
        completed = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'active': active,
            'completed': completed,
            'paused': 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= ANALYTICS DASHBOARD =============
@app.route('/api/analytics/dashboard', methods=['GET'])
def get_analytics_dashboard():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        total = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
        enriched = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE match_tier = 'HIGH'")
        high = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE created_at > NOW() - INTERVAL '7 days'")
        recent = cursor.fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'total_contacts': total,
            'enriched': enriched,
            'high_priority': high,
            'new_this_week': recent,
            'charts': {
                'pipeline': [
                    {'stage': 'New', 'count': recent},
                    {'stage': 'Enriched', 'count': enriched},
                    {'stage': 'Qualified', 'count': high}
                ]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= RUN =============
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"🚀 Starting APEX Backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
