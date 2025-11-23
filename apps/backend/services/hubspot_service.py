#!/usr/bin/env python3

#!/usr/bin/env python3
"""
HubSpot Contact Data Mapper
Comprehensive field mapping with data validation, cleaning, and profile picture retrieval
"""

from typing import Dict, Optional, List
import re
import requests
from datetime import datetime

class HubSpotContactMapper:
	"""Maps and validates HubSpot contact data"""
	
	# All HubSpot properties to request (YOUR EXACT LIST + standard fields)
	HUBSPOT_PROPERTIES = [
		# Identity fields
		"hs_object_id",
		"firstname",
		"lastname",
		"fullname",
		
		# Email & Phone
		"email",
		"phone",
		"mobilephone",
		"homephone",
		"work_phone",
		"hs_mobile_phone",
		
		# Company/Job
		"company",
		"jobtitle",
		"job_title",
		"industry",
		"hs_industry",
		"company_size",
		"annualrevenue",
		
		# LinkedIn - YOUR SPECIFIC FIELD
		"hs_linkedin_url",  # Primary LinkedIn field
		"linkedin_url",
		"linkedinbio",
		"hs_linkedinid",
		"linkedin_profile_url",
		"linkedin",
		"linked_in",
		
		# Sales Navigator & LinkedIn Extended
		"sales_nav_url",
		"linkedin_connection_date",
		
		# Address
		"address",
		"city",
		"state",
		"zip",
		"country",
		
		# Lifecycle & Status
		"lifecyclestage",
		"hs_lead_status",
		"lead_status",
		"hubspot_owner_id",
		"hs_owner_id",
		"contact_unworked",  # YOUR FIELD
		
		# Dates - YOUR SPECIFIC FIELDS
		"birthday",
		"createdate",
		"lastmodifieddate",
		"notes_last_updated",
		"last_activity_date",
		"last_engagement_date",
		"hs_last_engagement_date",
		"person_last_email_received",  # YOUR FIELD
		
		# Activity Metrics - YOUR SPECIFIC FIELDS
		"number_of_sales_activities",  # YOUR FIELD
		"number_of_times_contacted",   # YOUR FIELD
		"best_time",                   # YOUR FIELD
		"num_contacted_notes",
		"num_notes",
		"hs_sales_email_last_replied",
		"recent_deal_amount",
		"recent_deal_close_date",
		
		# Social
		"twitterhandle",
		"twitter",
		"facebook_url",
		"instagram_url",
		
		# Additional
		"website",
		"company_website",
		"notes",
		"description"
	]
	
	def __init__(self, hubspot_token: Optional[str] = None):
		self.data_quality_issues = []
		self.hubspot_token = hubspot_token
		
	def map_contact(self, hubspot_contact: Dict, fetch_profile_pic: bool = True) -> Dict:
		"""
		Map HubSpot contact to our internal format with profile picture
		"""
		props = hubspot_contact.get('properties', {})
		contact_id = hubspot_contact.get('id')
		
		self.data_quality_issues = []
		
		# Build contact data
		contact_data = {
			'hubspot_id': contact_id,
			'hs_object_id': self._get_first_non_empty(props, ['hs_object_id']) or contact_id,
			
			# Name
			'first_name': self._clean_text(self._get_first_non_empty(props, ['firstname'])),
			'last_name': self._clean_text(self._get_first_non_empty(props, ['lastname'])),
			'name': '',
			
			# Email & Phone
			'email': self._validate_email(self._get_first_non_empty(props, ['email'])),
			'phone': self._clean_phone(self._get_first_non_empty(props, ['mobilephone', 'phone', 'work_phone', 'hs_mobile_phone'])),
			'mobile_phone': self._clean_phone(self._get_first_non_empty(props, ['mobilephone', 'hs_mobile_phone'])),
			
			# Company/Job
			'company': self._clean_text(self._get_first_non_empty(props, ['company'])),
			'title': self._clean_text(self._get_first_non_empty(props, ['jobtitle', 'job_title'])),
			'industry': self._clean_text(self._get_first_non_empty(props, ['industry', 'hs_industry'])),
			
			# LinkedIn - PRIORITIZE hs_linkedin_url
			'linkedin_url': self._validate_linkedin(self._get_first_non_empty(props, [
				'hs_linkedin_url',  # YOUR PRIMARY FIELD
				'linkedin_url',
				'linkedin_profile_url',
				'linkedinbio',
				'linkedin',
				'linked_in'
			])),
			'sales_nav_url': self._clean_text(self._get_first_non_empty(props, ['sales_nav_url'])),
			'linkedin_connection_date': self._parse_date(props.get('linkedin_connection_date')),
			
			# Lifecycle
			'lifecycle_stage': self._get_first_non_empty(props, ['lifecyclestage']),
			'lead_status': self._get_first_non_empty(props, ['hs_lead_status', 'lead_status']),
			'hubspot_owner_id': self._get_first_non_empty(props, ['hubspot_owner_id', 'hs_owner_id']),
			'contact_unworked': self._parse_boolean(props.get('contact_unworked')),
			
			# Dates
			'birthday': self._parse_date(props.get('birthday')),
			'created_at': self._parse_date(props.get('createdate')),
			'updated_at': self._parse_date(props.get('lastmodifieddate')),
			'last_activity_date': self._parse_date(props.get('last_activity_date')),
			'last_engagement_date': self._parse_date(self._get_first_non_empty(props, ['last_engagement_date', 'hs_last_engagement_date'])),
			'last_email_received': self._parse_date(props.get('person_last_email_received')),
			
			# Activity Metrics
			'num_sales_activities': self._parse_int(props.get('number_of_sales_activities')),
			'num_times_contacted': self._parse_int(props.get('number_of_times_contacted')),
			'best_time': self._clean_text(props.get('best_time')),
			
			# Profile Picture
			'profile_picture_url': None,  # Will be fetched if available
			
			# Data Quality
			'data_quality_score': 0,
			'data_quality_issues': []
		}
		
		# Compute full name
		contact_data['name'] = self._build_full_name(
			contact_data['first_name'],
			contact_data['last_name'],
			contact_data['email']
		)
		
		# Fetch profile picture if token provided
		if fetch_profile_pic and self.hubspot_token and contact_id:
			profile_pic_url = self._fetch_profile_picture(contact_id)
			if profile_pic_url:
				contact_data['profile_picture_url'] = profile_pic_url
				
		# Calculate data quality
		contact_data['data_quality_score'] = self._calculate_quality_score(contact_data)
		contact_data['data_quality_issues'] = self.data_quality_issues.copy()
		
		return contact_data
	
	def _fetch_profile_picture(self, contact_id: str) -> Optional[str]:
		"""
		Fetch profile picture from HubSpot File Manager via associations
		Association Type ID: 1061 (CONTACT_TO_FILE_MANAGER_FILE)
		"""
		try:
			# Step 1: Get associated files
			associations_url = f"https://api.hubapi.com/crm/v4/objects/contacts/{contact_id}/associations/file_manager_file"
			
			headers = {
				'Authorization': f"Bearer {self.hubspot_token}",
				'Content-Type': 'application/json'
			}
			
			response = requests.get(associations_url, headers=headers, timeout=10)
			
			if response.status_code != 200:
				return None
			
			associations = response.json()
			results = associations.get('results', [])
			
			if not results:
				return None
			
			# Get first associated file ID
			file_id = results[0].get('toObjectId')
			
			if not file_id:
				return None
			
			# Step 2: Get file details from File Manager
			file_url = f"https://api.hubapi.com/filemanager/api/v3/files/{file_id}"
			
			file_response = requests.get(file_url, headers=headers, timeout=10)
			
			if file_response.status_code != 200:
				return None
			
			file_data = file_response.json()
			
			# Get the file URL
			profile_pic_url = file_data.get('url')
			
			if profile_pic_url:
				print(f"      📷 Found profile picture for contact {contact_id}")
				return profile_pic_url
			
			return None
		
		except Exception as e:
			print(f"      ⚠️  Error fetching profile picture: {e}")
			return None
		
	def _get_first_non_empty(self, props: Dict, fields: List[str]) -> Optional[str]:
		"""Get first non-empty value from list of possible fields"""
		for field in fields:
			value = props.get(field)
			if value and str(value).strip():
				return str(value).strip()
		return None
	
	def _clean_text(self, text: Optional[str]) -> Optional[str]:
		"""Clean text field"""
		if not text:
			return None
		
		text = ' '.join(text.split())
		text = text.replace('null', '').replace('None', '').replace('N/A', '')
		
		return text.strip() if text.strip() else None
	
	def _validate_email(self, email: Optional[str]) -> Optional[str]:
		"""Validate email format"""
		if not email:
			self.data_quality_issues.append("Missing email")
			return None
		
		email = email.lower().strip()
		
		email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
		if not re.match(email_pattern, email):
			self.data_quality_issues.append(f"Invalid email format: {email}")
			return None
		
		return email
	
	def _clean_phone(self, phone: Optional[str]) -> Optional[str]:
		"""Clean phone number"""
		if not phone:
			return None
		
		digits = re.sub(r'\D', '', phone)
		
		if len(digits) < 10:
			return None
		
		return phone
	
	def _validate_linkedin(self, linkedin: Optional[str]) -> Optional[str]:
		"""
		Validate and clean LinkedIn URL
		USES hs_linkedin_url as primary source
		"""
		if not linkedin:
			self.data_quality_issues.append("Missing LinkedIn URL")
			return None
		
		linkedin = linkedin.strip()
		
		# LinkedIn URL patterns
		valid_patterns = [
			r'https?://(?:www\.)?linkedin\.com/in/([a-zA-Z0-9\-]+)/?',
			r'linkedin\.com/in/([a-zA-Z0-9\-]+)/?',
			r'in/([a-zA-Z0-9\-]+)/?'
		]
		
		for pattern in valid_patterns:
			match = re.search(pattern, linkedin, re.IGNORECASE)
			if match:
				username = match.group(1)
				clean_url = f"https://www.linkedin.com/in/{username}/"
				
				if clean_url != linkedin:
					print(f"      🔧 Cleaned LinkedIn: {linkedin} → {clean_url}")
					
				return clean_url
			
		self.data_quality_issues.append(f"Invalid LinkedIn URL: {linkedin}")
		print(f"      ⚠️  Invalid LinkedIn URL: {linkedin}")
		return None
	
	def _parse_date(self, date_value: Optional[str]) -> Optional[str]:
		"""Parse date to ISO format"""
		if not date_value:
			return None
		
		try:
			# HubSpot typically uses ISO format or timestamp
			if isinstance(date_value, int):
				# Timestamp in milliseconds
				dt = datetime.fromtimestamp(date_value / 1000)
				return dt.isoformat()
			elif isinstance(date_value, str):
				return date_value
			return None
		except:
			return None
		
	def _parse_int(self, value: Optional[str]) -> Optional[int]:
		"""Parse integer value"""
		if not value:
			return None
		try:
			return int(value)
		except:
			return None
		
	def _parse_boolean(self, value: Optional[str]) -> Optional[bool]:
		"""Parse boolean value"""
		if value is None:
			return None
		
		if isinstance(value, bool):
			return value
		
		if isinstance(value, str):
			return value.lower() in ['true', '1', 'yes']
		
		return bool(value)
	
	def _build_full_name(self, first: Optional[str], last: Optional[str], email: Optional[str]) -> str:
		"""Build full name with fallback"""
		if first and last:
			return f"{first} {last}"
		elif first:
			return first
		elif last:
			return last
		elif email:
			return email.split('@')[0].replace('.', ' ').replace('_', ' ').title()
		else:
			return "Unknown"
		
	def _calculate_quality_score(self, contact: Dict) -> int:
		"""Calculate data quality score (0-100)"""
		score = 0
		
		# Required (50 points)
		if contact.get('email'): score += 20
		if contact.get('company'): score += 15
		if contact.get('name') and contact['name'] != 'Unknown': score += 15
		
		# Important (30 points)
		if contact.get('linkedin_url'): score += 10
		if contact.get('phone'): score += 10
		if contact.get('title'): score += 10
		
		# Nice to have (20 points)
		if contact.get('industry'): score += 5
		if contact.get('profile_picture_url'): score += 5
		if contact.get('num_sales_activities'): score += 5
		if contact.get('last_engagement_date'): score += 5
		
		return min(score, 100)
	
	@classmethod
	def get_all_properties(cls) -> List[str]:
		"""Get list of all HubSpot properties to request"""
		return cls.HUBSPOT_PROPERTIES
	
	
def map_hubspot_contact(hubspot_contact: Dict, hubspot_token: Optional[str] = None) -> Dict:
	"""Convenience function"""
	mapper = HubSpotContactMapper(hubspot_token)
	return mapper.map_contact(hubspot_contact)
