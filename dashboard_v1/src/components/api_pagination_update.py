
# ============================================================
# UPDATE IN api.py - Modify the get_contacts endpoint
# ============================================================

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts with optional filtering and pagination"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        status = request.args.get('status')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)

        # Build query
        query = 'SELECT * FROM contacts'
        count_query = 'SELECT COUNT(*) FROM contacts'
        params = []
        count_params = []

        if status:
            query += ' WHERE enrichment_status = ?'
            count_query += ' WHERE enrichment_status = ?'
            params.append(status)
            count_params.append(status)

        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])

        cursor.execute(query, params)
        contacts = [dict(row) for row in cursor.fetchall()]

        # Get total count
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        conn.close()

        return jsonify({
            'contacts': contacts,
            'total': total,
            'page': (offset // limit) + 1,
            'hasMore': offset + limit < total
        })

    except Exception as e:
        logger.error(f"❌ Error fetching contacts: {e}")
        return jsonify({'error': str(e)}), 500
