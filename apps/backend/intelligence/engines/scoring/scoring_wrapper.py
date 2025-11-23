#!/usr/bin/ruby

"""
Scoring Wrapper - Standalone module to handle scoring logic
This wraps the actual scoring engines and provides a simple interface
"""
import sys
import os
import sqlite3
from datetime import datetime
import json

# Add backend path
BACKEND_PATH = '/Users/chrisrabenold/projects/apex/apps/backend'
sys.path.insert(0, BACKEND_PATH)
sys.path.insert(0, os.path.join(BACKEND_PATH, 'intelligence', 'engines'))

# Try to import the scoring engines
try:
	from apex_intelligence_engine import ApexScoringEngine
	APEX_ENGINE_AVAILABLE = True
except ImportError:
	try:
		from intelligence.engines.apex_intelligence_engine import ApexScoringEngine
		APEX_ENGINE_AVAILABLE = True
	except ImportError:
		APEX_ENGINE_AVAILABLE = False
		ApexScoringEngine = None
		
try:
	from scoring_orchestrator import ScoringOrchestrator
	ORCHESTRATOR_AVAILABLE = True
except ImportError:
	try:
		from intelligence.engines.scoring_orchestrator import ScoringOrchestrator
		ORCHESTRATOR_AVAILABLE = True
	except ImportError:
		ORCHESTRATOR_AVAILABLE = False
		ScoringOrchestrator = None
		

def score_contact_simple(contact_dict):
	"""
	Simple scoring function that works with just contact data
	Returns scores even if engines aren't available
	"""
	# Default fallback scoring
	default_score = {
		'mdcp_score': 0,
		'mdcp_tier': 'UNKNOWN',
		'rss_score': 0,
		'rss_tier': 'UNKNOWN',
		'priority_score': 0,
		'urgency_level': 'LOW',
		'recommended_action': 'Review contact manually',
		'calculation_version': 'fallback_v1',
		'timestamp': datetime.now().isoformat()
	}

	# If no engines available, use basic heuristic scoring
	if not APEX_ENGINE_AVAILABLE:
		# Simple heuristic based on available data
		score = 50  # Base score
		
		# Add points for data completeness
		if contact_dict.get('email'): score += 10
		if contact_dict.get('phone'): score += 10
		if contact_dict.get('company'): score += 10
		if contact_dict.get('title'): score += 10
		if contact_dict.get('linkedin_url'): score += 10
		
		# Determine tier
		if score >= 80:
			tier = 'HOT'
			urgency = 'IMMEDIATE'
		elif score >= 65:
			tier = 'WARM'
			urgency = 'HIGH'
		elif score >= 50:
			tier = 'QUALIFIED'
			urgency = 'MEDIUM'
		else:
			tier = 'COLD'
			urgency = 'LOW'
			
		return {
			'mdcp_score': score,
			'mdcp_tier': tier,
			'rss_score': score,
			'rss_tier': tier,
			'priority_score': score,
			'urgency_level': urgency,
			'recommended_action': f'{urgency} priority - Contact within 24-48 hours',
			'calculation_version': 'heuristic_v1',
			'timestamp': datetime.now().isoformat()
		}

	# If engines are available, use them
	try:
		engine = ApexScoringEngine()
		result = engine.score(contact_dict)
		return result
	except Exception as e:
		print(f"Error using scoring engine: {e}")
		return default_score
		

def score_contact_from_db(conn, contact_id, trigger='manual'):
	"""
	Score a contact using database connection
	"""
	cursor = conn.cursor()
	
	# Get contact data
	cursor.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
	row = cursor.fetchone()
	
	if not row:
		return {'error': 'Contact not found'}
		
	# Convert to dict
	columns = [desc[0] for desc in cursor.description]
	contact_dict = dict(zip(columns, row))
	
	# Score the contact
	scores = score_contact_simple(contact_dict)
	
	# Update database
	cursor.execute('''
		UPDATE contacts
		SET mdcp_score = ?,
			mdcp_tier = ?,
			rss_score = ?,
			rss_tier = ?,
			priority_score = ?,
			urgency_level = ?,
			recommended_action = ?,
			calculation_version = ?,
			last_scored = ?
		WHERE id = ?
	''', (
		scores.get('mdcp_score'),
		scores.get('mdcp_tier'),
		scores.get('rss_score'),
		scores.get('rss_tier'),
		scores.get('priority_score'),
		scores.get('urgency_level'),
		scores.get('recommended_action'),
		scores.get('calculation_version'),
		scores.get('timestamp'),
		contact_id
	))

	conn.commit()
	
	return {
		'success': True,
		'contact_id': contact_id,
		'scores': scores
	}


def bulk_score_contacts(conn, contact_ids, trigger='batch'):
	"""
	Score multiple contacts in bulk
	"""
	results = []
	
	for contact_id in contact_ids:
		try:
			result = score_contact_from_db(conn, contact_id, trigger)
			results.append(result)
		except Exception as e:
			results.append({
				'contact_id': contact_id,
				'error': str(e)
			})

	return results
	

def get_apex_scores(conn):
	"""
	Get all contacts with Apex scores for the intelligence dashboard
	"""
	cursor = conn.cursor()
	
	cursor.execute('''
		SELECT 
			id, name, company, email,
			lead_type, lifecycle_stage,
			mdcp_score, mdcp_tier,
			rss_score, rss_tier,
			priority_score, urgency_level,
			recommended_action, last_scored
		FROM contacts
		WHERE mdcp_score IS NOT NULL
		ORDER BY priority_score DESC
	''')

	columns = [desc[0] for desc in cursor.description]
	contacts = []
	
	for row in cursor.fetchall():
		contact_dict = dict(zip(columns, row))
		contacts.append(contact_dict)
		
	return {
		'status': 'success',
		'count': len(contacts),
		'contacts': contacts
	}
