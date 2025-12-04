# REPLACE the todays-board endpoint in api.py with this version:

@app.route('/api/todays-board', methods=['GET'])
def get_todays_board():
    """Daily prioritized action list - shows ALL contacts"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        now = datetime.now()
        date_str = now.strftime('%B %d, %Y')
        time_str = now.strftime('%I:%M %p')
        
        # Get ALL contacts (not just enriched)
        cursor.execute("""
            SELECT id, name, email, phone, company, title,
                   mdcp_score, priority_score, enrichment_status,
                   enriched_at as last_enriched
            FROM contacts
            ORDER BY COALESCE(mdcp_score, priority_score, 0) DESC
            LIMIT 100
        """)
        
        all_contacts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info(f"📊 Found {len(all_contacts)} contacts for Today's Board")
        
        # Organize by tiers
        urgent = []
        warm = []
        nurture = []
        stable = []
        hot = []
        qualified = []
        potential = []
        
        for c in all_contacts:
            # Calculate score if missing
            score = c.get('mdcp_score') or c.get('priority_score')
            
            if not score:
                # Default score based on data completeness
                score = 50
                if c.get('email'): score += 10
                if c.get('phone'): score += 10
                if c.get('company'): score += 10
                if c.get('title'): score += 10
                logger.debug(f"Contact {c.get('name')}: calculated score {score}")
            
            c['mdcp_score'] = float(score)
            c['priority_score'] = float(score)
            
            # Set enrichment status
            enrich_status = c.get('enrichment_status') or 'none'
            c['enrichment_status'] = enrich_status
            c['last_enriched'] = c.get('last_enriched')
            
            # Generate why_now message
            if enrich_status == 'completed':
                c['why_now'] = f"✅ Enriched - Score {score:.0f}"
            else:
                c['why_now'] = f"⚡ Ready to enrich - Score {score:.0f}"
            
            # Categorize by score
            if score >= 90:
                c['urgency_tier'] = 'urgent'
                c['urgency_label'] = '🔥 URGENT'
                c['contact_type'] = 'relationship'
                c['urgency_message'] = f"High priority: {score:.0f}"
                if len(urgent) < 10:
                    urgent.append(c)
            elif score >= 80:
                c['urgency_tier'] = 'hot_prospect'
                c['urgency_label'] = '🎯 HOT'
                c['contact_type'] = 'prospect'
                c['urgency_message'] = f"Hot prospect: {score:.0f}"
                if len(hot) < 10:
                    hot.append(c)
            elif score >= 70:
                c['urgency_tier'] = 'warm'
                c['urgency_label'] = '⏰ WARM'
                c['contact_type'] = 'relationship'
                c['urgency_message'] = f"Good timing: {score:.0f}"
                if len(warm) < 10:
                    warm.append(c)
            elif score >= 60:
                c['urgency_tier'] = 'qualified_prospect'
                c['urgency_label'] = '✅ QUALIFIED'
                c['contact_type'] = 'prospect'
                c['urgency_message'] = f"Qualified: {score:.0f}"
                if len(qualified) < 10:
                    qualified.append(c)
            else:
                c['urgency_tier'] = 'potential_prospect'
                c['urgency_label'] = '🔍 POTENTIAL'
                c['contact_type'] = 'prospect'
                c['urgency_message'] = f"Needs enrichment: {score:.0f}"
                if len(potential) < 10:
                    potential.append(c)
        
        total_actions = len(urgent) + len(hot) + len(warm) + len(qualified)
        
        logger.info(f"📊 Board: {len(urgent)} urgent, {len(hot)} hot, {len(warm)} warm, {len(qualified)} qualified")
        
        return jsonify({
            'success': True,
            'date': date_str,
            'time': time_str,
            'total_actions': total_actions,
            'recommendation': f"Start with {len(urgent)} urgent and {len(hot)} hot prospects. Enrich {len(potential)} contacts to improve prioritization.",
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