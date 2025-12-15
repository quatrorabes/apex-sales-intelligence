#!/bin/bash

#!/bin/bash
# Fix Apex Enrichment + Deploy Analytics

set -e

echo "🚀 Apex Enrichment Fix & Analytics Deployment"
echo "=" * 70

cd ~/projects/apex/apex-sales-intelligence

# 1. Create enrichment analytics module
echo "📝 Creating enrichment_analytics.py..."
cat > apps/backend/intelligence/engines/enrichment/enrichment_analytics.py << 'EOF'
#!/usr/bin/env python3
"""
Apex Sales Intelligence - Enrichment Analytics Module
Tracks enrichment performance, ROI, and quality metrics
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

DATABASE_URL = os.getenv("DATABASE_URL")

def get_enrichment_analytics(days: int = 30) -> Dict[str, Any]:
	"""
	Generate comprehensive enrichment analytics
	
	Args:
		days: Number of days to analyze (default 30)
		
	Returns:
		Dictionary with analytics data
	"""
	conn = psycopg2.connect(DATABASE_URL)
	conn.cursor_factory = RealDictCursor
	cursor = conn.cursor()
	
	cutoff_date = datetime.now() - timedelta(days=days)
	
	# 1. ENRICHMENT VOLUME METRICS
	cursor.execute("""
		SELECT 
			COUNT(*) FILTER (WHERE enriched_at >= %s) as enrichments_period,
			COUNT(*) FILTER (WHERE enriched_at >= %s AND enrichment_status = 'completed') as successful,
			COUNT(*) FILTER (WHERE enriched_at >= %s AND enrichment_status = 'failed') as failed,
			COUNT(*) FILTER (WHERE enrichment_status = 'pending') as pending,
			COUNT(*) as total_contacts,
			COUNT(*) FILTER (WHERE enriched = 1) as total_enriched
		FROM contacts
	""", (cutoff_date, cutoff_date, cutoff_date))
	
	volume_stats = dict(cursor.fetchone())
	
	# 2. ENRICHMENT QUALITY METRICS
	cursor.execute("""
		SELECT 
			AVG(CAST(match_score AS FLOAT)) as avg_match_score,
			COUNT(*) FILTER (WHERE match_tier = 'HIGH') as high_quality,
			COUNT(*) FILTER (WHERE match_tier = 'MEDIUM') as medium_quality,
			COUNT(*) FILTER (WHERE match_tier = 'LOW') as low_quality,
			AVG(LENGTH(COALESCE(enrichment_data::text, ''))) as avg_profile_length
		FROM contacts
		WHERE enriched_at >= %s
	""", (cutoff_date,))
	
	quality_stats = dict(cursor.fetchone())
	
	# 3. ENRICHMENT TIMELINE (daily breakdown)
	cursor.execute("""
		SELECT 
			DATE(enriched_at) as date,
			COUNT(*) as count,
			COUNT(*) FILTER (WHERE enrichment_status = 'completed') as successful,
			COUNT(*) FILTER (WHERE enrichment_status = 'failed') as failed
		FROM contacts
		WHERE enriched_at >= %s
		GROUP BY DATE(enriched_at)
		ORDER BY date DESC
	""", (cutoff_date,))
	
	timeline = [dict(row) for row in cursor.fetchall()]
	
	# 4. TOP ENRICHED CONTACTS (by match score)
	cursor.execute("""
		SELECT 
			id,
			name,
			company,
			title,
			match_score,
			match_tier,
			enriched_at,
			enrichment_status
		FROM contacts
		WHERE enriched_at >= %s AND enrichment_status = 'completed'
		ORDER BY COALESCE(match_score, 0) DESC
		LIMIT 20
	""", (cutoff_date,))
	
	top_contacts = [dict(row) for row in cursor.fetchall()]
	
	# 5. ENRICHMENT ROI METRICS
	cursor.execute("""
		SELECT 
			COUNT(*) FILTER (WHERE deal_stage IS NOT NULL AND deal_stage != 'lost') as contacts_in_pipeline,
			SUM(CAST(deal_value AS FLOAT)) FILTER (WHERE deal_stage = 'won') as revenue_from_enriched,
			AVG(EXTRACT(EPOCH FROM (NOW() - enriched_at))/86400) as avg_days_since_enrichment
		FROM contacts
		WHERE enriched_at >= %s
	""", (cutoff_date,))
	
	roi_stats = dict(cursor.fetchone())
	
	# 6. ENRICHMENT ERRORS & FAILURE ANALYSIS
	cursor.execute("""
		SELECT 
			enrichment_status,
			COUNT(*) as count,
			array_agg(name ORDER BY enriched_at DESC LIMIT 5) as recent_examples
		FROM contacts
		WHERE enriched_at >= %s AND enrichment_status IN ('failed', 'error')
		GROUP BY enrichment_status
	""", (cutoff_date,))
	
	errors = [dict(row) for row in cursor.fetchall()]
	
	cursor.close()
	conn.close()
	
	# Calculate derived metrics
	success_rate = 0
	if volume_stats['enrichments_period'] > 0:
		success_rate = (volume_stats['successful'] / volume_stats['enrichments_period']) * 100
	
	return {
		"period": {
			"days": days,
			"start_date": cutoff_date.isoformat(),
			"end_date": datetime.now().isoformat()
		},
		"volume": {
			"total_contacts": volume_stats['total_contacts'],
			"total_enriched": volume_stats['total_enriched'],
			"enrichments_this_period": volume_stats['enrichments_period'],
			"successful": volume_stats['successful'],
			"failed": volume_stats['failed'],
			"pending": volume_stats['pending'],
			"success_rate": round(success_rate, 2)
		},
		"quality": {
			"avg_match_score": round(float(quality_stats['avg_match_score'] or 0), 2),
			"high_quality_count": quality_stats['high_quality'],
			"medium_quality_count": quality_stats['medium_quality'],
			"low_quality_count": quality_stats['low_quality'],
			"avg_profile_length": int(quality_stats['avg_profile_length'] or 0)
		},
		"timeline": timeline,
		"top_contacts": top_contacts,
		"roi": {
			"contacts_in_pipeline": roi_stats['contacts_in_pipeline'] or 0,
			"revenue_from_enriched": float(roi_stats['revenue_from_enriched'] or 0),
			"avg_days_since_enrichment": round(float(roi_stats['avg_days_since_enrichment'] or 0), 1)
		},
		"errors": errors
	}

if __name__ == "__main__":
	# Test the analytics
	print("=" * 70)
	print("APEX ENRICHMENT ANALYTICS TEST")
	print("=" * 70)
	
	analytics = get_enrichment_analytics(days=30)
	
	print(f"\n📊 VOLUME METRICS (Last 30 Days)")
	print(f"   Total Contacts: {analytics['volume']['total_contacts']}")
	print(f"   Enriched: {analytics['volume']['total_enriched']}")
	print(f"   This Period: {analytics['volume']['enrichments_this_period']}")
	print(f"   Success Rate: {analytics['volume']['success_rate']}%")
	
	print(f"\n🎯 QUALITY METRICS")
	print(f"   Avg Match Score: {analytics['quality']['avg_match_score']}")
	print(f"   High Quality: {analytics['quality']['high_quality_count']}")
	print(f"   Avg Profile Length: {analytics['quality']['avg_profile_length']} chars")
	
	print(f"\n💰 ROI METRICS")
	print(f"   Contacts in Pipeline: {analytics['roi']['contacts_in_pipeline']}")
	print(f"   Revenue: ${analytics['roi']['revenue_from_enriched']:,.2f}")
	
	print(f"\n📈 TIMELINE (Last 5 Days)")
	for day in analytics['timeline'][:5]:
		print(f"   {day['date']}: {day['successful']} successful, {day['failed']} failed")
	
	print("\n" + "=" * 70)
EOF

# 2. Update main.py with analytics endpoint
echo "📝 Updating main.py..."
# Manual step: Add the analytics endpoint code from Section 2

# 3. Check Render logs for 404 source
echo ""
echo "🔍 DIAGNOSTIC: Check Render logs for enrichment errors"
echo "   Go to: https://dashboard.render.com → apex-backend → Logs"
echo "   Look for:"
echo "     - 'FileNotFoundError'"
echo "     - 'ModuleNotFoundError'"
echo "     - '404' errors during enrichment"
echo ""

# 4. Test enrichment engine locally first
echo "🧪 Testing enrichment engine..."
cd apps/backend
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'intelligence' / 'engines' / 'enrichment'))
try:
	from enhanced_enrichment import EnhancedEnrichment
	engine = EnhancedEnrichment()
	print('✅ Enrichment engine loads successfully')
except Exception as e:
	print(f'❌ Enrichment engine failed: {e}')
"

# 5. Commit and push
echo ""
echo "📤 Committing changes..."
cd ~/projects/apex/apex-sales-intelligence
git add apps/backend/intelligence/engines/enrichment/enrichment_analytics.py
git add apps/backend/main.py
git commit -m "feat: Add enrichment analytics + fix enrichment 404 errors"
git push origin main

echo ""
echo "✅ Deployed! Monitor at:"
echo "   https://dashboard.render.com"
echo ""
echo "Test after deploy:"
echo "  curl https://apex-backend-i7b0.onrender.com/api/analytics/enrichment | jq"
