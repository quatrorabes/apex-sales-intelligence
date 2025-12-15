"""
Contact Service - CRUD operations for contacts (PostgreSQL + SQLite)
"""
import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict

def get_db():
    """Connect to PostgreSQL (production) or SQLite (local)"""
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    if DATABASE_URL and DATABASE_URL.startswith('postgresql'):
        # Production: PostgreSQL
        import psycopg2
        from psycopg2.extras import RealDictCursor
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    else:
        # Local: SQLite
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), '..', 'apex.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

def _is_postgres(conn):
    """Check if connection is PostgreSQL"""
    try:
        import psycopg2
        return isinstance(conn, psycopg2.extensions.connection)
    except ImportError:
        return False

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
    
    is_pg = _is_postgres(conn)
    placeholder = '%s' if is_pg else '?'
    
    cursor.execute(f"""
        INSERT INTO contacts (
            id, hubspot_id, first_name, last_name, email, phone, 
            title, company, created_at, updated_at, enrichment_status
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, 
                  {placeholder}, {placeholder}, {placeholder}, {placeholder}, 
                  {placeholder}, {placeholder}, {placeholder})
    """, (contact_id, hubspot_id, first_name, last_name, email, phone, 
          title, company, now, now, 'pending'))
    
    conn.commit()
    conn.close()
    
    return get_contact(contact_id)

def get_contact(contact_id: str) -> Optional[dict]:
    """Get single contact by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    is_pg = _is_postgres(conn)
    placeholder = '%s' if is_pg else '?'
    
    cursor.execute(f"SELECT * FROM contacts WHERE id = {placeholder}", (contact_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        contact = dict(row)
        # Parse enrichment JSON if string
        if contact.get('enrichment') and isinstance(contact['enrichment'], str):
            try:
                contact['enrichment'] = json.loads(contact['enrichment'])
            except:
                pass
        return contact
    return None

def get_all_contacts(limit: int = 50, offset: int = 0) -> List[dict]:
    """Get paginated list of contacts"""
    from datetime import datetime, date
    
    conn = get_db()
    cursor = conn.cursor()

    is_pg = _is_postgres(conn)
    placeholder = '%s' if is_pg else '?'

    cursor.execute(f"""
        SELECT id, hubspot_id, first_name, last_name, email, phone,
               title, company, industry, linkedin_url,
               enrichment_status, enriched_at, created_at, updated_at
        FROM contacts
        ORDER BY created_at DESC
        LIMIT {placeholder} OFFSET {placeholder}
    """, (limit, offset))

    contacts = []
    for row in cursor.fetchall():
        contact = {}
        for key, value in dict(row).items():
            # Convert datetime/date objects to ISO strings
            if isinstance(value, (datetime, date)):
                contact[key] = value.isoformat()
            else:
                contact[key] = value
        contacts.append(contact)
    
    conn.close()
    return contacts

def update_contact(contact_id: str, **updates) -> Optional[dict]:
    """Update contact fields"""
    if not updates:
        return get_contact(contact_id)
    
    conn = get_db()
    cursor = conn.cursor()
    
    is_pg = _is_postgres(conn)
    placeholder = '%s' if is_pg else '?'
    
    # Build SET clause
    set_clause = ', '.join([f"{k} = {placeholder}" for k in updates.keys()])
    values = list(updates.values()) + [datetime.utcnow().isoformat(), contact_id]
    
    cursor.execute(f"""
        UPDATE contacts 
        SET {set_clause}, updated_at = {placeholder}
        WHERE id = {placeholder}
    """, values)
    
    conn.commit()
    conn.close()
    
    return get_contact(contact_id)

def save_enrichment(contact_id: str, enrichment_data: dict) -> dict:
    """Save enrichment data to contact"""
    conn = get_db()
    cursor = conn.cursor()
    
    is_pg = _is_postgres(conn)
    placeholder = '%s' if is_pg else '?'
    now = datetime.utcnow().isoformat()
    
    cursor.execute(f"""
        UPDATE contacts 
        SET enrichment = {placeholder},
            enrichment_status = 'enriched',
            enriched_at = {placeholder},
            updated_at = {placeholder}
        WHERE id = {placeholder}
    """, (json.dumps(enrichment_data), now, now, contact_id))
    
    conn.commit()
    conn.close()
    
    return get_contact(contact_id)

def get_stats() -> dict:
    """Get aggregate statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    is_pg = _is_postgres(conn)
    
    cursor.execute("SELECT COUNT(*) as count FROM contacts")
    total = cursor.fetchone()['count'] if is_pg else cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment IS NOT NULL")
    enriched = cursor.fetchone()['count'] if is_pg else cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'pending'")
    pending = cursor.fetchone()['count'] if is_pg else cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_contacts": total,
        "enriched_contacts": enriched,
        "pending_enrichment": pending
    }


def delete_contact(contact_id: str) -> bool:
    """Delete a contact"""
    conn = get_db()
    cursor = conn.cursor()
    
    is_pg = _is_postgres(conn)
    placeholder = '%s' if is_pg else '?'
    
    cursor.execute(f"DELETE FROM contacts WHERE id = {placeholder}", (contact_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted

def import_from_csv(csv_data: List[dict]) -> int:
    """Import contacts from CSV data"""
    conn = get_db()
    cursor = conn.cursor()
    
    is_pg = _is_postgres(conn)
    placeholder = '%s' if is_pg else '?'
    
    imported = 0
    for row in csv_data:
        # Skip if missing required fields
        if not all([row.get('first_name'), row.get('last_name'), 
                   row.get('email'), row.get('company')]):
            continue
        
        contact_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        try:
            cursor.execute(f"""
                INSERT INTO contacts (
                    id, first_name, last_name, email, phone,
                    title, company, industry, linkedin_url,
                    created_at, updated_at, enrichment_status
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, 
                          {placeholder}, {placeholder}, {placeholder}, {placeholder}, 
                          {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """, (
                contact_id,
                row.get('first_name'),
                row.get('last_name'),
                row.get('email'),
                row.get('phone'),
                row.get('title'),
                row.get('company'),
                row.get('industry'),
                row.get('linkedin_url'),
                now,
                now,
                'pending'
            ))
            imported += 1
        except Exception as e:
            print(f"Error importing {row.get('email')}: {e}")
            continue
    
    conn.commit()
    conn.close()
    
    return imported

def get_contact_by_hubspot_id(hubspot_id: str) -> Optional[dict]:
    """Get contact by HubSpot ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    is_pg = _is_postgres(conn)
    placeholder = '%s' if is_pg else '?'
    
    cursor.execute(
        f"SELECT * FROM contacts WHERE hubspot_id = {placeholder}",
        (hubspot_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        contact = dict(row)
        if contact.get('enrichment') and isinstance(contact['enrichment'], str):
            try:
                contact['enrichment'] = json.loads(contact['enrichment'])
            except:
                pass
        return contact
    return None

def bulk_enrich(limit: int = 10) -> dict:
    """Get contacts needing enrichment"""
    conn = get_db()
    cursor = conn.cursor()
    
    is_pg = _is_postgres(conn)
    placeholder = '%s' if is_pg else '?'
    
    cursor.execute(f"""
        SELECT id, first_name, last_name, email, company, title
        FROM contacts
        WHERE enrichment_status = 'pending'
        ORDER BY created_at DESC
        LIMIT {placeholder}
    """, (limit,))
    
    contacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {
        "contacts": contacts,
        "count": len(contacts)
    }
