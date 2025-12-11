"""
Contact Service - CRUD operations for contacts with PostgreSQL/SQLite
"""
import sqlite3
import json
import uuid
import os
from datetime import datetime
from typing import Optional, List

# Path to database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'apex.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# =============================================================================
# CRUD OPERATIONS
# =============================================================================

def create_contact(
    first_name: str,
    last_name: str,
    email: str = None,
    phone: str = None,
    title: str = None,
    company: str = None,
    hubspot_id: str = None
) -> dict:
    """Create a new contact"""
    conn = get_db()
    cursor = conn.cursor()
    
    contact_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        INSERT INTO contacts (id, hubspot_id, first_name, last_name, email, phone, title, company, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (contact_id, hubspot_id, first_name, last_name, email, phone, title, company, now, now))
    
    conn.commit()
    conn.close()
    
    return get_contact(contact_id)


def get_contact(contact_id: str) -> Optional[dict]:
    """Get a contact by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return _row_to_dict(row)


def get_contact_by_hubspot_id(hubspot_id: str) -> Optional[dict]:
    """Get a contact by HubSpot ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM contacts WHERE hubspot_id = ?", (hubspot_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return _row_to_dict(row)


def get_all_contacts(limit: int = 100, offset: int = 0) -> List[dict]:
    """Get all contacts with pagination"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM contacts 
        ORDER BY updated_at DESC 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [_row_to_dict(row) for row in rows]


def update_contact(contact_id: str, **kwargs) -> Optional[dict]:
    """Update a contact"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Build update query
    updates = []
    values = []
    for key, value in kwargs.items():
        if key in ['first_name', 'last_name', 'email', 'phone', 'title', 'company', 'hubspot_id']:
            updates.append(f"{key} = ?")
            values.append(value)
    
    if not updates:
        return get_contact(contact_id)
    
    updates.append("updated_at = ?")
    values.append(datetime.utcnow().isoformat())
    values.append(contact_id)
    
    cursor.execute(f"""
        UPDATE contacts SET {', '.join(updates)} WHERE id = ?
    """, values)
    
    conn.commit()
    conn.close()
    
    return get_contact(contact_id)


def save_enrichment(contact_id: str, enrichment_data: dict) -> Optional[dict]:
    """Save enrichment data for a contact"""
    conn = get_db()
    cursor = conn.cursor()
    
    now = datetime.utcnow().isoformat()
    
    cursor.execute("""
        UPDATE contacts 
        SET enrichment = ?, enriched_at = ?, updated_at = ?
        WHERE id = ?
    """, (json.dumps(enrichment_data), now, now, contact_id))
    
    conn.commit()
    conn.close()
    
    return get_contact(contact_id)


def delete_contact(contact_id: str) -> bool:
    """Delete a contact"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted


def import_from_csv(csv_data: List[dict]) -> List[dict]:
    """Import contacts from CSV data"""
    created = []
    for row in csv_data:
        contact = create_contact(
            first_name=row.get('first_name', row.get('firstname', '')),
            last_name=row.get('last_name', row.get('lastname', '')),
            email=row.get('email'),
            phone=row.get('phone'),
            title=row.get('title', row.get('jobtitle', '')),
            company=row.get('company')
        )
        created.append(contact)
    return created


def _row_to_dict(row) -> dict:
    """Convert SQLite row to dictionary"""
    d = dict(row)
    if d.get('enrichment'):
        d['enrichment'] = json.loads(d['enrichment'])
    return d


# =============================================================================
# STATS
# =============================================================================

def get_stats() -> dict:
    """Get contact statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE enriched_at IS NOT NULL")
    enriched = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_contacts": total,
        "enriched_contacts": enriched,
        "pending_enrichment": total - enriched
    }
