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
import sys
from intelligence.outreach.dashboard_bridge import hook_after_enrichment
from intelligence.outreach.apex_script_orchestrator import (
    ScriptOrchestrator,
    DashboardConfigManager
)  # ← Fixed: Added closing parenthesis
from intelligence.engines.enrichment.apex_intelligence_engine import ApexScoringEngine
from intelligence.engines.enrichment.persona_classifier_cre_sba import UltimatePersonaClassifier
from intelligence.engines.scoring.scoring_orchestrator import ScoringOrchestrator
from intelligence.hubspot_sync import HubSpotSync



# Add current directory to path
sys.path.append('.')

# Import the enrichment module
from intelligence.enrichment import enrich_contact

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

        # Create contacts table with ALL required columns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hubspot_id VARCHAR(255),
                hs_object_id VARCHAR(255),
                name VARCHAR(255) NOT NULL,
                firstname VARCHAR(100),
                lastname VARCHAR(100),
                title VARCHAR(200),
                job_title VARCHAR(200),
                company VARCHAR(255),
                industry VARCHAR(100),
                email VARCHAR(255),
                phone VARCHAR(50),
                linkedin_url VARCHAR(500),
                linkedin VARCHAR(500),
                profile_picture_url VARCHAR(500),
                lifecycle_stage VARCHAR(100),
                enrichment_status VARCHAR(50) DEFAULT 'pending',
                enriched_at TIMESTAMP,
                opportunity_score INTEGER DEFAULT 0,
                lead_tier VARCHAR(50),
                buyer_role VARCHAR(100),
                department VARCHAR(100),
                seniority VARCHAR(100),
                hubspot_owner VARCHAR(255),
                last_activity_date TIMESTAMP,
                location VARCHAR(200),
                website VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                tags TEXT,
                notes TEXT,
                source VARCHAR(100),
                campaign VARCHAR(200),
                lead_score INTEGER DEFAULT 0,
                engagement_score INTEGER DEFAULT 0,
                fit_score INTEGER DEFAULT 0,
                activity_score INTEGER DEFAULT 0,
                last_contacted TIMESTAMP,
                times_contacted INTEGER DEFAULT 0,
                last_email_opened TIMESTAMP,
                last_email_clicked TIMESTAMP,
                social_linkedin VARCHAR(500),
                social_twitter VARCHAR(500),
                enrichment_data TEXT,
                pain_points TEXT,
                talking_points TEXT,
                myers_briggs VARCHAR(10),
                hubspot_sync_status VARCHAR(50),
                hubspot_last_synced TIMESTAMP,
                hubspot_error TEXT
            )
        """)

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_enrichment_status ON contacts(enrichment_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_opportunity_score ON contacts(opportunity_score DESC)')

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
        print("✅ Database tables initialized")

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    print("="*70)
    print("🚀 APEX SALES INTELLIGENCE API")
    print("="*70)

    init_db()

    required_env = ['PERPLEXITY_API_KEY']
    missing_env = [env for env in required_env if not os.getenv(env)]

    if missing_env:
        print(f"⚠️ Warning: Missing environment variables: {', '.join(missing_env)}")
    else:
        print("✅ All environment variables configured")

    print("✅ All systems initialized")
    print(f"📚 API Documentation: http://localhost:3000/docs")
    print(f"🔍 ReDoc Documentation: http://localhost:3000/redoc")
    print("="*70)

    yield

    print("="*70)
    print("Shutting down Apex API...")
    print("="*70)

app = FastAPI(
    title="Apex Sales Intelligence API",
    version="2.1.0",
    description="AI-Powered Sales Automation & Intelligence Platform",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3001", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELS
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
# BASIC ENDPOINTS
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

        return {
            "status": "healthy",
            "database": "connected",
            "contacts": contact_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# CONTACT ENDPOINTS
# ============================================================================

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
            contacts = [dict(row) for row in cursor.fetchall()]

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

@app.post("/api/contacts")
async def create_contact(contact: ContactCreate, background_tasks: BackgroundTasks):
    """Create a new contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            firstname = contact.first_name or ""
            lastname = contact.last_name or ""

            cursor.execute("""
                INSERT INTO contacts (
                    hubspot_id, name, firstname, lastname, title, company,
                    industry, email, phone, linkedin_url, lifecycle_stage,
                    enrichment_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (
                contact.hubspot_id, contact.name, firstname,
                lastname, contact.title, contact.company,
                contact.industry, contact.email, contact.phone,
                contact.linkedin_url, contact.lifecycle_stage,
                datetime.now().isoformat()
            ))

            conn.commit()
            contact_id = cursor.lastrowid

            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            new_contact = dict(row)

            # Queue enrichment
            background_tasks.add_task(run_perplexity_enrichment, contact_id, new_contact)

            return new_contact

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENRICHMENT ENDPOINTS
# ============================================================================

@app.post("/api/contacts/{contact_id}/enrich")
async def enrich_contact_endpoint(contact_id: int, background_tasks: BackgroundTasks):
    """Enrich contact with scoring and deep enrichment"""
    try:
        print(f"\n🚀 ENRICHMENT: Contact ID {contact_id}")

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Contact not found")

            contact = dict(row)

            cursor.execute(
                "UPDATE contacts SET enrichment_status = 'enriching' WHERE id = ?",
                (contact_id,)
            )
            conn.commit()

        # Try Apex scoring if available
        try:
            from pathlib import Path
            INTELLIGENCE_PATH = Path(__file__).parent / 'intelligence'
            sys.path.insert(0, str(INTELLIGENCE_PATH))

            from apex_intelligence_engine import ApexScoringEngine
            scoring_engine = ApexScoringEngine(db_path='./apex.db')

            apex_result = scoring_engine.score_contact(
                contact_id=contact_id,
                save_to_db=True
            )

            print(f"✅ Scoring Complete: {apex_result['mdcp_score']}/100")

            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE contacts SET
                        opportunity_score = ?,
                        lead_tier = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (
                    apex_result['mdcp_score'],
                    apex_result['mdcp_tier'],
                    datetime.now().isoformat(),
                    contact_id
                ))
                conn.commit()

        except Exception as e:
            print(f"⚠️ Apex scoring not available: {e}")

        # Queue Perplexity enrichment
        background_tasks.add_task(run_perplexity_enrichment, contact_id, contact)

        return {
            "status": "success",
            "contact_id": contact_id,
            "message": "Enrichment started",
            "enrichment_status": "processing"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/deep-enrich")
async def deep_enrich_contact(contact_id: int, background_tasks: BackgroundTasks):
    """Enhanced deep enrichment with all fixes"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Contact not found")
                
            contact = dict(row)
            
            background_tasks.add_task(run_enhanced_enrichment, contact_id, contact)
            
            return {
                "status": "queued",
                "contact_id": contact_id,
                "message": "Enhanced enrichment started"
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
async def run_enhanced_enrichment(contact_id: int, contact: Dict):
    """Enhanced background task with all fixes"""
    from intelligence.outreach.comprehensive_fix import (
        enhanced_enrich_contact,
        verified_dashboard_transfer,
        generate_content_with_confirmation
    )
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contacts SET enrichment_status = 'enriching' WHERE id = ?",
                (contact_id,)
            )
            conn.commit()
            
        # FIX 1: Enhanced enrichment with LinkedIn
        result = enhanced_enrich_contact(contact_id, contact)
        
        # FIX 2: Verified dashboard transfer
        dashboard_success = verified_dashboard_transfer(contact_id, result)
        
        if dashboard_success:
            # Get the dashboard data
            from intelligence.outreach.dashboard_bridge import DashboardBridge
            bridge = DashboardBridge()
            dashboard_data = bridge.get_dashboard_data(contact_id)
            
            # FIX 3 & 4: Generate content (with confirmation check)
            generated_content = generate_content_with_confirmation(contact_id, dashboard_data)
            
            # Update dashboard with generated content
            dashboard_data['generated_scripts'] = generated_content
            bridge.update_contact(contact_id, dashboard_data)
            
        # Update database with results
        if result["status"] == "success":
            with get_db() as conn:
                cursor = conn.cursor()
                
                # ... existing update code ...
                
                cursor.execute(
                    "UPDATE contacts SET enrichment_status = 'complete', enriched_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), contact_id)
                )
                conn.commit()
                
    except Exception as e:
        print(f"❌ Enrichment error: {e}")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE contacts SET enrichment_status = 'failed' WHERE id = ?",
                (contact_id,)
            )
            conn.commit()

            #FIX 4: OPENAI CONTENT GENERATION
# ========================================
    
#def generate_all_content(dashboard_data: Dict) -> Dict:
#   """Actually call OpenAI to generate content"""
#   
#   try:
#       # Import the actual generators
#       from intelligence.outreach.email_generator import generate_email_variants
#       from intelligence.outreach.call_script_generator_unified import generate_call_scripts
#       
#       contact_data = {
#           'firstname': dashboard_data['contact_info']['name'].split()[0] if dashboard_data['contact_info']['name'] else '',
#           'lastname': dashboard_data['contact_info']['name'].split()[-1] if dashboard_data['contact_info']['name'] else '',
#           'company': dashboard_data['contact_info']['company'],
#           'jobtitle': dashboard_data['contact_info']['title'],
#           'email': dashboard_data['contact_info']['email']
#       }
#       
#       enrichment_data = {
#           'pain_points': dashboard_data['engagement']['pain_points'],
#           'talking_points': dashboard_data['engagement']['talking_points'],
#           'recent_activity': dashboard_data['intelligence']['recent_activity'],
#           'myers_briggs': dashboard_data['intelligence']['myers_briggs']
#       }
#       
#       # Generate email variants
#       print(f"📧 Generating emails via OpenAI...")
#       emails = generate_email_variants(contact_data, enrichment_data)
#       
#       # Generate call scripts
#       print(f"📞 Generating call scripts via OpenAI...")
#       scripts = generate_call_scripts(contact_data, enrichment_data)
#       
#       return {
#           'status': 'generated',
#           'emails': emails,
#           'call_scripts': scripts,
#           'generated_at': datetime.now().isoformat()
#       }
#   
#   except Exception as e:
#       print(f"❌ Content generation error: {e}")
#       return {
#           'status': 'error',
#           'error': str(e)
#       }
    

@app.post("/api/generate-scripts/{contact_id}")
async def generate_scripts(contact_id: int):
    # Get enriched data
    enriched_data = get_enrichment_data(contact_id)
    
    # Initialize orchestrator
    orchestrator = ScriptOrchestrator()
    
    # Generate all scripts
    results = orchestrator.route_for_generation(
        enriched_data, 
        detect_vertical(enriched_data)
    )
    
    return results

@app.post("/api/contacts/{contact_id}/generate-scripts")
async def generate_scripts_for_contact(contact_id: int):
    """Manually trigger script generation"""
    from intelligence.outreach.dashboard_bridge import DashboardBridge
    from intelligence.outreach.comprehensive_fix import generate_all_content
    
    bridge = DashboardBridge()
    dashboard_data = bridge.get_dashboard_data(contact_id)
    
    if not dashboard_data:
        raise HTTPException(status_code=404, detail="No enrichment data found")
        
    # Generate content via OpenAI
    generated = generate_all_content(dashboard_data)
    
    # Update dashboard
    dashboard_data['generated_scripts'] = generated
    bridge.update_contact(contact_id, dashboard_data)
    
    return generated

@app.post("/api/contacts/{contact_id}/verify-linkedin")
async def verify_linkedin(contact_id: int, linkedin_url: str):
    """Verify and update LinkedIn URL"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE contacts SET linkedin_url = ? WHERE id = ?",
            (linkedin_url, contact_id)
        )
        conn.commit()
        
    return {"status": "updated", "linkedin_url": linkedin_url}

@app.get("/api/settings/auto-generate")
async def get_auto_generate_setting():
    """Get auto-generate setting"""
    return {"auto_generate": os.getenv('AUTO_GENERATE_CONTENT', 'true')}

@app.put("/api/settings/auto-generate")
async def update_auto_generate_setting(enabled: bool):
    """Update auto-generate setting"""
    os.environ['AUTO_GENERATE_CONTENT'] = 'true' if enabled else 'false'
    return {"auto_generate": enabled}



# ============================================================================
# ANALYTICS ENDPOINT
# ============================================================================

@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics():
    """Get dashboard analytics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM contacts")
            total_contacts = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'complete'")
            enriched = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'pending'")
            pending = cursor.fetchone()[0]

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
            "lifecycle_breakdown": {},
            "tier_breakdown": {},
            "open_rate": 0.0,
            "sent": 0,
            "errors": 0
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================
# ALL ENDPOINTS - NO DUPLICATES
# ============================================
        
# Import everything at the top
from intelligence.outreach.data_flow_pipeline import (
    run_complete_pipeline,
    DashboardUpdater,
    generate_all_scripts,
    detect_vertical
)
from intelligence.outreach.apex_script_orchestrator import (
    ScriptOrchestrator,
    DashboardConfigManager
)

# 1. PROCESS ENRICHMENT
@app.post("/api/process-enrichment/{contact_id}")
async def process_enrichment(contact_id: int):
    """Process enrichment output and update dashboard"""
    result = run_complete_pipeline(contact_id)
    return result

# 2. GET DASHBOARD DATA
@app.get("/api/dashboard/{contact_id}")
async def get_dashboard_data(contact_id: int):
    """Get dashboard data for a contact"""
    updater = DashboardUpdater()
    data = updater.get_contact(contact_id)
    return data if data else {"error": "Contact not found"}

# 3. REFRESH SCRIPTS
@app.post("/api/refresh-scripts/{contact_id}")
async def refresh_scripts(contact_id: int):
    """Regenerate scripts for a contact"""
    updater = DashboardUpdater()
    data = updater.get_contact(contact_id)
    if data:
        scripts = generate_all_scripts(data)
        data["generated_scripts"] = scripts
        updater.update_contact(contact_id, data)
        return scripts
    return {"error": "Contact not found"}

# 4. UPDATE BUSINESS CONFIG
@app.put("/api/business-config")
async def update_business_config(updates: dict):
    """Update business configuration from dashboard"""
    dashboard = DashboardConfigManager()
    success = dashboard.update_from_dashboard(updates)
    return {"status": "success" if success else "error"}

# 5. GET BUSINESS CONFIG
@app.get("/api/business-config")
async def get_business_config():
    """Get current business configuration for dashboard display"""
    dashboard = DashboardConfigManager()
    return dashboard.get_config_for_generation()

# 6. GENERATE SCRIPTS DIRECTLY (optional - different from refresh)
@app.post("/api/generate-scripts/{contact_id}")
async def generate_scripts(contact_id: int):
    """Generate scripts directly from enriched data"""
    # This is different from refresh - it's for direct generation
    # You might want to get enriched data from your database here
    enriched_data = {}  # Replace with actual data retrieval
    
    orchestrator = ScriptOrchestrator()
    results = orchestrator.route_for_generation(
        enriched_data, 
        detect_vertical(enriched_data)
    )
    return results
    if data:
        return data
    else:
        return {"error": "Contact not found"}

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000, reload=True)
    
    
    
    
# ===============================
# API ENDPOINTS (Add to main.py)
# ===============================
    
    