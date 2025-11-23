#!/usr/bin/env python3

#!/usr/bin/env python3
"""
Cadence Router - Automatically assigns cadences based on lead tier
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class CadenceRouter:
	"""Routes contacts to appropriate cadence based on scoring/tier"""
	
	# Cadence definitions
	CADENCE_DEFINITIONS = {
		'aggressive': {
			'name': 'Aggressive Outreach',
			'duration_days': 7,
			'description': 'High-touch sequence for hot leads',
			'touches': [
				{'day': 0, 'type': 'email', 'variant': 1},
				{'day': 1, 'type': 'call', 'variant': 1},
				{'day': 3, 'type': 'email', 'variant': 2},
				{'day': 5, 'type': 'call', 'variant': 2},
				{'day': 7, 'type': 'email', 'variant': 3}
			]
		},
		'standard': {
			'name': 'Standard Follow-Up',
			'duration_days': 14,
			'description': 'Balanced approach for warm/qualified leads',
			'touches': [
				{'day': 0, 'type': 'email', 'variant': 1},
				{'day': 3, 'type': 'email', 'variant': 2},
				{'day': 7, 'type': 'call', 'variant': 1},
				{'day': 10, 'type': 'email', 'variant': 3},
				{'day': 14, 'type': 'call', 'variant': 2}
			]
		},
		'nurture': {
			'name': 'Long-Term Nurture',
			'duration_days': 30,
			'description': 'Patient approach for cold leads',
			'touches': [
				{'day': 0, 'type': 'email', 'variant': 1},
				{'day': 7, 'type': 'email', 'variant': 2},
				{'day': 14, 'type': 'call', 'variant': 1},
				{'day': 21, 'type': 'email', 'variant': 3},
				{'day': 30, 'type': 'call', 'variant': 2}
			]
		}
	}
	
	# Tier to cadence mapping
	TIER_TO_CADENCE = {
		'HOT': 'aggressive',
		'WARM': 'standard',
		'QUALIFIED': 'standard',
		'COLD': 'nurture'
	}
	
	def __init__(self, db_path: str = './apex.db'):
		self.db_path = db_path
		
	def get_db(self):
		"""Get database connection"""
		return sqlite3.connect(self.db_path)
	
	def route_contact(self, contact_id: int) -> Optional[int]:
		"""
		Auto-route contact to appropriate cadence based on tier
		Returns sequence_id if successful
		"""
		# Get contact details
		contact = self._get_contact(contact_id)
		
		if not contact:
			print(f"❌ Contact {contact_id} not found")
			return None
		
		# Determine cadence type from tier
		tier = contact.get('lead_tier', 'COLD')
		cadence_type = self.TIER_TO_CADENCE.get(tier, 'standard')
		
		print(f"\n🎯 Routing Contact: {contact['name']}")
		print(f"   Tier: {tier}")
		print(f"   Assigned Cadence: {cadence_type}")
		
		# Start sequence
		sequence_id = self.start_sequence(contact_id, cadence_type)
		
		return sequence_id
	
	def start_sequence(self, contact_id: int, cadence_type: str) -> int:
		"""Start a cadence sequence for a contact"""
		
		if cadence_type not in self.CADENCE_DEFINITIONS:
			raise ValueError(f"Invalid cadence type: {cadence_type}")
			
		cadence = self.CADENCE_DEFINITIONS[cadence_type]
		
		# Check if contact already has active sequence
		existing = self._get_active_sequence(contact_id)
		if existing:
			print(f"   ⚠️  Contact already has active cadence (ID: {existing['id']})")
			return existing['id']
		
		conn = self.get_db()
		cursor = conn.cursor()
		
		try:
			# Create sequence record
			now = datetime.now().isoformat()
			cursor.execute("""
				INSERT INTO cadence_sequences (
					contact_id, cadence_type, status, current_step, 
					total_steps, started_at, created_at
				)
				VALUES (?, ?, 'active', 0, ?, ?, ?)
			""", (
				contact_id,
				cadence_type,
				len(cadence['touches']),
				now,
				now
			))
			
			sequence_id = cursor.lastrowid
			
			# Schedule all touches
			self._schedule_touches(cursor, sequence_id, contact_id, cadence)
			
			# Update contact record
			cursor.execute("""
				UPDATE contacts 
				SET cadence_id = ?, 
					cadence_status = 'active',
					cadence_started_at = ?
				WHERE id = ?
			""", (sequence_id, now, contact_id))
			
			# Log activity
			self._log_activity(cursor, contact_id, sequence_id, 'cadence_started', {
				'cadence_type': cadence_type,
				'total_touches': len(cadence['touches'])
			})
			
			conn.commit()
			
			print(f"   ✅ Sequence started (ID: {sequence_id})")
			print(f"   📅 {len(cadence['touches'])} touches scheduled")
			
			return sequence_id
		
		except Exception as e:
			conn.rollback()
			print(f"   ❌ Error starting sequence: {e}")
			raise
		finally:
			conn.close()
			
	def _schedule_touches(self, cursor, sequence_id: int, contact_id: int, cadence: Dict):
		"""Schedule all touches for a cadence"""
		start_date = datetime.now()
		
		for step_num, touch in enumerate(cadence['touches'], 1):
			scheduled_date = start_date + timedelta(days=touch['day'])
			
			cursor.execute("""
				INSERT INTO cadence_touches (
					sequence_id, contact_id, step_number, touch_type,
					variant_number, scheduled_for, status, created_at
				)
				VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
			""", (
				sequence_id,
				contact_id,
				step_num,
				touch['type'],
				touch['variant'],
				scheduled_date.isoformat(),
				datetime.now().isoformat()
			))
			
	def _get_contact(self, contact_id: int) -> Optional[Dict]:
		"""Get contact details"""
		conn = self.get_db()
		cursor = conn.cursor()
		
		cursor.execute("""
			SELECT id, name, email, company, lead_tier, opportunity_score,
					enrichment_status, enrichment_data
			FROM contacts
			WHERE id = ?
		""", (contact_id,))
		
		row = cursor.fetchone()
		conn.close()
		
		if not row:
			return None
		
		return {
			'id': row[0],
			'name': row[1],
			'email': row[2],
			'company': row[3],
			'lead_tier': row[4],
			'opportunity_score': row[5],
			'enrichment_status': row[6],
			'enrichment_data': row[7]
		}
	
	def _get_active_sequence(self, contact_id: int) -> Optional[Dict]:
		"""Check if contact has active sequence"""
		conn = self.get_db()
		cursor = conn.cursor()
		
		cursor.execute("""
			SELECT id, cadence_type, current_step, total_steps
			FROM cadence_sequences
			WHERE contact_id = ? AND status = 'active'
		""", (contact_id,))
		
		row = cursor.fetchone()
		conn.close()
		
		if not row:
			return None
		
		return {
			'id': row[0],
			'cadence_type': row[1],
			'current_step': row[2],
			'total_steps': row[3]
		}
	
	def _log_activity(self, cursor, contact_id: int, sequence_id: int, 
					activity_type: str, data: Dict):
		"""Log cadence activity"""
		cursor.execute("""
			INSERT INTO cadence_activities (
				contact_id, sequence_id, activity_type, activity_data, created_at
			)
			VALUES (?, ?, ?, ?, ?)
		""", (
			contact_id,
			sequence_id,
			activity_type,
			json.dumps(data),
			datetime.now().isoformat()
		))
		
	def get_sequence_status(self, sequence_id: int) -> Optional[Dict]:
		"""Get detailed status of a sequence"""
		conn = self.get_db()
		cursor = conn.cursor()
		
		# Get sequence info
		cursor.execute("""
			SELECT cs.*, c.name, c.email
			FROM cadence_sequences cs
			JOIN contacts c ON cs.contact_id = c.id
			WHERE cs.id = ?
		""", (sequence_id,))
		
		seq_row = cursor.fetchone()
		
		if not seq_row:
			conn.close()
			return None
		
		# Get touches
		cursor.execute("""
			SELECT step_number, touch_type, variant_number, 
					scheduled_for, executed_at, status
			FROM cadence_touches
			WHERE sequence_id = ?
			ORDER BY step_number
		""", (sequence_id,))
		
		touches = cursor.fetchall()
		conn.close()
		
		return {
			'sequence_id': seq_row[0],
			'contact_id': seq_row[1],
			'contact_name': seq_row[12],
			'contact_email': seq_row[13],
			'cadence_type': seq_row[2],
			'status': seq_row[3],
			'current_step': seq_row[4],
			'total_steps': seq_row[5],
			'started_at': seq_row[6],
			'touches': [
				{
					'step': t[0],
					'type': t[1],
					'variant': t[2],
					'scheduled': t[3],
					'executed': t[4],
					'status': t[5]
				}
				for t in touches
			]
		}
	
	def pause_sequence(self, sequence_id: int, reason: str = 'manual'):
		"""Pause an active sequence"""
		conn = self.get_db()
		cursor = conn.cursor()
		
		cursor.execute("""
			UPDATE cadence_sequences
			SET status = 'paused', stop_reason = ?
			WHERE id = ? AND status = 'active'
		""", (reason, sequence_id))
		
		# Update contact
		cursor.execute("""
			UPDATE contacts
			SET cadence_status = 'paused'
			WHERE cadence_id = ?
		""", (sequence_id,))
		
		conn.commit()
		conn.close()
		
		print(f"⏸️  Sequence {sequence_id} paused: {reason}")
		
	def stop_sequence(self, sequence_id: int, reason: str = 'manual'):
		"""Stop a sequence permanently"""
		conn = self.get_db()
		cursor = conn.cursor()
		
		now = datetime.now().isoformat()
		
		cursor.execute("""
			UPDATE cadence_sequences
			SET status = 'stopped', stop_reason = ?, completed_at = ?
			WHERE id = ?
		""", (reason, now, sequence_id))
		
		# Cancel pending touches
		cursor.execute("""
			UPDATE cadence_touches
			SET status = 'skipped'
			WHERE sequence_id = ? AND status = 'pending'
		""", (sequence_id,))
		
		# Update contact
		cursor.execute("""
			UPDATE contacts
			SET cadence_status = 'none'
			WHERE cadence_id = ?
		""", (sequence_id,))
		
		conn.commit()
		conn.close()
		
		print(f"🛑 Sequence {sequence_id} stopped: {reason}")
		
		
def test_router():
	"""Test the cadence router"""
	router = CadenceRouter()
	
	# Test with a contact
	print("\n" + "="*60)
	print("🧪 TESTING CADENCE ROUTER")
	print("="*60)
	
	# Get a contact to test
	conn = router.get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT id, name, lead_tier FROM contacts LIMIT 1")
	row = cursor.fetchone()
	conn.close()
	
	if row:
		contact_id, name, tier = row
		print(f"\nTest Contact: {name} (ID: {contact_id}, Tier: {tier})")
		
		# Route contact
		sequence_id = router.route_contact(contact_id)
		
		if sequence_id:
			# Get status
			status = router.get_sequence_status(sequence_id)
			
			print(f"\n📊 Sequence Status:")
			print(f"   Type: {status['cadence_type']}")
			print(f"   Status: {status['status']}")
			print(f"   Progress: {status['current_step']}/{status['total_steps']}")
			print(f"\n📅 Scheduled Touches:")
			for touch in status['touches']:
				print(f"   Step {touch['step']}: {touch['type']} (variant {touch['variant']}) - {touch['scheduled'][:10]}")
	else:
		print("❌ No contacts found in database")
		
if __name__ == "__main__":
	test_router()
	