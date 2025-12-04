# Add this to your api.py after the enrichment endpoints

@app.route('/api/todays-board', methods=['GET'])
def get_todays_board():
    """Daily prioritized action list"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        now = datetime.now()
        date_str = now.strftime('%B %d, %Y')
        time_str = now.strftime('%I:%M %p')
        
        # Get all contacts with scores
        cursor.execute("""
            SELECT id, name, email, phone, company, title,
                   mdcp_score, priority_score, enrichment_status,
                   enriched_at as last_enriched
            FROM contacts
            WHERE enrichment_status = 'completed'
            ORDER BY COALESCE(mdcp_score, priority_score, 0) DESC
            LIMIT 50
        """)
        
        all_contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # Organize by tiers
        urgent = []
        warm = []
        nurture = []
        stable = []
        hot = []
        qualified = []
        potential = []
        
        for c in all_contacts:
            score = c.get('mdcp_score') or c.get('priority_score') or 0
            c['mdcp_score'] = score
            c['why_now'] = f"Priority score: {score:.0f}"
            c['enrichment_status'] = c.get('enrichment_status', 'none')
            
            # Categorize
            if score >= 90:
                c['urgency_tier'] = 'urgent'
                c['urgency_label'] = '🔥 ACT TODAY'
                c['contact_type'] = 'relationship'
                if len(urgent) < 5:
                    urgent.append(c)
            elif score >= 80:
                c['urgency_tier'] = 'hot_prospect'
                c['urgency_label'] = '🎯 HOT'
                c['contact_type'] = 'prospect'
                if len(hot) < 5:
                    hot.append(c)
            elif score >= 70:
                c['urgency_tier'] = 'warm'
                c['urgency_label'] = '⏰ THIS WEEK'
                c['contact_type'] = 'relationship'
                if len(warm) < 5:
                    warm.append(c)
            elif score >= 60:
                c['urgency_tier'] = 'qualified_prospect'
                c['urgency_label'] = '✅ QUALIFIED'
                c['contact_type'] = 'prospect'
                if len(qualified) < 5:
                    qualified.append(c)
            else:
                c['urgency_tier'] = 'nurture'
                c['urgency_label'] = '💎 NURTURE'
                c['contact_type'] = 'relationship'
                if len(nurture) < 4:
                    nurture.append(c)
        
        return jsonify({
            'success': True,
            'date': date_str,
            'time': time_str,
            'total_actions': len(urgent) + len(hot) + len(warm) + len(qualified),
            'recommendation': f"Start with {len(urgent)} urgent contacts and {len(hot)} hot prospects",
            'relationships': {
                'total': len(urgent) + len(warm) + len(nurture),
                'urgent_count': len(urgent),
                'warm_count': len(warm),
                'nurture_count': len(nurture),
                'stable_count': len(stable),
                'tiers': {
                    'urgent': urgent,
                    'warm': warm,
                    'nurture': nurture,
                    'stable': stable
                }
            },
            'new_prospects': {
                'total': len(hot) + len(qualified) + len(potential),
                'hot_count': len(hot),
                'qualified_count': len(qualified),
                'potential_count': len(potential),
                'tiers': {
                    'hot': hot,
                    'qualified': qualified,
                    'potential': potential
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Today's Board error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500