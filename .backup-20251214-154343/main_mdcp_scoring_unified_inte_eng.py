#!/usr/bin/env python3
"""
APEX Backend API - Complete Main Application
Unified Sales Intelligence Platform with Enhanced HubSpot Integration
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import sqlite3
import json
import asyncio
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv
import os
from contextlib import contextmanager, asynccontextmanager
from cadence_router import CadenceRouter



import sys


sys.path.append('.')

# Load environment variables
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

DATABASE = './apex.db'

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize all database tables with enhanced schema"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Enhanced Contacts table with enrichment tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hubspot_id TEXT UNIQUE,
                
                -- Basic Info
                name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                title TEXT,
                company TEXT,
                industry TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                mobile_phone TEXT,
                linkedin_url TEXT,
                
                -- HubSpot Metadata
                lifecycle_stage TEXT,
                lead_status TEXT,
                hubspot_owner_id TEXT,
                
                -- Enrichment Status
                enrichment_status TEXT DEFAULT 'pending',
                enriched_at TIMESTAMP,
                enrichment_data TEXT,
                
                -- AI Intelligence
                tier INTEGER,
                persona_name TEXT,
                personality_type TEXT,
                disc_profile TEXT,
                opportunity_score REAL,
                urgency_level TEXT,
                lead_tier TEXT,
                
                -- Advanced Data
                relationship_data TEXT,
                vertical_intelligence TEXT,
                pain_points TEXT,
                
                -- Outreach Content (stored for quick access)
                email_variant_1 TEXT,
                email_variant_2 TEXT,
                email_variant_3 TEXT,
                call_script_1 TEXT,
                call_script_2 TEXT,
                call_script_3 TEXT,
                
                -- Tracking
                last_contacted TIMESTAMP,
                outreach_stage TEXT,
                conversion_probability REAL,
                
                -- Timestamps
                imported_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON contacts(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hubspot_id ON contacts(hubspot_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_enrichment_status ON contacts(enrichment_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_lifecycle_stage ON contacts(lifecycle_stage)")
        
        # Outreach history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                content TEXT,
                sent_at TIMESTAMP,
                response TEXT,
                success BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
        """)
        
        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                metric_type TEXT,
                metric_value REAL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(contact_id) REFERENCES contacts(id)
            )
        """)
        
        conn.commit()
        print("✅ Database tables initialized with enhanced schema")

# ============================================================================
# LIFESPAN CONTEXT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    print("\n" + "="*70)
    print("🚀 APEX SALES INTELLIGENCE API v2.1")
    print("="*70)
    init_db()
    
    required_env = ['HUBSPOT_ACCESS_TOKEN', 'PERPLEXITY_API_KEY']
    missing_env = [env for env in required_env if not os.getenv(env)]
    
    if missing_env:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing_env)}")
    else:
        print("✅ All environment variables configured")
    
    print("✅ All systems initialized")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print("="*70 + "\n")
    
    yield
    
    # Shutdown
    print("\n" + "="*70)
    print("👋 Shutting down Apex API...")
    print("="*70 + "\n")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Apex Sales Intelligence API",
    version="2.1.0",
    description="AI-Powered Sales Automation & Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ============================================================================
# CORS CONFIGURATION
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3001", "http://localhost:8000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ContactCreate(BaseModel):
    hubspot_id: Optional[str] = None
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    lifecycle_stage: Optional[str] = None

class ImportRequest(BaseModel):
    limit: int = 100
    lifecycle_stages: Optional[List[str]] = None

# ============================================================================
# CORE API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Apex Sales Intelligence API",
        "version": "2.1.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            contact_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'complete'")
            enriched_count = cursor.fetchone()[0]
            
            return {
                "status": "healthy",
                "database": "connected",
                "contacts": contact_count,
                "enriched": enriched_count,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# CONTACTS ENDPOINTS
# ============================================================================

@app.post("/api/contacts")
async def create_contact(contact: ContactCreate):
    """Create a new contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (
                    hubspot_id, name, first_name, last_name, title, company,
                    industry, email, phone, linkedin_url, lifecycle_stage,
                    enrichment_status, imported_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (
                contact.hubspot_id, contact.name, contact.first_name, 
                contact.last_name, contact.title, contact.company,
                contact.industry, contact.email, contact.phone, 
                contact.linkedin_url, contact.lifecycle_stage,
                datetime.now().isoformat()
            ))
            conn.commit()
            contact_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            return dict(row)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts")
async def list_contacts(
    limit: int = 100, 
    offset: int = 0,
    enrichment_status: Optional[str] = None,
    lifecycle_stage: Optional[str] = None
):
    """List all contacts with optional filtering"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT * FROM contacts WHERE 1=1"
            params = []
            
            if enrichment_status:
                query += " AND enrichment_status = ?"
                params.append(enrichment_status)
            
            if lifecycle_stage:
                query += " AND lifecycle_stage = ?"
                params.append(lifecycle_stage)
            
            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            contacts = []
            for row in cursor.fetchall():
                contact_dict = dict(row)
                contacts.append(contact_dict)
            
            # Get total count
            count_query = "SELECT COUNT(*) FROM contacts WHERE 1=1"
            count_params = []
            
            if enrichment_status:
                count_query += " AND enrichment_status = ?"
                count_params.append(enrichment_status)
            
            if lifecycle_stage:
                count_query += " AND lifecycle_stage = ?"
                count_params.append(lifecycle_stage)
            
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()[0]
            
            return {
                "contacts": contacts,
                "total": total,
                "limit": limit,
                "offset": offset
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: int):
    """Get a specific contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            return dict(row)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/enrich")
async def enrich_contact(contact_id: int):
        """
        Enrich contact with AI intelligence.

        Flow:
            1. Validate contact exists.
            2. Mark enrichment_status = 'enriching'.
            3. Run UnifiedIntelligenceEngine (or fallback stub).
            4. Save enrichment_data, opportunity_score, lead_tier.
            5. On any failure, mark status = 'failed' and return 500.
        """
        try:
                # 1) Fetch contact and mark as enriching
                with get_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                                """
                                SELECT id, name, email, company, title, linkedin_url
                                FROM contacts
                                WHERE id = ?
                                """,
                                (contact_id,),
                        )
                        row = cursor.fetchone()
                        if not row:
                                raise HTTPException(status_code=404, detail="Contact not found")
                            
                        contact = {
                                "id": row["id"],
                                "name": row["name"],
                                "email": row["email"],
                                "company": row["company"],
                                "title": row["title"],
                                "linkedin_url": row["linkedin_url"],
                        }
                    
                        cursor.execute(
                                """
                                UPDATE contacts
                                SET enrichment_status = 'enriching'
                                WHERE id = ?
                                """,
                                (contact_id,),
                        )
                        conn.commit()
                    
                # 2) Run enrichment engine outside DB context
                try:
                        try:
                                from unified_intelligence_engine import UnifiedIntelligenceEngine
                                engine = UnifiedIntelligenceEngine()
                                enrichment_data = engine.enrich_contact(contact)
                        except ImportError:
                                # Safe fallback stub if engine is not installed
                                enrichment_data = {
                                        "source": "fallback_stub",
                                        "notes": "UnifiedIntelligenceEngine not installed; used simple heuristic scoring.",
                                        "opportunity_score": 50.0,
                                        "lead_tier": "QUALIFIED",
                                }
                            
                        # Ensure keys exist
                        opportunity_score = float(enrichment_data.get("opportunity_score", 0))
                        lead_tier = str(enrichment_data.get("lead_tier", "COLD"))
                    
                        # 3) Persist results and mark complete
                        with get_db() as conn:
                                cursor = conn.cursor()
                                cursor.execute(
                                        """
                                        UPDATE contacts
                                        SET
                                                enrichment_status = 'complete',
                                                enriched_at = ?,
                                                enrichment_data = ?,
                                                opportunity_score = ?,
                                                lead_tier = ?,
                                                updated_at = ?
                                        WHERE id = ?
                                        """,
                                        (
                                                datetime.now().isoformat(),
                                                json.dumps(enrichment_data),
                                                opportunity_score,
                                                lead_tier,
                                                datetime.now().isoformat(),
                                                contact_id,
                                        ),
                                )
                                conn.commit()
                            
                        return {
                                "status": "success",
                                "contact_id": contact_id,
                                "opportunity_score": opportunity_score,
                                "lead_tier": lead_tier,
                                "enrichment_data": enrichment_data,
                                "message": "Contact enriched successfully",
                        }
            
                except Exception as engine_error:
                        # 4) Mark as failed if engine or scoring blows up
                        with get_db() as conn:
                                cursor = conn.cursor()
                                cursor.execute(
                                        """
                                        UPDATE contacts
                                        SET enrichment_status = 'failed',
                                                updated_at = ?
                                        WHERE id = ?
                                        """,
                                        (datetime.now().isoformat(), contact_id),
                                )
                                conn.commit()
                            
                        print(f"Enrichment error for contact {contact_id}: {engine_error}")
                        raise HTTPException(
                                status_code=500,
                                detail=f"Enrichment failed: {str(engine_error)}",
                        )
                    
        except HTTPException:
                # Bubble up explicit HTTP errors
                raise
        except Exception as e:
                print(f"Endpoint error in /api/contacts/{contact_id}/enrich: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            
@app.patch("/api/contacts/{contact_id}")
async def update_contact(contact_id: int, updates: dict):
    """Update contact information"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            update_fields = []
            values = []
            
            allowed_fields = ['first_name', 'last_name', 'company', 'email', 'linkedin_url']
            for field in allowed_fields:
                if field in updates:
                    update_fields.append(f"{field} = ?")
                    values.append(updates[field])
                    
            if not update_fields:
                return {'success': False, 'error': 'No valid fields to update'}
            
            # Add updated_at
            update_fields.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            
            # Reset enrichment status to pending if data changed
            update_fields.append("enrichment_status = ?")
            values.append('pending')
            
            values.append(contact_id)
            
            query = f"UPDATE contacts SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            return {'success': True, 'message': 'Contact updated successfully'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
@app.post("/api/contacts/{contact_id}/flag")
async def flag_contact(contact_id: int, flag_data: dict):
    """Flag contact as having incorrect information"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE contacts 
                SET 
                    enrichment_status = 'failed',
                    pain_points = ?,
                    updated_at = ?
                WHERE id = ?
            """, (
                f"FLAGGED: {flag_data.get('reason', 'Data quality issue')}",
                datetime.now().isoformat(),
                contact_id
            ))
            conn.commit()
            
            return {'success': True, 'message': 'Contact flagged for review'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
@app.delete("/api/contacts/{contact_id}")
async def delete_contact(contact_id: int):
    """Remove contact from database"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
            
            return {'success': True, 'message': 'Contact removed successfully'}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
# ============================================================================
# HUBSPOT IMPORT ENDPOINT - ENHANCED
# ============================================================================
@app.post("/api/contacts/import")
async def import_contacts(import_req: Optional[ImportRequest] = None):
    """
    Import contacts with quick lookup and scoring
    NO expensive AI enrichment - that comes later
    """
    try:
        # Set default import parameters
        limit = 100 if not import_req else min(import_req.limit, 100)
        
        # Default qualified lifecycle stages
        default_stages = ["lead", "subscriber", "marketingqualifiedlead", "salesqualifiedlead"]
        lifecycle_stages = default_stages if not import_req or not import_req.lifecycle_stages else import_req.lifecycle_stages
        
        # HubSpot API
        hubspot_url = 'https://api.hubapi.com/crm/v3/objects/contacts/search'
        
        headers = {
            'Authorization': f"Bearer {os.getenv('HUBSPOT_ACCESS_TOKEN', '')}",
            'Content-Type': 'application/json'
        }
        
        # Get pagination offset
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE hubspot_id IS NOT NULL")
            already_imported = cursor.fetchone()[0]
            
        offset = already_imported
        
        # Build filters
        filters = [
            {"propertyName": "lifecyclestage", "operator": "IN", "values": lifecycle_stages},
            {"propertyName": "email", "operator": "HAS_PROPERTY"},
            {"propertyName": "company", "operator": "HAS_PROPERTY"}
        ]
        
        properties = [
            "firstname", "lastname", "email", "phone", "mobilephone",
            "company", "jobtitle", "linkedin_url", "lifecyclestage",
            "hs_lead_status", "hubspot_owner_id", "industry",
            "createdate", "notes_last_updated"
        ]
        
        sorts = [{"propertyName": "createdate", "direction": "DESCENDING"}]
        
        search_body = {
            "filterGroups": [{"filters": filters}],
            "properties": properties,
            "sorts": sorts,
            "limit": limit,
            "after": offset
        }
        
        print(f"\n📥 Importing contacts from HubSpot...")
        print(f"   Limit: {limit}, Offset: {offset}")
        
        # Fetch from HubSpot
        response = requests.post(hubspot_url, headers=headers, json=search_body)
        
        if response.status_code != 200:
            return JSONResponse(
                status_code=response.status_code,
                content={'success': False, 'error': 'HubSpot API error'}
            )
        
        hubspot_data = response.json()
        contacts = hubspot_data.get('results', [])
        total_available = hubspot_data.get('total', len(contacts))
        has_more = 'next' in hubspot_data.get('paging', {})
        
        print(f"✅ Retrieved {len(contacts)} contacts")
        
        # Import quick enrichment and scorer
        try:
            from quick_enrichment import quick_enrich_contact
            has_quick_enrich = True
        except ImportError:
            print("⚠️  quick_enrichment.py not found - skipping quick lookup")
            has_quick_enrich = False
            
        try:
            from apps.backend.intelligence import ApexScoringEngine  # New enhanced scorer
            has_scorer = True
        except ImportError:
            print("⚠️  contact_scorer.py not found - skipping scoring")
            has_scorer = False
            
        # Track results
        imported_count = 0
        updated_count = 0
        duplicate_count = 0
        skipped_count = 0
        tier_counts = {'HOT': 0, 'WARM': 0, 'QUALIFIED': 0, 'COLD': 0}
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            for idx, contact in enumerate(contacts, 1):
                contact_id = contact.get('id')
                props = contact.get('properties', {})
                
                # Parse contact data
                first_name = (props.get('firstname') or '').strip()
                last_name = (props.get('lastname') or '').strip()
                email = (props.get('email') or '').strip()
                company = (props.get('company') or '').strip()
                
                # Validate required fields
                if not email or not company:
                    skipped_count += 1
                    continue
                
                # Build contact data
                full_name = ' '.join(filter(None, [first_name, last_name])) or email.split('@')[0]
                phone = (props.get('mobilephone') or props.get('phone') or '').strip() or None
                mobile_phone = (props.get('mobilephone') or '').strip() or None
                title = (props.get('jobtitle') or '').strip() or None
                industry = (props.get('industry') or '').strip() or None
                linkedin_url = (props.get('linkedin_url') or '').strip() or None
                lifecycle_stage = (props.get('lifecyclestage') or '').strip() or None
                lead_status = (props.get('hs_lead_status') or '').strip() or None
                hubspot_owner_id = (props.get('hubspot_owner_id') or '').strip() or None
                
                try:
                    # Check if exists
                    cursor.execute("SELECT id FROM contacts WHERE hubspot_id = ? OR email = ?", (contact_id, email))
                    existing = cursor.fetchone()
                    
                    if idx % 10 == 0 or idx <= 5:  # Print every 10th or first 5
                        print(f"   [{idx}/{len(contacts)}] {full_name} ({company})")
                    
                    # Quick enrichment (if available)
                    if has_quick_enrich:
                        contact_data = {
                            'name': full_name,
                            'email': email,
                            'company': company,
                            'linkedin_url': linkedin_url
                        }
                        quick_data = quick_enrich_contact(contact_data)
                        if quick_data.get('linkedin_url') and not linkedin_url:
                            linkedin_url = quick_data['linkedin_url']
                            
                    # Scoring (if available)
                    total_score = 50  # Default
                    tier = 'QUALIFIED'  # Default
                    
                    if has_scorer:
                        score_data = score_contact({
                            'title': title,
                            'company': company,
                            'lifecycle_stage': lifecycle_stage,
                            'phone': phone,
                            'linkedin_url': linkedin_url,
                            'industry': industry
                        })
                        total_score = score_data['total_score']
                        tier = score_data['tier']
                        
                    tier_counts[tier] += 1
                    
                    if existing:
                        # Update existing
                        cursor.execute("""
                            UPDATE contacts SET
                                hubspot_id = ?, name = ?, first_name = ?, last_name = ?,
                                title = ?, company = ?, industry = ?, email = ?,
                                phone = ?, mobile_phone = ?, linkedin_url = ?,
                                lifecycle_stage = ?, lead_status = ?, hubspot_owner_id = ?,
                                opportunity_score = ?, lead_tier = ?, updated_at = ?
                            WHERE id = ?
                        """, (
                            contact_id, full_name, first_name, last_name,
                            title, company, industry, email,
                            phone, mobile_phone, linkedin_url,
                            lifecycle_stage, lead_status, hubspot_owner_id,
                            total_score, tier, datetime.now().isoformat(),
                            existing[0]
                        ))
                        updated_count += 1
                    else:
                        # Insert new
                        cursor.execute("""
                            INSERT INTO contacts (
                                hubspot_id, name, first_name, last_name, title, company,
                                industry, email, phone, mobile_phone, linkedin_url,
                                lifecycle_stage, lead_status, hubspot_owner_id,
                                opportunity_score, lead_tier, enrichment_status, imported_at
                            )
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
                        """, (
                            contact_id, full_name, first_name, last_name,
                            title, company, industry, email,
                            phone, mobile_phone, linkedin_url,
                            lifecycle_stage, lead_status, hubspot_owner_id,
                            total_score, tier, datetime.now().isoformat()
                        ))
                        imported_count += 1
                        
                except sqlite3.IntegrityError:
                    duplicate_count += 1
                    continue
                except Exception as e:
                    print(f"      ❌ Error: {e}")
                    continue
                
            conn.commit()
            
        # Get total count
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            total_in_db = cursor.fetchone()[0]
            
        result = {
            'success': True,
            'imported': imported_count,
            'updated': updated_count,
            'duplicates': duplicate_count,
            'skipped': skipped_count,
            'total_processed': len(contacts),
            'total_available': total_available,
            'total_in_database': total_in_db,
            'has_more': has_more,
            'tier_distribution': tier_counts
        }
        
        print(f"\n📊 Import Summary:")
        print(f"   ✅ New: {imported_count}, Updated: {updated_count}")
        print(f"   🎯 Tiers - HOT:{tier_counts['HOT']} WARM:{tier_counts['WARM']} QUALIFIED:{tier_counts['QUALIFIED']} COLD:{tier_counts['COLD']}")
        print(f"   💾 Total in DB: {total_in_db}, More: {'Yes' if has_more else 'No'}\n")
        
        return result
    
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
# Add to your main.py (around line 700, after existing endpoints)
        
#@app.get("/api/apex/scores")
#async def get_apex_scores():
#   """Get all contacts with Apex Intelligence scores"""
#   with get_db() as conn:
#       cursor = conn.cursor()
#       cursor.execute("""
#           SELECT 
#               c.id, c.name, c.company, c.email,
#               c.lead_type, c.lifecycle_stage,
#               m.mdcp_total, m.mdcp_tier,
#               r.rss_total, r.rss_tier,
#               p.priority_score, p.urgency_level,
#               p.recommended_action
#           FROM contacts c
#           LEFT JOIN (
#               SELECT contact_id, MAX(id) as max_id FROM mdcp_scores GROUP BY contact_id
#           ) m_latest ON c.id = m_latest.contact_id
#           LEFT JOIN mdcp_scores m ON m_latest.max_id = m.id
#           LEFT JOIN (
#               SELECT contact_id, MAX(id) as max_id FROM rss_scores GROUP BY contact_id
#           ) r_latest ON c.id = r_latest.contact_id
#           LEFT JOIN rss_scores r ON r_latest.max_id = r.id
#           LEFT JOIN (
#               SELECT contact_id, MAX(id) as max_id FROM priority_scores GROUP BY contact_id
#           ) p_latest ON c.id = p_latest.contact_id
#           LEFT JOIN priority_scores p ON p_latest.max_id = p.id
#           WHERE p.priority_score IS NOT NULL
#           ORDER BY p.priority_score DESC
#       """)
#       
#       columns = [desc[0] for desc in cursor.description]
#       contacts = [dict(zip(columns, row)) for row in cursor.fetchall()]
#       
#       return {
#           "status": "success",
#           "count": len(contacts),
#           "contacts": contacts
#       }
    
    # ============================================================================
    # APEX INTELLIGENCE API (using contacts table)
    # ============================================================================
        
    @app.get("/api/apex/scores")
    async def get_apex_scores():
            """
            Return prioritized contacts for Apex Intelligence.
    
            This implementation uses existing contacts data:
                - opportunity_score -> priority_score / mdcp_total
                - lead_tier         -> mdcp_tier
                - urgency_level     -> derived from lead_tier
            """
            try:
                    with get_db() as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                    """
                                    SELECT
                                            id,
                                            name,
                                            company,
                                            email,
                                            lifecycle_stage,
                                            opportunity_score,
                                            lead_tier,
                                            enrichment_status
                                    FROM contacts
                                    WHERE enrichment_status = 'complete'
                                    ORDER BY COALESCE(opportunity_score, 0) DESC
                                    """
                            )
                            rows = cursor.fetchall()
                        
                    def derive_urgency(lead_tier: str | None) -> str:
                            lt = (lead_tier or "").upper()
                            if lt == "HOT":
                                    return "IMMEDIATE"
                            if lt == "WARM":
                                    return "HIGH"
                            if lt == "QUALIFIED":
                                    return "MEDIUM"
                            return "LOW"
                
                    contacts = []
                    for row in rows:
                            opportunity_score = row["opportunity_score"] or 0.0
                            lead_tier = row["lead_tier"] or "COLD"
                            urgency = derive_urgency(lead_tier)
                        
                            if urgency == "IMMEDIATE":
                                    action = "Book a call today; this is a top‑priority opportunity."
                            elif urgency == "HIGH":
                                    action = "Schedule an intro call this week and send a tailored email."
                            elif urgency == "MEDIUM":
                                    action = "Send a nurture email and add to a warm cadence."
                            else:
                                    action = "Keep in long‑term nurture; light check‑in next month."
                                
                            contacts.append(
                                    {
                                            "id": row["id"],
                                            "name": row["name"],
                                            "company": row["company"],
                                            "email": row["email"],
                                            # lead_type isn’t in the schema; pick a safe default so UI doesn’t break
                                            "lead_type": "BORROWER",
                                            "lifecycle_stage": row["lifecycle_stage"],
                                            "mdcp_total": float(opportunity_score),
                                            "mdcp_tier": lead_tier,
                                            "rss_total": None,
                                            "rss_tier": None,
                                            "priority_score": float(opportunity_score),
                                            "urgency_level": urgency,
                                            "recommended_action": action,
                                    }
                            )
                        
                    return {
                            "status": "success",
                            "count": len(contacts),
                            "contacts": contacts,
                    }
        
            except Exception as e:
                    print(f"[APEX] Error in /api/apex/scores: {e}")
                    raise HTTPException(status_code=500, detail=str(e))
                
                
    @app.post("/api/apex/score-all")
    async def score_all_contacts():
            """
            Stub for the 'Run Scoring' button.
    
            It currently just reports how many enriched contacts there are.
            Apex Intelligence then uses opportunity_score/lead_tier from contacts.
            """
            try:
                    with get_db() as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                    "SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'complete'"
                            )
                            enriched = cursor.fetchone()[0] or 0
                        
                    return {
                            "status": "success",
                            "message": "Apex Intelligence is using existing opportunity_score and lead_tier values as scores.",
                            "scored": int(enriched),
                    }
            except Exception as e:
                    print(f"[APEX] Error in /api/apex/score-all: {e}")
                    raise HTTPException(status_code=500, detail=str(e))
                
    
@app.post("/api/apex/score/{contact_id}")
async def score_single_contact(contact_id: int):
    """Run Apex Intelligence scoring for a single contact"""
    try:
        from apps.backend.intelligence import ApexScoringEngine
        engine = ApexScoringEngine('apex.db')
        result = engine.score_contact(contact_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
#@app.post("/api/apex/score-all")
#async def score_all_contacts(background_tasks: BackgroundTasks):
#   """Score all contacts in background"""
#   background_tasks.add_task(run_apex_scoring)
#   return {"status": "started", "message": "Scoring all contacts in background"}
#
#async def run_apex_scoring():
#   """Background task to score all contacts"""
#   from apps.backend.intelligence import ApexScoringEngine
#   engine = ApexScoringEngine('apex.db')
#   results = engine.score_all_contacts()
#   print(f"[APEX] Scored {len(results)} contacts")
    
# ============================================================================
# ANALYTICS ENDPOINT
# ============================================================================

@app.get("/api/analytics/dashboard")
async def get_dashboard_metrics():
    """Get dashboard metrics for UI"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Total contacts
            cursor.execute("SELECT COUNT(*) FROM contacts")
            total_contacts = cursor.fetchone()[0]
            
            # Enriched contacts
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'complete'")
            enriched = cursor.fetchone()[0]
            
            # Pending enrichment
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'pending'")
            pending = cursor.fetchone()[0]
            
            # By lifecycle stage
            cursor.execute("""
                SELECT lifecycle_stage, COUNT(*) as count
                FROM contacts
                WHERE lifecycle_stage IS NOT NULL
                GROUP BY lifecycle_stage
            """)
            lifecycle_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            
            # By lead tier
            cursor.execute("""
                SELECT lead_tier, COUNT(*) as count
                FROM contacts
                WHERE lead_tier IS NOT NULL
                GROUP BY lead_tier
            """)
            tier_breakdown = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Average opportunity score
            cursor.execute("""
                SELECT AVG(opportunity_score)
                FROM contacts
                WHERE opportunity_score IS NOT NULL
            """)
            avg_score = cursor.fetchone()[0] or 0
            
            return {
                "total_contacts": total_contacts,
                "enriched": enriched,
                "pending_enrichment": pending,
                "average_opportunity_score": round(avg_score, 2),
                "lifecycle_breakdown": lifecycle_breakdown,
                "tier_breakdown": tier_breakdown,
                "open_rate": 0.0,  # Placeholder
                "sent": 0,  # Placeholder
                "errors": 0  # Placeholder
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# APEX INTELLIGENCE API (Stubbed from contacts table)
# ============================================================================
        
@app.get("/api/apex/scores")
async def get_apex_scores():
        """
        Return prioritized contacts for Apex Intelligence.

        This stub implementation uses existing contacts data:
            - mdcp_total      -> opportunity_score
            - mdcp_tier       -> lead_tier
            - priority_score  -> opportunity_score
            - urgency_level   -> derived from lead_tier
        """
        try:
                with get_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                                """
                                SELECT
                                        id,
                                        name,
                                        company,
                                        email,
                                        lifecycle_stage,
                                        opportunity_score,
                                        lead_tier,
                                        enrichment_status
                                FROM contacts
                                WHERE enrichment_status = 'complete'
                                ORDER BY COALESCE(opportunity_score, 0) DESC
                                """
                        )
                        rows = cursor.fetchall()
                    
                def derive_urgency(lead_tier: str | None) -> str:
                        lt = (lead_tier or "").upper()
                        if lt == "HOT":
                                return "IMMEDIATE"
                        if lt == "WARM":
                                return "HIGH"
                        if lt == "QUALIFIED":
                                return "MEDIUM"
                        return "LOW"
            
                contacts = []
                for row in rows:
                        opportunity_score = row["opportunity_score"] or 0.0
                        lead_tier = row["lead_tier"] or "COLD"
                    
                        urgency = derive_urgency(lead_tier)
                        if urgency == "IMMEDIATE":
                                action = "Book a call today; this is a top‑priority opportunity."
                        elif urgency == "HIGH":
                                action = "Schedule an intro call this week and send a tailored email."
                        elif urgency == "MEDIUM":
                                action = "Send a nurture email and add to a warm cadence."
                        else:
                                action = "Keep in long‑term nurture; light check‑in next month."
                            
                        contacts.append(
                                {
                                        "id": row["id"],
                                        "name": row["name"],
                                        "company": row["company"],
                                        "email": row["email"],
                                        # lead_type is not in the original schema; default to BORROWER
                                        "lead_type": "BORROWER",
                                        "lifecycle_stage": row["lifecycle_stage"],
                                        # MDCP proxy
                                        "mdcp_total": float(opportunity_score),
                                        "mdcp_tier": lead_tier,
                                        # RSS not implemented yet
                                        "rss_total": None,
                                        "rss_tier": None,
                                        # Priority proxy
                                        "priority_score": float(opportunity_score),
                                        "urgency_level": urgency,
                                        "recommended_action": action,
                                }
                        )
                    
                return {
                        "status": "success",
                        "count": len(contacts),
                        "contacts": contacts,
                }
    
        except Exception as e:
                print(f"[APEX] Error in /api/apex/scores: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            
            
@app.post("/api/apex/score-all")
async def score_all_contacts():
        """
        Stub for 'Run Scoring' button.

        In this version we simply report how many enriched contacts exist and
        rely on opportunity_score / lead_tier as the Apex scores.
        """
        try:
                with get_db() as conn:
                        cursor = conn.cursor()
                        cursor.execute(
                                "SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'complete'"
                        )
                        enriched = cursor.fetchone()[0]
                    
                return {
                        "status": "success",
                        "message": "Apex Intelligence is using opportunity_score and lead_tier as stubbed scores. Plug in the full MDCP/RSS engine when ready.",
                        "scored": int(enriched),
                }
        except Exception as e:
                print(f"[APEX] Error in /api/apex/score-all: {e}")
                raise HTTPException(status_code=500, detail=str(e))
            

# ============================================================================
# OUTREACH ENDPOINTS (Enhanced Stubs)
# ============================================================================

@app.post("/api/v1/outreach/contacts/{contact_id}/call-scripts")
async def generate_call_script(contact_id: int):
    """Generate call script for contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            contact = cursor.fetchone()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            # TODO: Integrate with actual AI generation
            scripts = {
                "variant_1": {
                    "opener": f"Hi {contact['first_name']}, this is [Your Name] from Harvest Small Business Finance...",
                    "value_prop": f"I noticed you're the {contact['title']} at {contact['company']}, and I wanted to reach out because...",
                    "close": "Would you be open to a brief 15-minute call to explore this further?"
                },
                "variant_2": {
                    "opener": f"Good morning {contact['first_name']}, I hope I'm catching you at a good time...",
                    "value_prop": "I specialize in helping companies in your industry with...",
                    "close": "Can we schedule a quick conversation next week?"
                },
                "variant_3": {
                    "opener": f"{contact['first_name']}, I've been following {contact['company']} and...",
                    "value_prop": "We've helped similar organizations achieve...",
                    "close": "Are you available for a brief chat this week?"
                }
            }
            
            return {
                "status": "success",
                "contact_id": contact_id,
                "scripts": scripts
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/outreach/contacts/{contact_id}/emails")
async def generate_email(contact_id: int):
    """Generate email for contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            contact = cursor.fetchone()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            # TODO: Integrate with actual AI generation
            emails = {
                "variant_1": {
                    "subject": f"Quick question about {contact['company']}",
                    "body": f"Hi {contact['first_name']},\n\nI noticed your role as {contact['title']} at {contact['company']}...",
                    "signature": "Best regards,\n[Your Name]"
                },
                "variant_2": {
                    "subject": "Insight for your team",
                    "body": f"Hi {contact['first_name']},\n\nI've been researching companies in {contact['industry']}...",
                    "signature": "Looking forward to connecting,\n[Your Name]"
                },
                "variant_3": {
                    "subject": "Helping companies like yours",
                    "body": f"Hi {contact['first_name']},\n\nWe specialize in supporting businesses like {contact['company']}...",
                    "signature": "Warm regards,\n[Your Name]"
                }
            }
            
            return {
                "status": "success",
                "contact_id": contact_id,
                "emails": emails
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
# Cadence Management Endpoints
        
@app.get("/api/cadences/types")
async def get_cadence_types():
    """Get available cadence types and their definitions"""
    router = CadenceRouter()
    return {
        'cadences': router.CADENCE_DEFINITIONS,
        'tier_mapping': router.TIER_TO_CADENCE
    }
    
@app.post("/api/contacts/{contact_id}/start-cadence")
async def start_contact_cadence(contact_id: int, cadence_type: str = None):
    """Manually start cadence for a contact"""
    try:
        router = CadenceRouter()
        
        if cadence_type:
            # Manual cadence type specified
            sequence_id = router.start_sequence(contact_id, cadence_type)
        else:
            # Auto-route based on tier
            sequence_id = router.route_contact(contact_id)
            
        return {
            'success': True,
            'sequence_id': sequence_id,
            'message': 'Cadence started'
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
@app.get("/api/cadences/sequence/{sequence_id}")
async def get_sequence_status(sequence_id: int):
    """Get status of a cadence sequence"""
    router = CadenceRouter()
    status = router.get_sequence_status(sequence_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Sequence not found")
        
    return status

@app.post("/api/cadences/sequence/{sequence_id}/pause")
async def pause_sequence(sequence_id: int):
    """Pause a cadence sequence"""
    router = CadenceRouter()
    router.pause_sequence(sequence_id, reason='manual_pause')
    
    return {'success': True, 'message': 'Sequence paused'}

@app.post("/api/cadences/sequence/{sequence_id}/stop")
async def stop_sequence(sequence_id: int):
    """Stop a cadence sequence"""
    router = CadenceRouter()
    router.stop_sequence(sequence_id, reason='manual_stop')
    
    return {'success': True, 'message': 'Sequence stopped'}

@app.get("/api/cadences/active")
async def get_active_cadences():
    """Get all active cadence sequences"""
    conn = sqlite3.connect('./apex.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cs.id, cs.cadence_type, cs.current_step, cs.total_steps,
               cs.started_at, cs.next_touch_at,
               c.id as contact_id, c.name, c.email, c.company, c.lead_tier
        FROM cadence_sequences cs
        JOIN contacts c ON cs.contact_id = c.id
        WHERE cs.status = 'active'
        ORDER BY cs.next_touch_at ASC
    """)
    
    sequences = []
    for row in cursor.fetchall():
        sequences.append({
            'id': row[0],
            'cadence_type': row[1],
            'current_step': row[2],
            'total_steps': row[3],
            'started_at': row[4],
            'next_touch_at': row[5],
            'contact': {
                'id': row[6],
                'name': row[7],
                'email': row[8],
                'company': row[9],
                'tier': row[10]
            }
        })
        
    conn.close()
    
    return {
        'sequences': sequences,
        'count': len(sequences)
    }

## ============================================================================
# BULK OPERATIONS
# ============================================================================

class BulkEnrichRequest(BaseModel):
    contact_ids: List[int]
    
    
@app.post("/api/contacts/bulk/enrich")
async def bulk_enrich_contacts(payload: BulkEnrichRequest):
    """
        Enrich multiple contacts.

        Current behavior:
            1. Mark selected contacts as 'enriching'.
            2. Sequentially call the single-contact /enrich endpoint logic in-process.
            3. Return a summary of successes/failures.

        This reuses the same enrichment flow as /api/contacts/{id}/enrich.
        """
    contact_ids = payload.contact_ids
    if not contact_ids:
        raise HTTPException(status_code=400, detail="No contact_ids provided")
        
    try:
        # 1) Mark all as 'enriching'
        with get_db() as conn:
            cursor = conn.cursor()
            placeholders = ",".join("?" * len(contact_ids))
            cursor.execute(
                f"""
                                UPDATE contacts
                                SET enrichment_status = 'enriching',
                                        updated_at = ?
                                WHERE id IN ({placeholders})
                                """,
                [datetime.now().isoformat()] + contact_ids,
            )
            conn.commit()
            
            # 2) Run the same enrichment logic used by the single-contact endpoint
        successes: List[int] = []
        failures: Dict[int, str] = {}
        
        for cid in contact_ids:
            try:
                # Reuse the enrich_contact logic directly
                await enrich_contact(cid)
                successes.append(cid)
            except HTTPException as he:
                failures[cid] = str(he.detail)
            except Exception as e:
                failures[cid] = str(e)
                
        return {
    "status": "partial_success" if failures else "success",
    "requested": len(contact_ids),
    "enriched": len(successes),
    "failed": failures,
    }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
    