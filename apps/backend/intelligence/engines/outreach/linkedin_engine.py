#!/usr/bin/env python3

#!/usr/bin/env python3
"""
APEX SALES INTELLIGENCE - LinkedIn Automation Engine
Safe, compliant LinkedIn outreach at scale
PostgreSQL + Supabase production version
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

class LinkedInEngine:
	"""
	Automated LinkedIn outreach engine - SAFE & COMPLIANT
	Daily Limits:
	- Connection Requests: 20/day
	- Messages: 30/day
	- Profile Views: 100/day
	"""
	
	DAILY_LIMITS = {
		'connection_requests': 20,
		'messages': 30,
		'profile_views': 100,
		'inmails': 10
	}
	
	def __init__(self):
		if not DATABASE_URL:
			raise ValueError("DATABASE_URL required in environment")
			
	def _get_db_connection(self):
		"""Get PostgreSQL connection"""
		return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
	
	def add_prospect(self, linkedin_url: str, contact_id: str, profile_data: Optional[Dict] = None) -> Dict:
		"""Add a LinkedIn prospect"""
		
		conn = self._get_db_connection()
		try:
			cursor = conn.cursor()
			
			cursor.execute("""
				INSERT INTO linkedin_prospects (
					linkedin_url, contact_id, profile_name, headline, company
				) VALUES (%s, %s, %s, %s, %s)
				RETURNING id
			""", (
				linkedin_url,
				contact_id,
				profile_data.get('name') if profile_data else None,
				profile_data.get('headline') if profile_data else None,
				profile_data.get('company') if profile_data else None
			))
			
			prospect_id = cursor.fetchone()['id']
			conn.commit()
			
			logger.info(f"✅ LinkedIn prospect added: {prospect_id}")
			
			return {'success': True, 'prospect_id': str(prospect_id)}
		
		except psycopg2.IntegrityError:
			conn.rollback()
			return {'success': False, 'error': 'Prospect already exists'}
		except Exception as e:
			conn.rollback()
			logger.error(f"Error adding prospect: {str(e)}")
			return {'success': False, 'error': str(e)}
		finally:
			conn.close()
			
	def generate_connection_message(self, prospect_id: str, template_name: str = 'connection_request_1') -> Optional[str]:
		"""Generate personalized connection request from template"""
		
		conn = self._get_db_connection()
		try:
			cursor = conn.cursor()
			
			# Get prospect + contact data
			cursor.execute("""
				SELECT p.*, c.name, c.company as contact_company, c.title
				FROM linkedin_prospects p
				LEFT JOIN contacts c ON p.contact_id = c.id
				WHERE p.id = %s
			""", (prospect_id,))
			
			prospect = cursor.fetchone()
			if not prospect:
				return None
			
			# Get template
			cursor.execute("""
				SELECT message_body FROM linkedin_message_templates
				WHERE template_name = %s
			""", (template_name,))
			
			template = cursor.fetchone()
			if not template:
				return None
			
			# Parse name
			full_name = prospect.get('name') or prospect.get('profile_name') or 'there'
			firstname = full_name.split()[0] if full_name else 'there'
			
			# Personalize message
			message = template['message_body']
			replacements = {
				'{firstname}': firstname,
				'{company}': prospect.get('company') or prospect.get('contact_company') or 'your company',
				'{industry}': 'the industry'  # Could enhance with actual industry data
			}
			
			for key, value in replacements.items():
				message = message.replace(key, value)
				
			return message
		
		except Exception as e:
			logger.error(f"Error generating message: {str(e)}")
			return None
		finally:
			conn.close()
			
	def get_daily_quota_status(self) -> Dict:
		"""Check today's activity against daily limits"""
		
		conn = self._get_db_connection()
		try:
			cursor = conn.cursor()
			today = datetime.now().date()
			quota = {}
			
			for activity_type, limit in self.DAILY_LIMITS.items():
				cursor.execute("""
					SELECT COUNT(*) as count FROM linkedin_activities
					WHERE activity_type = %s
					AND DATE(performed_at) = %s
				""", (activity_type, today))
				
				count = cursor.fetchone()['count']
				remaining = max(0, limit - count)
				
				quota[activity_type] = {
					'used': count,
					'limit': limit,
					'remaining': remaining,
					'percentage': (count / limit * 100) if limit > 0 else 0
				}
				
			return quota
		
		except Exception as e:
			logger.error(f"Error getting quota: {str(e)}")
			return {}
		finally:
			conn.close()
			
	def get_analytics(self) -> Dict:
		"""Get LinkedIn outreach analytics"""
		
		conn = self._get_db_connection()
		try:
			cursor = conn.cursor()
			
			# Total prospects
			cursor.execute("SELECT COUNT(*) as count FROM linkedin_prospects")
			total_prospects = cursor.fetchone()['count']
			
			# Connection requests sent
			cursor.execute("""
				SELECT COUNT(*) as count FROM linkedin_prospects
				WHERE connection_request_sent IS NOT NULL
			""")
			requests_sent = cursor.fetchone()['count']
			
			# Connections accepted
			cursor.execute("""
				SELECT COUNT(*) as count FROM linkedin_prospects
				WHERE connection_status = 'connected'
			""")
			connections_accepted = cursor.fetchone()['count']
			
			# Messages sent
			cursor.execute("""
				SELECT COUNT(*) as count FROM linkedin_activities
				WHERE activity_type = 'messages'
			""")
			messages_sent = cursor.fetchone()['count']
			
			# Responses received
			cursor.execute("""
				SELECT COUNT(*) as count FROM linkedin_prospects
				WHERE last_engaged IS NOT NULL
			""")
			responses = cursor.fetchone()['count']
			
			# Calculate rates
			acceptance_rate = (connections_accepted / requests_sent * 100) if requests_sent > 0 else 0
			response_rate = (responses / messages_sent * 100) if messages_sent > 0 else 0
			
			return {
				'total_prospects': total_prospects,
				'connection_requests_sent': requests_sent,
				'connections_accepted': connections_accepted,
				'acceptance_rate': round(acceptance_rate, 1),
				'messages_sent': messages_sent,
				'responses_received': responses,
				'response_rate': round(response_rate, 1)
			}
		
		except Exception as e:
			logger.error(f"Error getting analytics: {str(e)}")
			return {}
		finally:
			conn.close()
			
	def get_pending_actions(self) -> Dict:
		"""Get today's pending LinkedIn actions"""
		
		conn = self._get_db_connection()
		try:
			cursor = conn.cursor()
			quota = self.get_daily_quota_status()
			
			pending = {
				'connection_requests': [],
				'follow_ups': [],
				'quota': quota
			}
			
			# Get prospects ready for connection requests
			if quota.get('connection_requests', {}).get('remaining', 0) > 0:
				cursor.execute("""
					SELECT * FROM linkedin_prospects
					WHERE connection_request_sent IS NULL
					AND connection_status = 'not_connected'
					ORDER BY created_at DESC
					LIMIT %s
				""", (quota['connection_requests']['remaining'],))
				
				pending['connection_requests'] = [dict(row) for row in cursor.fetchall()]
				
			return pending
		
		except Exception as e:
			logger.error(f"Error getting pending actions: {str(e)}")
			return {}
		finally:
			conn.close()
			