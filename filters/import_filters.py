"""
Import Filters API - Smart Contact Qualification (FastAPI)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import json
import sqlite3
import os

router = APIRouter(prefix="/api/import", tags=["import_filters"])

def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apex.db')
    return sqlite3.connect(db_path)

class CustomFilter(BaseModel):
    property: str
    operator: str
    value: str

class ImportFilters(BaseModel):
    requiredFields: Dict[str, bool]
    recommendedFields: Dict[str, bool]
    leadStatus: List[str]
    lifecycleStage: List[str]
    customFilters: List[CustomFilter]

class ContactValidation(BaseModel):
    contacts: List[Dict]

@router.get("/filters")
async def get_import_filters():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='import_filters'")
        if not cursor.fetchone():
            return get_default_filters()
        
        cursor.execute("SELECT filters_json FROM import_filters WHERE user_id = 1")
        row = cursor.fetchone()
        
        return json.loads(row[0]) if row else get_default_filters()
    finally:
        conn.close()

@router.post("/filters")
async def save_import_filters(filters: ImportFilters):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filters_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        filters_json = json.dumps(filters.dict())
        cursor.execute("SELECT id FROM import_filters WHERE user_id = 1")
        
        if cursor.fetchone():
            cursor.execute("UPDATE import_filters SET filters_json = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = 1", (filters_json,))
        else:
            cursor.execute("INSERT INTO import_filters (user_id, filters_json) VALUES (1, ?)", (filters_json,))
        
        conn.commit()
        return {"success": True, "message": "Import filters saved"}
    finally:
        conn.close()

@router.post("/validate")
async def validate_contacts(data: ContactValidation):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT filters_json FROM import_filters WHERE user_id = 1")
        row = cursor.fetchone()
        filters = json.loads(row[0]) if row else get_default_filters()
    finally:
        conn.close()
    
    results = {'total': len(data.contacts), 'qualified': [], 'rejected': [], 'warnings': []}
    
    for contact in data.contacts:
        validation = validate_contact(contact, filters)
        
        if validation['status'] == 'reject':
            results['rejected'].append({'contact': contact, 'reason': validation['reason']})
        elif validation['status'] == 'warn':
            results['warnings'].append({'contact': contact, 'missing_fields': validation.get('missing_fields', [])})
            results['qualified'].append(contact)
        else:
            results['qualified'].append(contact)
    
    return results

def validate_contact(contact: dict, filters: dict) -> dict:
    if not contact.get('name') or not str(contact.get('name')).strip():
        return {'status': 'reject', 'reason': 'Missing required field: name'}
    
    if not contact.get('company') or not str(contact.get('company')).strip():
        return {'status': 'reject', 'reason': 'Missing required field: company'}
    
    if filters.get('leadStatus'):
        contact_status = contact.get('lead_status') or contact.get('leadstatus')
        if contact_status and contact_status not in filters['leadStatus']:
            return {'status': 'reject', 'reason': f"Lead status '{contact_status}' not allowed"}
    
    if filters.get('lifecycleStage'):
        contact_stage = contact.get('lifecycle_stage') or contact.get('lifecyclestage')
        if contact_stage and contact_stage not in filters['lifecycleStage']:
            return {'status': 'reject', 'reason': f"Lifecycle stage '{contact_stage}' not allowed"}
    
    for custom in filters.get('customFilters', []):
        if not custom.get('property') or not custom.get('operator'):
            continue
        
        actual_value = contact.get(custom['property']) or contact.get(custom['property'].lower())
        
        if custom['operator'] == 'equals' and str(actual_value) != str(custom['value']):
            return {'status': 'reject', 'reason': f"{custom['property']} must equal '{custom['value']}'"}
        elif custom['operator'] == 'contains' and custom['value'] not in str(actual_value or ''):
            return {'status': 'reject', 'reason': f"{custom['property']} must contain '{custom['value']}'"}
        elif custom['operator'] == 'not_empty' and not actual_value:
            return {'status': 'reject', 'reason': f"{custom['property']} cannot be empty"}
    
    missing_recommended = []
    if filters.get('recommendedFields', {}).get('linkedin_url') and not contact.get('linkedin_url'):
        missing_recommended.append('LinkedIn URL')
    if filters.get('recommendedFields', {}).get('email') and not contact.get('email'):
        missing_recommended.append('Email')
    if filters.get('recommendedFields', {}).get('phone') and not contact.get('phone'):
        missing_recommended.append('Phone')
    
    if missing_recommended:
        return {'status': 'warn', 'missing_fields': missing_recommended}
    
    return {'status': 'pass'}

def get_default_filters() -> dict:
    return {
        'requiredFields': {'name': True, 'company': True},
        'recommendedFields': {'linkedin_url': True, 'email': True, 'phone': True},
        'leadStatus': ['Qualified', 'Working', 'SQL'],
        'lifecycleStage': ['SQL', 'Opportunity', 'Customer'],
        'customFilters': []
    }
