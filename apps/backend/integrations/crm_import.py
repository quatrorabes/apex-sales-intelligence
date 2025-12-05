"""
APEX CRM Import Engine
Supports: HubSpot, Salesforce, Pipedrive, CSV
With validation filters for data quality
"""
import os
import json
import requests
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============= VALIDATION & FILTERS =============

class ContactValidator:
    """Validates and filters contacts during import."""
    
    # Status values that indicate DO NOT CONTACT
    DNC_STATUSES = {
        # HubSpot
        'unqualified', 'bad timing', 'do not contact', 'dnc', 
        'unsubscribed', 'opted out', 'optedout', 'opt-out', 'opt out',
        'bounced', 'invalid', 'spam', 'junk',
        # Salesforce
        'disqualified', 'lost', 'closed lost', 'not interested',
        'do_not_contact', 'do not call', 'blacklist', 'blacklisted',
        # Pipedrive
        'lost', 'deleted', 'rejected',
        # Generic
        'unsubscribe', 'unsubscribed', 'removed', 'inactive', 'dead',
        'competitor', 'not a fit', 'wrong contact', 'no longer there',
    }
    
    # Fields to check for DNC flags
    DNC_FIELDS = [
        'status', 'lead_status', 'hs_lead_status', 'contact_status',
        'email_status', 'subscription_status', 'opt_out', 'do_not_contact',
        'unsubscribed', 'email_opt_out', 'has_opted_out_of_email',
    ]
    
    # Invalid email patterns
    INVALID_EMAIL_PATTERNS = [
        r'.*@example\.com$',
        r'.*@test\.com$',
        r'.*@localhost.*',
        r'^test@.*',
        r'^fake@.*',
        r'^noreply@.*',
        r'^no-reply@.*',
        r'^donotreply@.*',
        r'.*@mailinator\.com$',
        r'.*@tempmail\..*',
        r'.*@guerrillamail\..*',
    ]
    
    def __init__(self, require_email: bool = True, require_company: bool = True, 
                 require_name: bool = True, filter_dnc: bool = True,
                 filter_unsubscribed: bool = True):
        self.require_email = require_email
        self.require_company = require_company
        self.require_name = require_name
        self.filter_dnc = filter_dnc
        self.filter_unsubscribed = filter_unsubscribed
        
        # Stats tracking
        self.stats = {
            'total_processed': 0,
            'passed': 0,
            'filtered_no_email': 0,
            'filtered_no_company': 0,
            'filtered_no_name': 0,
            'filtered_dnc': 0,
            'filtered_unsubscribed': 0,
            'filtered_invalid_email': 0,
        }
    
    def validate(self, contact: Dict, raw: Dict = None) -> Tuple[bool, str]:
        """
        Validate a contact. Returns (is_valid, reason).
        
        Args:
            contact: Normalized contact dict
            raw: Original raw contact data (for checking extra fields)
        """
        self.stats['total_processed'] += 1
        raw = raw or {}
        
        # 1. Check for valid email
        email = (contact.get('email') or '').strip().lower()
        if self.require_email:
            if not email:
                self.stats['filtered_no_email'] += 1
                return False, 'missing_email'
            
            # Check for invalid email patterns
            for pattern in self.INVALID_EMAIL_PATTERNS:
                if re.match(pattern, email, re.IGNORECASE):
                    self.stats['filtered_invalid_email'] += 1
                    return False, 'invalid_email'
            
            # Basic email format check
            if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                self.stats['filtered_invalid_email'] += 1
                return False, 'invalid_email_format'
        
        # 2. Check for company
        company = (contact.get('company') or '').strip()
        if self.require_company and not company:
            self.stats['filtered_no_company'] += 1
            return False, 'missing_company'
        
        # 3. Check for name
        name = contact.get('name') or ''
        first_name = contact.get('first_name') or ''
        last_name = contact.get('last_name') or ''
        has_name = bool(name.strip() or first_name.strip() or last_name.strip())
        
        if self.require_name and not has_name:
            self.stats['filtered_no_name'] += 1
            return False, 'missing_name'
        
        # 4. Check for DNC / Unqualified status
        if self.filter_dnc or self.filter_unsubscribed:
            # Check normalized contact fields
            for field in self.DNC_FIELDS:
                value = str(contact.get(field) or '').lower().strip()
                if value in self.DNC_STATUSES:
                    self.stats['filtered_dnc'] += 1
                    return False, f'dnc_status:{value}'
            
            # Check raw data fields (CRM-specific)
            for field in self.DNC_FIELDS:
                value = str(raw.get(field) or '').lower().strip()
                if value in self.DNC_STATUSES:
                    self.stats['filtered_dnc'] += 1
                    return False, f'dnc_status:{value}'
            
            # Check for boolean DNC flags
            dnc_bool_fields = [
                'do_not_contact', 'donotcontact', 'dnc', 
                'opt_out', 'optout', 'opted_out', 'optedout',
                'unsubscribed', 'email_opt_out', 'has_opted_out_of_email',
                'email_unsubscribed', 'is_unsubscribed',
            ]
            for field in dnc_bool_fields:
                # Check both contact and raw
                for data in [contact, raw]:
                    value = data.get(field)
                    if value in [True, 'true', 'True', '1', 1, 'yes', 'Yes']:
                        self.stats['filtered_unsubscribed'] += 1
                        return False, f'unsubscribed:{field}'
            
            # HubSpot specific checks
            if raw.get('properties'):
                props = raw['properties']
                # Check hs_email_optout
                if props.get('hs_email_optout') in ['true', True, '1']:
                    self.stats['filtered_unsubscribed'] += 1
                    return False, 'hs_email_optout'
                # Check hs_lead_status
                lead_status = str(props.get('hs_lead_status') or '').lower()
                if lead_status in self.DNC_STATUSES:
                    self.stats['filtered_dnc'] += 1
                    return False, f'hs_lead_status:{lead_status}'
            
            # Salesforce specific checks
            if raw.get('HasOptedOutOfEmail') in [True, 'true']:
                self.stats['filtered_unsubscribed'] += 1
                return False, 'sf_has_opted_out'
            if raw.get('DoNotCall') in [True, 'true']:
                self.stats['filtered_dnc'] += 1
                return False, 'sf_do_not_call'
        
        # Passed all checks
        self.stats['passed'] += 1
        return True, 'valid'
    
    def get_stats(self) -> Dict:
        """Return validation statistics."""
        return self.stats.copy()


class CRMImporter:
    """Base class for CRM imports."""
    
    def __init__(self):
        self.imported_count = 0
        self.failed_count = 0
        self.filtered_count = 0
        self.errors = []
        self.validator = ContactValidator()
    
    def set_validation_rules(self, require_email: bool = True, require_company: bool = True,
                             require_name: bool = True, filter_dnc: bool = True,
                             filter_unsubscribed: bool = True):
        """Configure validation rules."""
        self.validator = ContactValidator(
            require_email=require_email,
            require_company=require_company,
            require_name=require_name,
            filter_dnc=filter_dnc,
            filter_unsubscribed=filter_unsubscribed
        )
    
    def normalize_contact(self, raw: Dict) -> Dict:
        """Override in subclasses to normalize contact data."""
        raise NotImplementedError
    
    def validate_and_normalize(self, raw: Dict) -> Tuple[Optional[Dict], str]:
        """Normalize and validate a contact."""
        try:
            normalized = self.normalize_contact(raw)
            is_valid, reason = self.validator.validate(normalized, raw)
            
            if is_valid:
                return normalized, 'valid'
            else:
                self.filtered_count += 1
                return None, reason
        except Exception as e:
            self.errors.append(str(e))
            return None, f'error:{str(e)}'
    
    def get_result(self) -> Dict:
        return {
            'imported': self.imported_count,
            'filtered': self.filtered_count,
            'failed': self.failed_count,
            'errors': self.errors[:10],
            'validation_stats': self.validator.get_stats(),
        }


class HubSpotImporter(CRMImporter):
    """Import contacts from HubSpot CRM."""
    
    BASE_URL = "https://api.hubapi.com"
    
    def __init__(self, api_key: str = None, access_token: str = None):
        super().__init__()
        self.api_key = api_key or os.getenv('HUBSPOT_API_KEY')
        self.access_token = access_token or os.getenv('HUBSPOT_ACCESS_TOKEN')
        
    def _get_headers(self) -> Dict:
        if self.access_token:
            return {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
        return {'Content-Type': 'application/json'}
    
    def _get_params(self) -> Dict:
        if self.api_key and not self.access_token:
            return {'hapikey': self.api_key}
        return {}
    
    def fetch_contacts(self, limit: int = 100, after: str = None) -> Dict:
        """Fetch contacts from HubSpot."""
        url = f"{self.BASE_URL}/crm/v3/objects/contacts"
        params = {
            'limit': min(limit, 100),
            'properties': ','.join([
                'firstname', 'lastname', 'email', 'phone', 'company', 'jobtitle',
                'linkedinbio', 'hs_lead_status', 'hs_email_optout', 'lifecyclestage',
                'hs_content_membership_status', 'hs_email_bounce', 'hs_email_hard_bounce_reason'
            ]),
            **self._get_params()
        }
        if after:
            params['after'] = after
            
        response = requests.get(url, headers=self._get_headers(), params=params)
        
        if response.status_code != 200:
            raise Exception(f"HubSpot API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def fetch_all_contacts(self, max_contacts: int = 1000) -> List[Dict]:
        """Fetch all contacts with pagination."""
        all_contacts = []
        after = None
        
        while len(all_contacts) < max_contacts:
            data = self.fetch_contacts(limit=100, after=after)
            contacts = data.get('results', [])
            
            if not contacts:
                break
                
            all_contacts.extend(contacts)
            
            paging = data.get('paging', {})
            next_page = paging.get('next', {})
            after = next_page.get('after')
            
            if not after:
                break
        
        return all_contacts[:max_contacts]
    
    def normalize_contact(self, raw: Dict) -> Dict:
        """Normalize HubSpot contact to APEX format."""
        props = raw.get('properties', {})
        return {
            'external_id': raw.get('id'),
            'external_source': 'hubspot',
            'first_name': props.get('firstname', ''),
            'last_name': props.get('lastname', ''),
            'email': props.get('email', ''),
            'phone': props.get('phone', ''),
            'company': props.get('company', ''),
            'title': props.get('jobtitle', ''),
            'linkedin_url': props.get('linkedinbio', ''),
            'status': props.get('hs_lead_status', ''),
            'lifecycle_stage': props.get('lifecyclestage', ''),
            'email_opt_out': props.get('hs_email_optout', ''),
            'imported_at': datetime.now().isoformat(),
        }


class SalesforceImporter(CRMImporter):
    """Import contacts from Salesforce."""
    
    def __init__(self, username: str = None, password: str = None, 
                 security_token: str = None, domain: str = 'login'):
        super().__init__()
        self.username = username or os.getenv('SALESFORCE_USERNAME')
        self.password = password or os.getenv('SALESFORCE_PASSWORD')
        self.security_token = security_token or os.getenv('SALESFORCE_SECURITY_TOKEN')
        self.domain = domain
        self.sf = None
        
    def connect(self):
        """Connect to Salesforce using simple-salesforce."""
        try:
            from simple_salesforce import Salesforce
            self.sf = Salesforce(
                username=self.username,
                password=self.password,
                security_token=self.security_token,
                domain=self.domain
            )
            return True
        except ImportError:
            raise Exception("simple-salesforce not installed. Run: pip install simple-salesforce")
        except Exception as e:
            raise Exception(f"Salesforce connection failed: {str(e)}")
    
    def fetch_contacts(self, limit: int = 1000) -> List[Dict]:
        """Fetch contacts using SOQL."""
        if not self.sf:
            self.connect()
        
        query = f"""
            SELECT Id, FirstName, LastName, Email, Phone, 
                   Account.Name, Title, LinkedIn_Profile__c, LeadSource,
                   HasOptedOutOfEmail, DoNotCall, EmailBouncedDate
            FROM Contact
            WHERE HasOptedOutOfEmail = false 
              AND DoNotCall = false
              AND Email != null
            ORDER BY CreatedDate DESC
            LIMIT {limit}
        """
        
        result = self.sf.query_all(query)
        return result.get('records', [])
    
    def normalize_contact(self, raw: Dict) -> Dict:
        """Normalize Salesforce contact to APEX format."""
        account = raw.get('Account') or {}
        return {
            'external_id': raw.get('Id'),
            'external_source': 'salesforce',
            'first_name': raw.get('FirstName', ''),
            'last_name': raw.get('LastName', ''),
            'email': raw.get('Email', ''),
            'phone': raw.get('Phone', ''),
            'company': account.get('Name', ''),
            'title': raw.get('Title', ''),
            'linkedin_url': raw.get('LinkedIn_Profile__c', ''),
            'status': raw.get('LeadSource', ''),
            'has_opted_out': raw.get('HasOptedOutOfEmail', False),
            'do_not_call': raw.get('DoNotCall', False),
            'imported_at': datetime.now().isoformat(),
        }


class PipedriveImporter(CRMImporter):
    """Import contacts from Pipedrive."""
    
    BASE_URL = "https://api.pipedrive.com/v1"
    
    def __init__(self, api_token: str = None):
        super().__init__()
        self.api_token = api_token or os.getenv('PIPEDRIVE_API_TOKEN')
    
    def fetch_contacts(self, start: int = 0, limit: int = 100) -> Dict:
        """Fetch persons from Pipedrive."""
        url = f"{self.BASE_URL}/persons"
        params = {
            'api_token': self.api_token,
            'start': start,
            'limit': min(limit, 500),
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Pipedrive API error: {response.status_code}")
        
        return response.json()
    
    def fetch_all_contacts(self, max_contacts: int = 1000) -> List[Dict]:
        """Fetch all contacts with pagination."""
        all_contacts = []
        start = 0
        
        while len(all_contacts) < max_contacts:
            data = self.fetch_contacts(start=start, limit=500)
            
            if not data.get('success'):
                break
            
            contacts = data.get('data') or []
            if not contacts:
                break
            
            all_contacts.extend(contacts)
            
            pagination = data.get('additional_data', {}).get('pagination', {})
            if not pagination.get('more_items_in_collection'):
                break
            
            start = pagination.get('next_start', start + 500)
        
        return all_contacts[:max_contacts]
    
    def normalize_contact(self, raw: Dict) -> Dict:
        """Normalize Pipedrive contact to APEX format."""
        emails = raw.get('email', [])
        primary_email = ''
        if emails and isinstance(emails, list):
            primary_email = emails[0].get('value', '') if emails else ''
        elif isinstance(emails, str):
            primary_email = emails
        
        phones = raw.get('phone', [])
        primary_phone = ''
        if phones and isinstance(phones, list):
            primary_phone = phones[0].get('value', '') if phones else ''
        elif isinstance(phones, str):
            primary_phone = phones
        
        org = raw.get('org_name') or ''
        if isinstance(raw.get('org_id'), dict):
            org = raw['org_id'].get('name', org)
        
        return {
            'external_id': str(raw.get('id')),
            'external_source': 'pipedrive',
            'first_name': raw.get('first_name', ''),
            'last_name': raw.get('last_name', ''),
            'name': raw.get('name', ''),
            'email': primary_email,
            'phone': primary_phone,
            'company': org,
            'title': raw.get('job_title', ''),
            'linkedin_url': '',
            'active_flag': raw.get('active_flag', True),
            'imported_at': datetime.now().isoformat(),
        }


class CSVImporter(CRMImporter):
    """Import contacts from CSV file."""
    
    FIELD_MAPPINGS = {
        'first name': 'first_name', 'firstname': 'first_name', 'first': 'first_name',
        'given name': 'first_name',
        'last name': 'last_name', 'lastname': 'last_name', 'last': 'last_name',
        'surname': 'last_name', 'family name': 'last_name',
        'full name': 'name', 'name': 'name', 'contact name': 'name',
        'email': 'email', 'email address': 'email', 'e-mail': 'email', 'work email': 'email',
        'phone': 'phone', 'phone number': 'phone', 'mobile': 'phone', 
        'mobile phone': 'phone', 'work phone': 'phone', 'telephone': 'phone',
        'company': 'company', 'company name': 'company', 'organization': 'company',
        'organisation': 'company', 'account': 'company', 'account name': 'company',
        'title': 'title', 'job title': 'title', 'position': 'title', 'role': 'title',
        'linkedin': 'linkedin_url', 'linkedin url': 'linkedin_url',
        # Status fields for DNC filtering
        'status': 'status', 'lead status': 'status', 'contact status': 'status',
        'unsubscribed': 'unsubscribed', 'opt out': 'opt_out', 'optout': 'opt_out',
        'do not contact': 'do_not_contact', 'dnc': 'do_not_contact',
    }
    
    def __init__(self):
        super().__init__()
        self.field_mapping = {}
    
    def auto_detect_mapping(self, headers: List[str]) -> Dict[str, str]:
        """Auto-detect field mapping from CSV headers."""
        mapping = {}
        for header in headers:
            normalized = header.lower().strip()
            if normalized in self.FIELD_MAPPINGS:
                mapping[header] = self.FIELD_MAPPINGS[normalized]
        return mapping
    
    def parse_csv(self, csv_content: str, custom_mapping: Dict = None) -> List[Dict]:
        """Parse CSV content and return validated contacts."""
        import csv
        from io import StringIO
        
        reader = csv.DictReader(StringIO(csv_content))
        headers = reader.fieldnames or []
        
        self.field_mapping = custom_mapping or self.auto_detect_mapping(headers)
        
        valid_contacts = []
        for row in reader:
            normalized, reason = self.validate_and_normalize(row)
            if normalized:
                valid_contacts.append(normalized)
        
        return valid_contacts
    
    def normalize_contact(self, raw: Dict) -> Dict:
        """Normalize CSV row to APEX format."""
        contact = {
            'external_source': 'csv',
            'imported_at': datetime.now().isoformat(),
        }
        
        for csv_field, apex_field in self.field_mapping.items():
            if csv_field in raw and raw[csv_field]:
                contact[apex_field] = raw[csv_field].strip()
        
        for key, value in raw.items():
            if value and key.lower() in self.FIELD_MAPPINGS:
                apex_field = self.FIELD_MAPPINGS[key.lower()]
                if apex_field not in contact:
                    contact[apex_field] = value.strip()
        
        return contact


# ============= IMPORT MANAGER =============

class ImportManager:
    """Manages imports from various CRM sources."""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self.validator = ContactValidator()
    
    def save_contacts(self, contacts: List[Dict], skip_validation: bool = False) -> Dict:
        """Save validated contacts to database."""
        success = 0
        failed = 0
        duplicates = 0
        filtered = 0
        filter_reasons = {}
        
        for contact in contacts:
            try:
                # Run validation if not already done
                if not skip_validation:
                    is_valid, reason = self.validator.validate(contact)
                    if not is_valid:
                        filtered += 1
                        filter_reasons[reason] = filter_reasons.get(reason, 0) + 1
                        continue
                
                # Check for duplicate by email
                if contact.get('email'):
                    cursor = self.db.execute(
                        "SELECT id FROM contacts WHERE email = ?",
                        (contact['email'],)
                    )
                    if cursor.fetchone():
                        duplicates += 1
                        continue
                
                # Build name
                name = contact.get('name', '')
                if not name:
                    name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                
                # Insert contact
                self.db.execute("""
                    INSERT INTO contacts (
                        name, first_name, last_name, email, phone,
                        company, title, linkedin_url, 
                        external_id, external_source, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    contact.get('first_name', ''),
                    contact.get('last_name', ''),
                    contact.get('email', ''),
                    contact.get('phone', ''),
                    contact.get('company', ''),
                    contact.get('title', ''),
                    contact.get('linkedin_url', ''),
                    contact.get('external_id', ''),
                    contact.get('external_source', ''),
                    datetime.now().isoformat(),
                ))
                success += 1
                
            except Exception as e:
                logger.error(f"Failed to save contact: {e}")
                failed += 1
        
        self.db.commit()
        
        return {
            'success': success,
            'failed': failed,
            'duplicates': duplicates,
            'filtered': filtered,
            'filter_reasons': filter_reasons,
            'validation_stats': self.validator.get_stats(),
            'total_processed': len(contacts),
        }
