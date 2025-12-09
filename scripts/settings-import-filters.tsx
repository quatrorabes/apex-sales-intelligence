#!/bin/bash

# Create patch file
cat > ~/projects/apex/backend/api/import_filters.py << 'EOF'
"""
Import Filters API - Smart Contact Qualification
Handles saving/loading import rules and validating contacts before import
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json

# Import database models (add to your existing database.py)
from database import SessionLocal, ImportFilters, engine
from sqlalchemy import Column, Integer, String, JSON, DateTime, Text

import_bp = Blueprint('import_filters', __name__)

# ========== API ENDPOINTS ==========

@import_bp.route('/api/import/filters', methods=['GET', 'POST'])
def import_filters_endpoint():
	"""Save or load import qualification rules"""
	db = SessionLocal()
	
	try:
		if request.method == 'POST':
			filters = request.json
			print(f"📥 Saving import filters: {json.dumps(filters, indent=2)}")
			
			# Upsert to database
			existing = db.query(ImportFilters).filter_by(user_id=1).first()
			if existing:
				existing.filters_json = json.dumps(filters)
				existing.updated_at = datetime.utcnow()
				print("✅ Updated existing filters")
			else:
				new_filter = ImportFilters(
					user_id=1,
					filters_json=json.dumps(filters),
					created_at=datetime.utcnow(),
					updated_at=datetime.utcnow()
				)
				db.add(new_filter)
				print("✅ Created new filters")
			
			db.commit()
			return jsonify({'success': True, 'message': 'Import filters saved'})
		
		else:
			# GET - Return saved filters
			saved = db.query(ImportFilters).filter_by(user_id=1).first()
			if saved:
				filters = json.loads(saved.filters_json)
				print(f"✅ Loaded saved filters for user 1")
				return jsonify(filters)
			else:
				# Return smart defaults
				defaults = {
					'requiredFields': {
						'name': True,
						'company': True
					},
					'recommendedFields': {
						'linkedin_url': True,
						'email': True,
						'phone': True
					},
					'leadStatus': ['Qualified', 'Working'],
					'lifecycleStage': ['SQL', 'Opportunity', 'Customer'],
					'customFilters': []
				}
				print("📋 No saved filters, returning defaults")
				return jsonify(defaults)
	
	finally:
		db.close()


@import_bp.route('/api/import/validate', methods=['POST'])
def validate_import_endpoint():
	"""
	Validate contacts against import rules BEFORE inserting to database
	Returns: {total, qualified, rejected, warnings}
	"""
	contacts = request.json.get('contacts', [])
	print(f"🔍 Validating {len(contacts)} contacts...")
	
	# Get saved filters
	db = SessionLocal()
	saved = db.query(ImportFilters).filter_by(user_id=1).first()
	db.close()
	
	if saved:
		filters = json.loads(saved.filters_json)
	else:
		# Use defaults if no filters saved
		filters = {
			'leadStatus': ['Qualified', 'Working'],
			'lifecycleStage': ['SQL', 'Opportunity', 'Customer'],
			'customFilters': []
		}
	
	results = {
		'total': len(contacts),
		'qualified': [],
		'rejected': [],
		'warnings': []
	}
	
	for contact in contacts:
		validation = validate_contact(contact, filters)
		
		if validation['status'] == 'reject':
			results['rejected'].append({
				'contact': contact,
				'reason': validation['reason']
			})
		elif validation['status'] == 'warn':
			results['warnings'].append({
				'contact': contact,
				'missing_fields': validation.get('missing_fields', [])
			})
			results['qualified'].append(contact)
		else:
			results['qualified'].append(contact)
	
	summary = f"✅ Validation complete: {len(results['qualified'])}/{len(contacts)} qualified, " \
				f"{len(results['rejected'])} rejected, {len(results['warnings'])} warnings"
	print(summary)
	
	return jsonify(results)


# ========== VALIDATION LOGIC ==========

def validate_contact(contact: dict, filters: dict) -> dict:
	"""
	Core validation logic - returns {'status': 'pass'|'warn'|'reject', 'reason': '...'}
	"""
	
	# CRITICAL: Check required fields
	if not contact.get('name') or not str(contact.get('name')).strip():
		return {
			'status': 'reject',
			'reason': 'Missing required field: name'
		}
	
	if not contact.get('company') or not str(contact.get('company')).strip():
		return {
			'status': 'reject',
			'reason': 'Missing required field: company'
		}
	
	# Check Lead Status filter
	if filters.get('leadStatus'):
		contact_status = contact.get('lead_status') or contact.get('leadstatus')
		if contact_status and contact_status not in filters['leadStatus']:
			return {
				'status': 'reject',
				'reason': f"Lead status '{contact_status}' not in allowed list: {', '.join(filters['leadStatus'])}"
			}
	
	# Check Lifecycle Stage filter (most important)
	if filters.get('lifecycleStage'):
		contact_stage = contact.get('lifecycle_stage') or contact.get('lifecyclestage')
		if contact_stage and contact_stage not in filters['lifecycleStage']:
			return {
				'status': 'reject',
				'reason': f"Lifecycle stage '{contact_stage}' not in allowed list: {', '.join(filters['lifecycleStage'])}"
			}
	
	# Check custom filters
	for custom in filters.get('customFilters', []):
		if not custom.get('property') or not custom.get('operator'):
			continue
			
		property_name = custom['property']
		operator = custom['operator']
		expected_value = custom['value']
		
		# Get actual value (try different case variations)
		actual_value = (contact.get(property_name) or 
						contact.get(property_name.lower()) or 
						contact.get(property_name.replace('_', '')))
		
		if operator == 'equals':
			if str(actual_value) != str(expected_value):
				return {
					'status': 'reject',
					'reason': f"{property_name} must equal '{expected_value}' (got '{actual_value}')"
				}
		
		elif operator == 'contains':
			if expected_value not in str(actual_value or ''):
				return {
					'status': 'reject',
					'reason': f"{property_name} must contain '{expected_value}'"
				}
		
		elif operator == 'not_empty':
			if not actual_value or str(actual_value).strip() == '':
				return {
					'status': 'reject',
					'reason': f"{property_name} cannot be empty"
				}
		
		elif operator == 'greater_than':
			try:
				if float(actual_value or 0) <= float(expected_value):
					return {
						'status': 'reject',
						'reason': f"{property_name} must be > {expected_value}"
					}
			except (ValueError, TypeError):
				return {
					'status': 'reject',
					'reason': f"{property_name} is not a valid number"
				}
	
	# Check recommended fields (warning only, not rejection)
	missing_recommended = []
	if filters.get('recommendedFields', {}).get('linkedin_url'):
		if not contact.get('linkedin_url') and not contact.get('linkedinurl'):
			missing_recommended.append('LinkedIn URL')
	
	if filters.get('recommendedFields', {}).get('email'):
		if not contact.get('email'):
			missing_recommended.append('Email')
	
	if filters.get('recommendedFields', {}).get('phone'):
		if not contact.get('phone') and not contact.get('phone_number'):
			missing_recommended.append('Phone')
	
	if missing_recommended:
		return {
			'status': 'warn',
			'missing_fields': missing_recommended
		}
	
	# All checks passed
	return {'status': 'pass'}


# ========== HELPER FUNCTIONS ==========

def get_import_filters() -> dict:
	"""Helper to get current import filters"""
	db = SessionLocal()
	saved = db.query(ImportFilters).filter_by(user_id=1).first()
	db.close()
	
	if saved:
		return json.loads(saved.filters_json)
	else:
		return {
			'leadStatus': ['Qualified', 'Working'],
			'lifecycleStage': ['SQL', 'Opportunity', 'Customer'],
			'customFilters': []
		}
EOF