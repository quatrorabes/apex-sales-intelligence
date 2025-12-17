# SURGICAL FIX: Replace beginning of main.py up to "# PYDANTIC MODELS" section
# Copy this block EXACTLY and replace lines 1-100 (approx) of your main.py

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from decimal import Decimal
from pathlib import Path

# ============================================================================
# FIX IMPORT PATHS FOR RENDER DEPLOYMENT (CRITICAL)
# ============================================================================
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    redirect_slashes=False,
    title="Apex Sales Intelligence API v2.0",
    description="Multi-vertical sales intelligence with APEX, BANT, and SPICE qualification frameworks",
    version="2.0.0"
)

ALLOWED_ORIGINS = [
    "https://apex-sales-intelligence.vercel.app",
    "https://apex-sales-intelligence-*.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATABASE CONNECTION
# ============================================================================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")
    
@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()
        
# ============================================================================
# ENRICHMENT ENGINE v3.0 - APEX (PRIORITY)
# ============================================================================
enrichment_engine_v3 = None

try:
    from engines.intelligence.enrichment import ApexEnrichmentEngineV3
    enrichment_engine_v3 = ApexEnrichmentEngineV3()
    logger.info("✅ APEX Enrichment Engine v3.0 initialized successfully")
except ImportError as e:
    logger.warning(f"⚠️ APEX v3.0 enrichment engine not found: {str(e)}")
except Exception as e:
    logger.error(f"❌ Error initializing APEX v3.0 engine: {str(e)}")
    
# ============================================================================
# LEGACY ENRICHMENT ENGINE (FALLBACK)
# ============================================================================
enrichment_engine = None

try:
    from enrichment_engine import EnhancedEnrichment
    enrichment_engine = EnhancedEnrichment()
    logger.info("✅ Legacy enrichment engine loaded (fallback)")
except ImportError:
    logger.warning("⚠️ Legacy enrichment engine not available (fallback)")
    
# ============================================================================
# OUTREACH CONTENT GENERATORS - INITIALIZATION
# ============================================================================
content_generator = None
linkedin_engine = None

try:
    from intelligence.engines.outreach.generators import ContentGenerator, LinkedInEngine
    content_generator = ContentGenerator()
    linkedin_engine = LinkedInEngine()
    logger.info("✅ Outreach generators initialized successfully")
except ImportError as e:
    logger.warning(f"⚠️ Outreach generators not found: {str(e)}")
except Exception as e:
    logger.error(f"❌ Error initializing outreach generators: {str(e)}")
    
# ============================================================================
# API ROUTES - V2 ENDPOINTS
# ============================================================================
    
# Import contacts router (REQUIRED)
try:
    from api.routes.contacts_v2 import router as contacts_v2_router
    app.include_router(contacts_v2_router)
    logger.info("✅ Contacts v2 routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Failed to import contacts_v2 routes: {e}")
    
# Import enrichment router (REQUIRED - has the v3.0 engine)
try:
    from api.routes.enrichment import router as enrichment_router
    app.include_router(enrichment_router)
    logger.info("✅ Enrichment routes loaded (v3.0)")
except ImportError as e:
    logger.warning(f"⚠️ Failed to import enrichment routes: {e}")
    
# Import premium enrichment router (OPTIONAL)
try:
    from api.routes.enrichment_premium import router as premium_enrichment_router
    app.include_router(premium_enrichment_router)
    logger.info("✅ Premium enrichment routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Premium enrichment routes not available: {e}")
    
# Import APEX custom enrichment router (OPTIONAL)
try:
    from api.routes.enrichment_apex_custom import router as apex_enrichment_router
    app.include_router(apex_enrichment_router)
    logger.info("✅ APEX custom enrichment routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ APEX custom enrichment routes not available: {e}")
    
# Import playbook router (OPTIONAL)
try:
    from api.routes.playbook import router as playbook_router
    app.include_router(playbook_router)
    logger.info("✅ Playbook routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Playbook routes not available: {e}")
    

# ============================================================================
# PYDANTIC MODELS
# ============================================================================
    
class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    vertical: Optional[str] = Field(default="SaaS")
    
class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    vertical: Optional[str] = None
    
class BANTQualification(BaseModel):
    bant_budget_confirmed: Optional[bool] = None
    bant_budget_range: Optional[str] = None
    bant_authority_level: Optional[str] = None
    bant_decision_maker_identified: Optional[bool] = None
    bant_need_identified: Optional[bool] = None
    bant_pain_severity: Optional[str] = None
    bant_current_solution: Optional[str] = None
    bant_timeline_identified: Optional[bool] = None
    bant_target_close_date: Optional[str] = None
    bant_urgency: Optional[str] = None
    
class SPICEQualification(BaseModel):
    spice_situation_documented: Optional[bool] = None
    spice_situation_summary: Optional[str] = None
    spice_org_structure_known: Optional[bool] = None
    spice_problem_identified: Optional[bool] = None
    spice_problem_description: Optional[str] = None
    spice_problem_owner_known: Optional[bool] = None
    spice_implication_quantified: Optional[bool] = None
    spice_business_impact: Optional[str] = None
    spice_cost_of_inaction: Optional[float] = None
    spice_revenue_opportunity: Optional[float] = None
    spice_critical_event_identified: Optional[bool] = None
    spice_critical_event_description: Optional[str] = None
    spice_critical_event_date: Optional[str] = None
    spice_event_driving_urgency: Optional[bool] = None
    spice_decision_process_known: Optional[bool] = None
    spice_decision_criteria: Optional[Dict[str, Any]] = None
    spice_stakeholders_mapped: Optional[bool] = None
    spice_decision_timeline_confirmed: Optional[bool] = None
    
class ScoreRequest(BaseModel):
    contact_ids: List[int]
    
class EnrollmentRequest(BaseModel):
    contact_id: str
    cadence_name: str
    sequence_days: int = 14
    
# ============================================================================
# SCORING FUNCTIONS
# ============================================================================
    
def calculate_mdcp_score(contact: dict) -> int:
    """Calculate MDCP Score (Match, Data, Contact, Profile)"""
    score = 0
    
    # Match (25 points)
    if contact.get('match_score'):
        score += min(int(contact['match_score'] * 0.25), 25)
    elif contact.get('icp_match_percentage'):
        score += min(int(contact['icp_match_percentage'] * 0.25), 25)
        
    # Data (25 points)
    if contact.get('enrichment_status') == 'completed':
        score += 20
    if contact.get('enrichment_data'):
        score += 5
        
    # Contact (25 points)
    persona = contact.get('persona_type', '')
    if persona in ['DECISION_MAKER', 'CFO', 'CEO']:
        score += 25
    elif persona in ['CHAMPION', 'DIRECTOR', 'VP']:
        score += 20
    elif persona in ['INFLUENCER', 'MANAGER']:
        score += 15
    elif persona in ['INITIATOR']:
        score += 10
        
    # Profile (25 points)
    profile_fields = ['email', 'phone', 'linkedin_url', 'title', 'company']
    filled_fields = sum(1 for field in profile_fields if contact.get(field))
    score += int((filled_fields / len(profile_fields)) * 25)
    
    return min(score, 100)

def calculate_rss_score(contact: dict) -> int:
    """Calculate RSS Score (Readiness, Suitability, Seniority)"""
    score = 0
    
    # Readiness (40 points)
    urgency = contact.get('urgency_level', '')
    if urgency == 'HIGH':
        score += 40
    elif urgency == 'MEDIUM':
        score += 25
    elif urgency == 'LOW':
        score += 10
        
    # Suitability (30 points)
    vertical_fit = contact.get('vertical_fit_score', 0)
    if vertical_fit:
        score += int(vertical_fit * 0.3)
    else:
        if contact.get('company') and contact.get('title'):
            score += 20
        elif contact.get('company') or contact.get('title'):
            score += 10
            
    # Seniority (30 points)
    title = (contact.get('title') or '').lower()
    if any(word in title for word in ['ceo', 'cto', 'cfo', 'president', 'founder', 'owner']):
        score += 30
    elif any(word in title for word in ['vp', 'vice president', 'director', 'head']):
        score += 25
    elif any(word in title for word in ['manager', 'lead', 'senior']):
        score += 15
    elif any(word in title for word in ['coordinator', 'specialist', 'analyst']):
        score += 5
        
    return min(score, 100)

    
    # Suitability (30 points)
    vertical_fit = contact.get('vertical_fit_score', 0)
    if vertical_fit:
        score += int(vertical_fit * 0.3)
    else:
        if contact.get('company') and contact.get('title'):
            score += 20
        elif contact.get('company') or contact.get('title'):
            score += 10
    
    # Seniority (30 points)
    title = (contact.get('title') or '').lower()
    if any(word in title for word in ['ceo', 'cto', 'cfo', 'president', 'founder', 'owner']):
        score += 30
    elif any(word in title for word in ['vp', 'vice president', 'director', 'head']):
        score += 25
    elif any(word in title for word in ['manager', 'lead', 'senior']):
        score += 15
    elif any(word in title for word in ['coordinator', 'specialist', 'analyst']):
        score += 5
    
    return min(score, 100)

def calculate_bant_score(contact: dict) -> dict:
    """Calculate BANT qualification score"""
    budget_score = 0
    authority_score = 0
    need_score = 0
    timeline_score = 0
    
    # Budget (0-25)
    if contact.get('bant_budget_confirmed'):
        budget_score += 15
    budget_range = contact.get('bant_budget_range', '')
    if '$250K+' in budget_range or '$500K+' in budget_range:
        budget_score += 10
    elif '$50K-$250K' in budget_range:
        budget_score += 7
    elif '<$50K' in budget_range:
        budget_score += 3
    
    # Authority (0-25)
    authority_level = contact.get('bant_authority_level', '')
    if authority_level == 'ECONOMIC_BUYER':
        authority_score += 25
    elif authority_level == 'TECHNICAL_BUYER':
        authority_score += 20
    elif authority_level == 'INFLUENCER':
        authority_score += 12
    elif authority_level == 'USER':
        authority_score += 5
    
    if contact.get('bant_decision_maker_identified'):
        authority_score = min(authority_score + 5, 25)
    
    # Need (0-25)
    if contact.get('bant_need_identified'):
        need_score += 10
    pain_severity = contact.get('bant_pain_severity', '')
    if pain_severity == 'CRITICAL':
        need_score += 15
    elif pain_severity == 'HIGH':
        need_score += 10
    elif pain_severity == 'MEDIUM':
        need_score += 5
    elif pain_severity == 'LOW':
        need_score += 2
    
    # Timeline (0-25)
    if contact.get('bant_timeline_identified'):
        timeline_score += 10
    urgency = contact.get('bant_urgency', '')
    if urgency == 'IMMEDIATE':
        timeline_score += 15
    elif urgency == 'THIS_QUARTER':
        timeline_score += 10
    elif urgency == 'THIS_YEAR':
        timeline_score += 5
    elif urgency == 'EXPLORATORY':
        timeline_score += 2
    
    total_score = budget_score + authority_score + need_score + timeline_score
    
    if total_score >= 80:
        status = 'HIGHLY_QUALIFIED'
    elif total_score >= 60:
        status = 'QUALIFIED'
    elif total_score >= 40:
        status = 'PARTIALLY_QUALIFIED'
    else:
        status = 'UNQUALIFIED'
    
    return {
        'budget_score': budget_score,
        'authority_score': authority_score,
        'need_score': need_score,
        'timeline_score': timeline_score,
        'total_score': total_score,
        'qualification_status': status
    }

def calculate_spice_score(contact: dict) -> dict:
    """Calculate SPICE qualification score"""
    situation_score = 0
    problem_score = 0
    implication_score = 0
    critical_event_score = 0
    decision_score = 0
    
    # Situation (0-20)
    if contact.get('spice_situation_documented'):
        situation_score += 10
    if contact.get('spice_org_structure_known'):
        situation_score += 5
    if contact.get('spice_situation_summary'):
        situation_score += 5
    
    # Problem (0-20)
    if contact.get('spice_problem_identified'):
        problem_score += 10
    if contact.get('spice_problem_description'):
        problem_score += 5
    if contact.get('spice_problem_owner_known'):
        problem_score += 5
    
    # Implication (0-20)
    if contact.get('spice_implication_quantified'):
        implication_score += 10
    if contact.get('spice_business_impact'):
        implication_score += 5
    if contact.get('spice_cost_of_inaction'):
        try:
            if float(contact.get('spice_cost_of_inaction', 0) or 0) > 0:
                implication_score += 5
        except (ValueError, TypeError):
            pass
    
    # Critical Event (0-20)
    if contact.get('spice_critical_event_identified'):
        critical_event_score += 10
    if contact.get('spice_event_driving_urgency'):
        critical_event_score += 5
    if contact.get('spice_critical_event_date'):
        critical_event_score += 5
    
    # Decision (0-20)
    if contact.get('spice_decision_process_known'):
        decision_score += 7
    if contact.get('spice_stakeholders_mapped'):
        decision_score += 7
    if contact.get('spice_decision_timeline_confirmed'):
        decision_score += 6
    
    total_score = situation_score + problem_score + implication_score + critical_event_score + decision_score
    
    if total_score >= 80:
        status = 'ADVANCING'
    elif total_score >= 60:
        status = 'QUALIFIED'
    elif total_score >= 40:
        status = 'DEVELOPING'
    else:
        status = 'EXPLORATORY'
    
    return {
        'situation_score': situation_score,
        'problem_score': problem_score,
        'implication_score': implication_score,
        'critical_event_score': critical_event_score,
        'decision_score': decision_score,
        'total_score': total_score,
        'qualification_status': status
    }

def calculate_unified_qualification_score(contact: dict, framework: str = 'HYBRID') -> dict:
    """Calculate unified score across all frameworks"""
    mdcp = contact.get('mdcp_score') or calculate_mdcp_score(contact)
    rss = contact.get('rss_score') or calculate_rss_score(contact)
    apex_score = int((mdcp + rss) / 2)
    
    bant_result = calculate_bant_score(contact)
    spice_result = calculate_spice_score(contact)
    
    if framework == 'HYBRID':
        unified_score = int(
            (apex_score * 0.4) +
            (bant_result['total_score'] * 0.3) +
            (spice_result['total_score'] * 0.3)
        )
    elif framework == 'APEX':
        unified_score = apex_score
    elif framework == 'BANT':
        unified_score = bant_result['total_score']
    elif framework == 'SPICE':
        unified_score = spice_result['total_score']
    else:
        unified_score = apex_score
    
    return {
        'unified_score': unified_score,
        'apex_score': apex_score,
        'mdcp_score': mdcp,
        'rss_score': rss,
        'bant_score': bant_result['total_score'],
        'bant_breakdown': bant_result,
        'spice_score': spice_result['total_score'],
        'spice_breakdown': spice_result,
        'framework': framework
    }

def classify_persona(contact: dict, vertical: str = "SaaS") -> tuple:
    """Classify contact persona"""
    title = (contact.get('title') or '').lower()
    
    persona_maps = {
        "SaaS": {
            "DECISION_MAKER": ['ceo', 'cto', 'cfo', 'president', 'founder', 'owner', 'chief'],
            "CHAMPION": ['vp', 'vice president', 'director', 'head of'],
            "INFLUENCER": ['manager', 'lead', 'senior', 'principal'],
            "INITIATOR": ['coordinator', 'specialist', 'analyst', 'associate']
        },
        "Insurance": {
            "DECISION_MAKER": ['agency owner', 'managing director', 'president', 'ceo'],
            "BROKER": ['broker', 'agent', 'producer'],
            "POLICYHOLDER": ['policyholder', 'insured', 'beneficiary'],
            "INFLUENCER": ['underwriter', 'claims', 'adjuster']
        },
        "Equipment_Leasing": {
            "DECISION_MAKER": ['cfo', 'treasurer', 'president', 'owner'],
            "FLEET_MANAGER": ['fleet manager', 'fleet director', 'operations manager'],
            "PROCUREMENT": ['procurement', 'purchasing', 'buyer'],
            "CFO": ['cfo', 'controller', 'finance director']
        }
    }
    
    persona_map = persona_maps.get(vertical, persona_maps["SaaS"])
    
    for persona, keywords in persona_map.items():
        for keyword in keywords:
            if keyword in title:
                return (persona, 0.85)
    
    return ("INITIATOR", 0.50)

def determine_match_tier(score: int) -> str:
    """Determine ICP match tier"""
    if score >= 80:
        return "HIGH"
    elif score >= 50:
        return "MEDIUM"
    elif score >= 20:
        return "LOW"
    else:
        return "UNQUALIFIED"

def get_qualification_recommendation(unified_result: dict) -> dict:
    """Get actionable recommendations"""
    score = unified_result['unified_score']
    bant = unified_result['bant_breakdown']
    spice = unified_result['spice_breakdown']
    
    recommendations = []
    priority = "LOW"
    
    if score >= 80:
        priority = "CRITICAL"
        recommendations.append("Schedule executive demo immediately")
        recommendations.append("Engage decision maker for proposal discussion")
    elif score >= 65:
        priority = "HIGH"
        recommendations.append("Develop business case with ROI analysis")
        recommendations.append("Map full buying committee")
    elif score >= 50:
        priority = "MEDIUM"
        recommendations.append("Conduct discovery call to qualify further")
        recommendations.append("Identify critical business events")
    else:
        priority = "LOW"
        recommendations.append("Nurture with educational content")
        recommendations.append("Monitor for buying signals")
    
    if bant['budget_score'] < 15:
        recommendations.append("⚠️ Confirm budget availability")
    if bant['authority_score'] < 15:
        recommendations.append("⚠️ Identify economic buyer")
    if spice['critical_event_score'] < 10:
        recommendations.append("⚠️ Discover critical business events")
    
    return {
        "priority": priority,
        "recommended_actions": recommendations,
        "next_best_action": recommendations[0] if recommendations else "Continue qualification"
    }

# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Apex Sales Intelligence API",
        "status": "operational",
        "version": "2.0.0",
        "frameworks": ["APEX (MDCP+RSS)", "BANT", "SPICE"],
        "verticals": ["SaaS", "Insurance", "Equipment_Leasing", "Custom"],
        "features": [
            "Multi-Framework Qualification",
            "Deep Enrichment (3-stage Perplexity)",
            "Unified Scoring Engine",
            "Persona Classification",
            "ICP Matching",
            "Cadence Management",
            "Content Generation",
            "Analytics Dashboard"
        ]
    }

@app.get("/health", tags=["Health"])
async def health():
    """Health check"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE unified_qualification_score IS NOT NULL")
            scored = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE bant_total_score > 0")
            bant_qualified = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE spice_total_score > 0")
            spice_qualified = cursor.fetchone()["count"]
            
            cursor.execute("SELECT vertical, COUNT(*) as count FROM contacts GROUP BY vertical")
            verticals = {row["vertical"]: row["count"] for row in cursor.fetchall()}
            
            cursor.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "total_contacts": total,
            "enriched_contacts": enriched,
            "apex_scored": scored,
            "bant_qualified": bant_qualified,
            "spice_qualified": spice_qualified,
            "vertical_breakdown": verticals,
            "enrichment_engine": "available" if enrichment_engine else "unavailable",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

# ============================================================================
# CONTACT CRUD ENDPOINTS
# ============================================================================



# ============================================================================
# V2 CONTACTS ENDPOINT (Frontend Primary)
# ============================================================================

@app.get("/api/v2/contacts", tags=["Contacts V2"])
async def list_contacts_v2(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """V2 Contacts endpoint - returns data in format frontend expects"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, name, email, company, title, phone, linkedin_url,
                    enrichment_status, enriched_at, created_at, updated_at,
                    unified_qualification_score, apex_score, mdcp_score, rss_score,
                    vertical, persona_type
                FROM contacts
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            contacts = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            
            cursor.close()
            
            return {
                "success": True,
                "contacts": contacts,
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.error(f"v2_contacts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/contacts", tags=["Contacts"])
async def list_contacts(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    enriched_only: bool = False,
    vertical: Optional[str] = None,
    min_apex_score: Optional[int] = None
):
    """List contacts with filtering"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM contacts WHERE 1=1"
            params = []
            
            if search:
                query += " AND (name ILIKE %s OR company ILIKE %s OR email ILIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])
            
            if enriched_only:
                query += " AND enrichment_status = 'completed'"
            
            if vertical:
                query += " AND vertical = %s"
                params.append(vertical)
            
            if min_apex_score is not None:
                query += " AND apex_score >= %s"
                params.append(min_apex_score)
            
            query += " ORDER BY COALESCE(unified_qualification_score, 0) DESC, id DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            contacts = cursor.fetchall()
            
            count_query = "SELECT COUNT(*) as count FROM contacts WHERE 1=1"
            count_params = []
            if search:
                count_query += " AND (name ILIKE %s OR company ILIKE %s OR email ILIKE %s)"
                count_params.extend([search_term, search_term, search_term])
            if enriched_only:
                count_query += " AND enrichment_status = 'completed'"
            if vertical:
                count_query += " AND vertical = %s"
                count_params.append(vertical)
            if min_apex_score is not None:
                count_query += " AND apex_score >= %s"
                count_params.append(min_apex_score)
            
            cursor.execute(count_query, count_params)
            total = cursor.fetchone()["count"]
            
            cursor.close()
            
            return {
                "success": True,
                "contacts": [dict(c) for c in contacts],
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        logger.error(f"List contacts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{contact_id}", tags=["Contacts"])
async def get_contact(contact_id: str):
    """Get single contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            return {
                "success": True,
                "contact": dict(contact)
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts", tags=["Contacts"])
async def create_contact(contact: ContactCreate):
    """Create new contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contacts (name, email, company, title, phone, linkedin_url, vertical, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id
            """, (
                contact.name,
                contact.email,
                contact.company,
                contact.title,
                contact.phone,
                contact.linkedin_url,
                contact.vertical or "SaaS"
            ))
            contact_id = cursor.fetchone()["id"]
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "message": "Contact created successfully"
            }
    except Exception as e:
        logger.error(f"Create contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/contacts/{contact_id}", tags=["Contacts"])
async def update_contact(contact_id: str, contact: ContactUpdate):
    """Update contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            for field in ['name', 'email', 'company', 'title', 'phone', 'linkedin_url', 'vertical']:
                value = getattr(contact, field, None)
                if value is not None:
                    updates.append(f"{field} = %s")
                    params.append(value)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            query = f"UPDATE contacts SET {', '.join(updates)} WHERE id = %s"
            params.append(contact_id)
            
            cursor.execute(query, params)
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            cursor.close()
            
            return {
                "success": True,
                "message": "Contact updated successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/contacts/{contact_id}", tags=["Contacts"])
async def delete_contact(contact_id: str):
    """Delete contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            cursor.close()
            
            return {
                "success": True,
                "message": "Contact deleted successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ENRICHMENT ENDPOINTS
# ============================================================================

@app.post("/api/contacts/{contact_id}/enrich", tags=["Enrichment"])
async def enrich_contact(contact_id: str):
    """Deep enrichment with 3-stage Perplexity search"""
    if not enrichment_engine:
        raise HTTPException(status_code=503, detail="Enrichment engine not available")

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")

            cursor.execute("UPDATE contacts SET enrichment_status = 'enriching' WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()

        contact_dict = dict(contact)

        logger.info(f"🚀 Starting enrichment for {contact_dict.get('name')} (ID: {contact_id})")
        enrichment_result = enrichment_engine.enrich_contact(contact_dict)

        with get_db() as conn:
            cursor = conn.cursor()

            profile_text = enrichment_result.get('profile_text', '')
            # Parse enrichment into structured sections
            raw_profile = enrichment_result.get('profile_text', '')
            enrichment_object = integrate_enrichment_result(raw_profile)
            enrichment_json = json.dumps(enrichment_object)

            cursor.execute("""
                UPDATE contacts SET
                    enrichment_status = 'completed',
                    enriched_at = NOW(),
                    enrichment_data = %s,
                    match_score = COALESCE(match_score, 0) + 20
                WHERE id = %s
            """, (
                enrichment_json,
                contact_id
            ))
            conn.commit()
            cursor.close()
        
        logger.info(f"✅ Enrichment completed for contact {contact_id} ({len(profile_text)} chars)")
        
        return {
            "success": True,
            "contact_id": contact_id,
            "profile_length": len(profile_text),
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enrichment error for contact {contact_id}: {e}")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE contacts SET enrichment_status = 'failed' WHERE id = %s", (contact_id,))
            conn.commit()
            cursor.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/deep-enrich", tags=["Enrichment"])
async def deep_enrich_contact(contact_id: str):
    """Full APEX deep enrichment with scoring"""
    try:
        enrich_result = await enrich_contact(contact_id)
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = dict(cursor.fetchone())
            cursor.close()
        
        vertical = contact.get('vertical', 'SaaS')
        persona, confidence = classify_persona(contact, vertical)
        
        mdcp_score = calculate_mdcp_score(contact)
        rss_score = calculate_rss_score(contact)
        apex_score = int((mdcp_score + rss_score) / 2)
        
        icp_score = contact.get('match_score', 0) or 0
        match_tier = determine_match_tier(icp_score)
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts SET
                    persona_type = %s,
                    persona_confidence = %s,
                    mdcp_score = %s,
                    rss_score = %s,
                    apex_score = %s,
                    match_tier = %s
                WHERE id = %s
            """, (
                persona,
                confidence,
                mdcp_score,
                rss_score,
                apex_score,
                match_tier,
                contact_id
            ))
            conn.commit()
            cursor.close()
        
        return {
            "success": True,
            "contact_id": contact_id,
            "enrichment": enrich_result,
            "persona": {
                "type": persona,
                "confidence": confidence
            },
            "scores": {
                "mdcp": mdcp_score,
                "rss": rss_score,
                "apex": apex_score
            },
            "icp_match": {
                "tier": match_tier,
                "score": icp_score
            }
        }
        
    except Exception as e:
        logger.error(f"Deep enrichment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/enrich-and-score/batch", tags=["Enrichment"])
async def batch_enrich_and_score(request: ScoreRequest):
    """Batch enrich and score"""
    results = []
    for contact_id in request.contact_ids:
        try:
            result = await deep_enrich_contact(contact_id)
            results.append({"contact_id": contact_id, "success": True, "data": result})
        except Exception as e:
            results.append({"contact_id": contact_id, "success": False, "error": str(e)})
    
    return {
        "success": True,
        "total": len(request.contact_ids),
        "completed": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results
    }

# ============================================================================
# QUALIFICATION ENDPOINTS (BANT + SPICE)
# ============================================================================

@app.post("/api/contacts/{contact_id}/qualify/bant", tags=["Qualification"])
async def qualify_contact_bant(contact_id: str, bant_data: BANTQualification):
    """Update BANT qualification"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            updates = []
            params = []
            
            for field, value in bant_data.dict(exclude_unset=True).items():
                updates.append(f"{field} = %s")
                params.append(value)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No BANT fields provided")
            
            params.append(contact_id)
            cursor.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE id = %s", params)
            
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            updated_contact = dict(cursor.fetchone())
            bant_result = calculate_bant_score(updated_contact)
            
            cursor.execute("""
                UPDATE contacts SET
                    bant_budget_score = %s,
                    bant_authority_score = %s,
                    bant_need_score = %s,
                    bant_timeline_score = %s,
                    bant_total_score = %s,
                    bant_qualification_status = %s,
                    qualification_last_updated = NOW()
                WHERE id = %s
            """, (
                bant_result['budget_score'],
                bant_result['authority_score'],
                bant_result['need_score'],
                bant_result['timeline_score'],
                bant_result['total_score'],
                bant_result['qualification_status'],
                contact_id
            ))
            
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "bant_score": bant_result
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"BANT qualification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/qualify/spice", tags=["Qualification"])
async def qualify_contact_spice(contact_id: str, spice_data: SPICEQualification):
    """Update SPICE qualification"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            updates = []
            params = []
            
            for field, value in spice_data.dict(exclude_unset=True).items():
                if field == 'spice_decision_criteria' and isinstance(value, dict):
                    updates.append(f"{field} = %s")
                    params.append(json.dumps(value))
                else:
                    updates.append(f"{field} = %s")
                    params.append(value)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No SPICE fields provided")
            
            params.append(contact_id)
            cursor.execute(f"UPDATE contacts SET {', '.join(updates)} WHERE id = %s", params)
            
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            updated_contact = dict(cursor.fetchone())
            spice_result = calculate_spice_score(updated_contact)
            
            cursor.execute("""
                UPDATE contacts SET
                    spice_situation_score = %s,
                    spice_problem_score = %s,
                    spice_implication_score = %s,
                    spice_critical_event_score = %s,
                    spice_decision_score = %s,
                    spice_total_score = %s,
                    spice_qualification_status = %s,
                    qualification_last_updated = NOW()
                WHERE id = %s
            """, (
                spice_result['situation_score'],
                spice_result['problem_score'],
                spice_result['implication_score'],
                spice_result['critical_event_score'],
                spice_result['decision_score'],
                spice_result['total_score'],
                spice_result['qualification_status'],
                contact_id
            ))
            
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "spice_score": spice_result
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SPICE qualification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/contacts/{contact_id}/qualification-report", tags=["Qualification"])
async def get_qualification_report(contact_id: str, framework: str = Query('HYBRID', regex='^(APEX|BANT|SPICE|HYBRID)$')):
    """Get comprehensive qualification report"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            unified_result = calculate_unified_qualification_score(contact, framework=framework)
            recommendation = get_qualification_recommendation(unified_result)
            
            return {
                "success": True,
                "contact_id": contact_id,
                "contact_name": contact.get('name'),
                "company": contact.get('company'),
                "vertical": contact.get('vertical'),
                "unified_qualification": unified_result,
                "recommendation": recommendation
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Qualification report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/score", tags=["Scoring"])
async def score_contact(contact_id: str):
    """Calculate all scores"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            mdcp_score = calculate_mdcp_score(contact)
            rss_score = calculate_rss_score(contact)
            apex_score = int((mdcp_score + rss_score) / 2)
            bant_result = calculate_bant_score(contact)
            spice_result = calculate_spice_score(contact)
            unified_score = int(
                (apex_score * 0.4) +
                (bant_result['total_score'] * 0.3) +
                (spice_result['total_score'] * 0.3)
            )
            
            cursor.execute("""
                UPDATE contacts SET
                    mdcp_score = %s,
                    rss_score = %s,
                    apex_score = %s,
                    bant_total_score = %s,
                    spice_total_score = %s,
                    unified_qualification_score = %s,
                    qualification_last_updated = NOW()
                WHERE id = %s
            """, (mdcp_score, rss_score, apex_score, bant_result['total_score'], 
                  spice_result['total_score'], unified_score, contact_id))
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "scores": {
                    "mdcp": mdcp_score,
                    "rss": rss_score,
                    "apex": apex_score,
                    "bant": bant_result['total_score'],
                    "spice": spice_result['total_score'],
                    "unified": unified_score
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Score contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/score/batch", tags=["Scoring"])
async def batch_score_contacts(request: ScoreRequest):
    """Batch score contacts"""
    results = []
    for contact_id in request.contact_ids:
        try:
            result = await score_contact(contact_id)
            results.append({"contact_id": contact_id, "success": True, "scores": result["scores"]})
        except Exception as e:
            results.append({"contact_id": contact_id, "success": False, "error": str(e)})
    
    return {
        "success": True,
        "total": len(request.contact_ids),
        "results": results
    }

@app.get("/api/apex/scores", tags=["Scoring"])
async def get_apex_scores(
    min_score: Optional[int] = 0,
    max_score: Optional[int] = 100,
    vertical: Optional[str] = None,
    limit: int = 50
):
    """Get contacts ranked by APEX score"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT id, name, company, title, vertical, apex_score, mdcp_score, rss_score, persona_type
                FROM contacts
                WHERE unified_qualification_score IS NOT NULL
                    AND apex_score >= %s
                    AND apex_score <= %s
            """
            params = [min_score, max_score]
            
            if vertical:
                query += " AND vertical = %s"
                params.append(vertical)
            
            query += " ORDER BY apex_score DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            contacts = cursor.fetchall()
            cursor.close()
            
            return {
                "success": True,
                "contacts": [dict(c) for c in contacts],
                "count": len(contacts)
            }
    except Exception as e:
        logger.error(f"Get APEX scores error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/api/todays-board", tags=["Dashboard"])
async def todays_board():
    """Get today's board"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM contacts 
                ORDER BY COALESCE(unified_qualification_score, 0) DESC, 
                         id DESC 
                LIMIT 20
            """)
            contacts = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE unified_qualification_score >= 70 OR apex_score >= 70
            """)
            high_priority = cursor.fetchone()["count"]
            
            cursor.execute("""
                SELECT COUNT(*) as count FROM contacts 
                WHERE cadence_status = 'active'
            """)
            in_call_queue = cursor.fetchone()["count"]
            
            cursor.close()
            
            high_contacts = [c for c in contacts if (c.get('unified_qualification_score') or c.get('apex_score') or 0) >= 70]
            medium_contacts = [c for c in contacts if 40 <= (c.get('unified_qualification_score') or c.get('apex_score') or 0) < 70]
            low_contacts = [c for c in contacts if (c.get('unified_qualification_score') or c.get('apex_score') or 0) < 40]
            
            return {
                "success": True,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "stats": {
                    "total_contacts": total,
                    "enriched": enriched,
                    "high_match": high_priority,
                    "medium_match": len(medium_contacts),
                    "low_match": len(low_contacts),
                    "cold_call_queue": in_call_queue
                },
                "segments": {
                    "high": high_contacts[:10],
                    "medium": medium_contacts[:10],
                    "low": low_contacts[:10]
                },
                "top_priority": contacts[:20],
                "cold_call_stats": {
                    "total": in_call_queue,
                    "new": 0,
                    "meeting_set": 0
                }
            }
    except Exception as e:
        logger.error(f"todays_board error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics", tags=["Analytics"])
async def get_analytics():
    """Get analytics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total_contacts = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE unified_qualification_score IS NOT NULL")
            scored = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE bant_total_score > 0")
            bant_qualified = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE spice_total_score > 0")
            spice_qualified = cursor.fetchone()["count"]
            
            cursor.execute("SELECT match_tier, COUNT(*) as count FROM contacts WHERE match_tier IS NOT NULL GROUP BY match_tier")
            match_tiers = {row["match_tier"]: row["count"] for row in cursor.fetchall()}
            
            cursor.execute("SELECT persona_type, COUNT(*) as count FROM contacts WHERE persona_type IS NOT NULL GROUP BY persona_type")
            personas = {row["persona_type"]: row["count"] for row in cursor.fetchall()}
            
            cursor.execute("SELECT vertical, COUNT(*) as count FROM contacts GROUP BY vertical")
            verticals = {row["vertical"]: row["count"] for row in cursor.fetchall()}
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE cadence_status = 'active'")
            in_cadence = cursor.fetchone()["count"]
            
            cursor.execute("SELECT AVG(apex_score) as avg_score FROM contacts WHERE unified_qualification_score IS NOT NULL")
            avg_apex = cursor.fetchone()["avg_score"]
            
            cursor.execute("SELECT AVG(unified_qualification_score) as avg_score FROM contacts WHERE unified_qualification_score > 0")
            avg_unified = cursor.fetchone()["avg_score"]
            
            cursor.close()
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "contacts": {
                    "total": total_contacts,
                    "enriched": enriched,
                    "scored": scored,
                    "enrichment_rate": round((enriched / total_contacts * 100), 2) if total_contacts > 0 else 0,
                    "scoring_rate": round((scored / total_contacts * 100), 2) if total_contacts > 0 else 0
                },
                "qualification": {
                    "bant_qualified": bant_qualified,
                    "spice_qualified": spice_qualified,
                    "average_apex_score": round(float(avg_apex), 2) if avg_apex else 0,
                    "average_unified_score": round(float(avg_unified), 2) if avg_unified else 0
                },
                "match_tiers": match_tiers,
                "personas": personas,
                "verticals": verticals,
                "cadence": {
                    "active_enrollments": in_cadence
                }
            }
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/dashboard", tags=["Analytics"])
async def analytics_dashboard():
    """Comprehensive analytics dashboard"""
    try:
        analytics = await get_analytics()
        board = await todays_board()
        
        return {
            "success": True,
            "analytics": analytics,
            "todays_board": board,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Analytics dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/{contact_id}", tags=["Dashboard"])
async def contact_dashboard(contact_id: str):
    """Full contact intelligence dashboard"""
    try:
        contact_response = await get_contact(contact_id)
        contact = contact_response["contact"]
        
        try:
            icp = await get_icp_match(contact_id)
        except:
            icp = {"icp_match": None}
        
        try:
            enrollments = await get_enrollments(contact_id)
        except:
            enrollments = {"enrollments": []}
        
        return {
            "success": True,
            "contact": contact,
            "icp_analysis": icp.get("icp_match"),
            "enrollments": enrollments.get("enrollments", []),
            "scores": {
                "mdcp": contact.get("mdcp_score"),
                "rss": contact.get("rss_score"),
                "apex": contact.get("apex_score"),
                "bant": contact.get("bant_total_score"),
                "spice": contact.get("spice_total_score"),
                "unified": contact.get("unified_qualification_score")
            },
            "persona": {
                "type": contact.get("persona_type"),
                "confidence": contact.get("persona_confidence")
            },
            "enrichment_status": contact.get("enrichment_status"),
            "vertical": contact.get("vertical")
        }
    except Exception as e:
        logger.error(f"Contact dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ICP, ENROLLMENTS, CONTENT GENERATION, LISTS
# ============================================================================

@app.get("/api/contacts/{contact_id}/icp-match", tags=["ICP"])
async def get_icp_match(contact_id: str):
    """Get ICP match"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            cursor.close()
            
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            match_score = contact.get('icp_match_percentage') or contact.get('match_score', 0)
            tier = contact.get('match_tier') or determine_match_tier(match_score)
            
            return {
                "success": True,
                "contact_id": contact_id,
                "icp_match": {
                    "score": match_score,
                    "tier": tier,
                    "company": contact.get('company'),
                    "title": contact.get('title'),
                    "vertical": contact.get('vertical')
                }
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ICP match error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-persona", tags=["Persona"])
async def generate_persona(contact_id: str):
    """Generate persona classification"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            vertical = contact.get('vertical', 'SaaS')
            persona, confidence = classify_persona(contact, vertical)
            
            cursor.execute("""
                UPDATE contacts SET 
                    persona_type = %s,
                    persona_confidence = %s
                WHERE id = %s
            """, (persona, confidence, contact_id))
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "persona": persona,
                "confidence": confidence,
                "vertical": vertical
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate persona error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{contact_id}/enrollments", tags=["Cadence"])
async def get_enrollments(contact_id: str):
    """Get enrollments"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            enrollments = []
            if contact.get('cadence_status') == 'active':
                enrollments.append({
                    "cadence_name": contact.get('cadence_name', 'Default Cadence'),
                    "status": "active",
                    "current_step": contact.get('cadence_step', 1),
                    "total_steps": contact.get('cadence_total_steps', 7),
                    "enrolled_at": contact.get('cadence_enrolled_at'),
                    "next_action": "Send follow-up email",
                    "next_action_date": contact.get('next_cadence_action') or (datetime.now() + timedelta(days=1)).isoformat()
                })
            
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "enrollments": enrollments,
                "count": len(enrollments)
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get enrollments error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/enroll", tags=["Cadence"])
async def enroll_contact(contact_id: str, request: EnrollmentRequest):
    """Enroll contact in cadence"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE contacts SET
                    cadence_status = 'active',
                    cadence_name = %s,
                    cadence_step = 1,
                    cadence_total_steps = %s,
                    cadence_enrolled_at = NOW(),
                    next_cadence_action = NOW() + INTERVAL '1 day'
                WHERE id = %s
            """, (request.cadence_name, request.sequence_days, contact_id))
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            conn.commit()
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "cadence_name": request.cadence_name,
                "sequence_days": request.sequence_days,
                "status": "enrolled"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enroll contact error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-call-script", tags=["Content"])
async def generate_call_script(contact_id: str):
    """Generate call script"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            script = f"""
CALL SCRIPT - {contact.get('name', 'Contact')}
Company: {contact.get('company', 'Unknown')}
Vertical: {contact.get('vertical', 'SaaS')}
APEX Score: {contact.get('apex_score', 'N/A')}
Unified Score: {contact.get('unified_qualification_score', 'N/A')}

Opening:
"Hi {contact.get('name', 'there')}, this is [Your Name] from [Your Company]..."

Value Prop:
"We help {contact.get('vertical', 'SaaS')} companies like {contact.get('company', 'yours')}..."

Discovery:
"What's your current process for [relevant pain point]?"
            """
            
            cursor.close()
            
            return {
                "success": True,
                "contact_id": contact_id,
                "call_script": script.strip()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate call script error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-email", tags=["Content"])
async def generate_email(contact_id: str):
    """Generate email"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            email = f"""
Subject: Quick question for {contact.get('company', 'your team')}

Hi {contact.get('name', 'there')},

I noticed you're {contact.get('title', 'leading efforts')} at {contact.get('company', 'your organization')}.

I work with companies in the {contact.get('vertical', 'SaaS')} space. Would you be open to a brief conversation?

Best regards,
[Your Name]
            """
            
            return {
                "success": True,
                "contact_id": contact_id,
                "email": email.strip()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts/{contact_id}/generate-linkedin", tags=["Content"])
async def generate_linkedin_message(contact_id: str):
    """Generate LinkedIn message"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
            contact = cursor.fetchone()
            if not contact:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            contact = dict(contact)
            
            message = f"""Hi {contact.get('name', 'there')},

I came across your profile and was impressed by your work as {contact.get('title', 'a professional')} at {contact.get('company', 'your company')}.

I'd love to connect!"""
            
            return {
                "success": True,
                "contact_id": contact_id,
                "linkedin_message": message.strip()
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate LinkedIn message error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/smart-lists", tags=["Lists"])
async def get_smart_lists():
    """Get smart lists"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE unified_qualification_score >= 70")
            high_priority = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed' AND enriched_at >= NOW() - INTERVAL '7 days'")
            recently_enriched = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE bant_total_score >= 80")
            bant_qualified = cursor.fetchone()["count"]
            
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE spice_total_score >= 70")
            spice_advancing = cursor.fetchone()["count"]
            
            cursor.close()
            
            return {
                "success": True,
                "lists": [
                    {"id": "high-priority", "name": "High Priority", "count": high_priority},
                    {"id": "recently-enriched", "name": "Recently Enriched", "count": recently_enriched},
                    {"id": "bant-qualified", "name": "BANT Qualified", "count": bant_qualified},
                    {"id": "spice-advancing", "name": "SPICE Advancing", "count": spice_advancing}
                ]
            }
    except Exception as e:
        logger.error(f"Smart lists error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cold-call/queue", tags=["Queues"])
async def cold_call_queue():
    """Get cold call queue"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM contacts
                WHERE cadence_status = 'active'
                ORDER BY COALESCE(unified_qualification_score, 0) DESC
                LIMIT 20
            """)
            queue = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            
            return {
                "success": True,
                "queue": queue,
                "count": len(queue),
                "generated_at": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Cold call queue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hubspot/import", tags=["HubSpot"])
async def import_from_hubspot():
    """Import from HubSpot (placeholder)"""
    return {
        "success": False,
        "message": "HubSpot integration not yet configured",
        "note": "Requires HUBSPOT_API_KEY environment variable"
    }

# ============================================================================
# BATCH ENRICHMENT - DASHBOARD COMPATIBILITY
# ============================================================================

# DISABLED: @app.post("/api/batch/enrich")
# DISABLED: async def batch_enrich_endpoint(request_body: dict = Body(...)):
# DISABLED:     """
# DISABLED:     POST /api/batch/enrich - Queue batch enrichment
# DISABLED:     Body: {"contact_ids": [1,2,3]} or {"limit": 10}
# DISABLED:     """
# DISABLED:     contact_ids = request_body.get("contact_ids", [])
# DISABLED:     limit = request_body.get("limit", 10)
# DISABLED:     
# DISABLED:     if not contact_ids:
# DISABLED:         try:
# DISABLED:             with get_db() as conn:
# DISABLED:                 cursor = conn.cursor()
# DISABLED:                 cursor.execute("""
# DISABLED:                     SELECT id FROM contacts 
# DISABLED:                     WHERE enrichment_status IS NULL OR enrichment_status = 'pending'
# DISABLED:                     LIMIT %s
# DISABLED:                 """, (limit,))
# DISABLED:                 contact_ids = [row[0] for row in cursor.fetchall()]
# DISABLED:         except Exception as e:
# DISABLED:             raise HTTPException(status_code=500, detail=str(e))
# DISABLED:             
# DISABLED:     return {
# DISABLED:         "queued": contact_ids,
# DISABLED:         "status": "queued",
# DISABLED:         "count": len(contact_ids)
# DISABLED:     }
# DISABLED:     
# DISABLED: 
# DISABLED: # ============================================================================
# DISABLED: # STARTUP
# DISABLED: # ============================================================================
# DISABLED: 
# DISABLED: @app.on_event("startup")
# DISABLED: async def startup_event():
# DISABLED:     """Initialize"""
# DISABLED:     logger.info("=" * 70)
# DISABLED:     logger.info("🚀 APEX SALES INTELLIGENCE v2.0 - MULTI-FRAMEWORK PLATFORM")
# DISABLED:     logger.info("=" * 70)
# DISABLED:     logger.info("Frameworks: APEX (MDCP+RSS), BANT, SPICE")
# DISABLED:     logger.info("Verticals: SaaS, Insurance, Equipment Leasing, Custom")
# DISABLED:     
# DISABLED:     try:
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             cursor.execute("SELECT COUNT(*) as count FROM contacts")
# DISABLED:             total = cursor.fetchone()["count"]
# DISABLED:             cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
# DISABLED:             enriched = cursor.fetchone()["count"]
# DISABLED:             cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE unified_qualification_score > 0")
# DISABLED:             qualified = cursor.fetchone()["count"]
# DISABLED:             cursor.close()
# DISABLED:         
# DISABLED:         logger.info(f"✅ Database: {total} contacts ({enriched} enriched, {qualified} qualified)")
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"❌ Database error: {e}")
# DISABLED:     
# DISABLED:     if enrichment_engine:
# DISABLED:         logger.info("✅ Enrichment engine loaded")
# DISABLED:     else:
# DISABLED:         logger.warning("⚠️ Enrichment engine not available")
# DISABLED:     
# DISABLED:     logger.info("=" * 70)
# DISABLED:     logger.info("🎯 APEX v2.0 OPERATIONAL")
# DISABLED:     logger.info("=" * 70)
# DISABLED: 
# DISABLED: if __name__ == "__main__":
# DISABLED:     import uvicorn
# DISABLED:     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
# DISABLED: 
# DISABLED: # =============================================================================
# DISABLED: 
# DISABLED: # ============================================================================
# DISABLED: # TODAYS BOARD ENDPOINT (for Dashboard v1 TodaysBoard component)
# DISABLED: # ============================================================================
# DISABLED: 
# DISABLED: @app.get("/api/todays-board", tags=["Dashboard"])
# DISABLED: async def get_todays_board():
# DISABLED:     """Get aggregated dashboard data for TodaysBoard component"""
# DISABLED:     try:
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             
# DISABLED:             # Get all contacts with scores
# DISABLED:             cursor.execute("""
# DISABLED:                 SELECT 
# DISABLED:                     id, first_name, last_name, email, phone, company, title,
# DISABLED:                     apex_score, unified_qualification_score, enrichment_status,
# DISABLED:                     enriched_at, match_tier
# DISABLED:                 FROM contacts
# DISABLED:                 ORDER BY COALESCE(apex_score, 0) DESC
# DISABLED:             """)
# DISABLED:             
# DISABLED:             contacts = [dict(row) for row in cursor.fetchall()]
# DISABLED:             
# DISABLED:             # Calculate stats
# DISABLED:             total = len(contacts)
# DISABLED:             enriched = sum(1 for c in contacts if c.get('enrichment_status') == 'completed')
# DISABLED:             
# DISABLED:             # Segment by apex_score (HIGH >= 75, MEDIUM 50-74, LOW < 50)
# DISABLED:             high_contacts = [c for c in contacts if c.get('apex_score', 0) >= 75]
# DISABLED:             medium_contacts = [c for c in contacts if 50 <= c.get('apex_score', 0) < 75]
# DISABLED:             low_contacts = [c for c in contacts if c.get('apex_score', 0) < 50]
# DISABLED:             
# DISABLED:             cursor.close()
# DISABLED:             
# DISABLED:             return {
# DISABLED:                 "success": True,
# DISABLED:                 "date": datetime.now().strftime("%B %d, %Y"),
# DISABLED:                 "time": datetime.now().strftime("%I:%M %p"),
# DISABLED:                 "stats": {
# DISABLED:                     "total_contacts": total,
# DISABLED:                     "enriched": enriched,
# DISABLED:                     "high_match": len(high_contacts),
# DISABLED:                     "medium_match": len(medium_contacts),
# DISABLED:                     "low_match": len(low_contacts),
# DISABLED:                     "cold_call_queue": len(low_contacts)
# DISABLED:                 },
# DISABLED:                 "segments": {
# DISABLED:                     "high": [
# DISABLED:                         {
# DISABLED:                             "id": c['id'],
# DISABLED:                             "first_name": c.get('first_name'),
# DISABLED:                             "last_name": c.get('last_name'),
# DISABLED:                             "name": f"{c.get('first_name', '')} {c.get('last_name', '')}".strip(),
# DISABLED:                             "email": c.get('email'),
# DISABLED:                             "phone": c.get('phone'),
# DISABLED:                             "company": c.get('company'),
# DISABLED:                             "title": c.get('title'),
# DISABLED:                             "match_score": c.get('apex_score', 0),
# DISABLED:                             "match_tier": "HIGH",
# DISABLED:                             "enrichment_status": c.get('enrichment_status'),
# DISABLED:                             "enriched_at": c.get('enriched_at')
# DISABLED:                         }
# DISABLED:                         for c in high_contacts[:20]
# DISABLED:                     ],
# DISABLED:                     "medium": [
# DISABLED:                         {
# DISABLED:                             "id": c['id'],
# DISABLED:                             "first_name": c.get('first_name'),
# DISABLED:                             "last_name": c.get('last_name'),
# DISABLED:                             "name": f"{c.get('first_name', '')} {c.get('last_name', '')}".strip(),
# DISABLED:                             "email": c.get('email'),
# DISABLED:                             "phone": c.get('phone'),
# DISABLED:                             "company": c.get('company'),
# DISABLED:                             "title": c.get('title'),
# DISABLED:                             "match_score": c.get('apex_score', 0),
# DISABLED:                             "match_tier": "MEDIUM",
# DISABLED:                             "enrichment_status": c.get('enrichment_status'),
# DISABLED:                             "enriched_at": c.get('enriched_at')
# DISABLED:                         }
# DISABLED:                         for c in medium_contacts[:20]
# DISABLED:                     ],
# DISABLED:                     "low": [
# DISABLED:                         {
# DISABLED:                             "id": c['id'],
# DISABLED:                             "first_name": c.get('first_name'),
# DISABLED:                             "last_name": c.get('last_name'),
# DISABLED:                             "name": f"{c.get('first_name', '')} {c.get('last_name', '')}".strip(),
# DISABLED:                             "email": c.get('email'),
# DISABLED:                             "phone": c.get('phone'),
# DISABLED:                             "company": c.get('company'),
# DISABLED:                             "title": c.get('title'),
# DISABLED:                             "match_score": c.get('apex_score', 0),
# DISABLED:                             "match_tier": "LOW",
# DISABLED:                             "enrichment_status": c.get('enrichment_status'),
# DISABLED:                             "enriched_at": c.get('enriched_at')
# DISABLED:                         }
# DISABLED:                         for c in low_contacts[:20]
# DISABLED:                     ]
# DISABLED:                 },
# DISABLED:                 "top_priority": high_contacts[:5],
# DISABLED:                 "cold_call_stats": {
# DISABLED:                     "total": total,
# DISABLED:                     "new": len([c for c in contacts if c.get('enrichment_status') != 'completed']),
# DISABLED:                     "meeting_set": 0
# DISABLED:                 }
# DISABLED:             }
# DISABLED:     
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Todays board error: {e}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED: 
# DISABLED: 
# DISABLED: # ============================================================================
# DISABLED: # COLD CALL QUEUE ENDPOINTS
# DISABLED: # ============================================================================
# DISABLED: 
# DISABLED: @app.get("/api/cold-call/queue", tags=["Cold Call"])
# DISABLED: async def get_cold_call_queue(status: Optional[str] = None):
# DISABLED:     """Get cold call queue - contacts needing outreach"""
# DISABLED:     try:
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             
# DISABLED:             # Get contacts sorted by apex_score, prioritize unenriched
# DISABLED:             query = """
# DISABLED:                 SELECT 
# DISABLED:                     id, name, first_name, last_name, email, phone, linkedin_url,
# DISABLED:                     company, title, apex_score, enrichment_status, created_at
# DISABLED:                 FROM contacts
# DISABLED:                 WHERE phone IS NOT NULL OR email IS NOT NULL
# DISABLED:                 ORDER BY 
# DISABLED:                     CASE WHEN enrichment_status != 'completed' THEN 0 ELSE 1 END,
# DISABLED:                     COALESCE(apex_score, 0) DESC
# DISABLED:                 LIMIT 100
# DISABLED:             """
# DISABLED:             cursor.execute(query)
# DISABLED:             rows = cursor.fetchall()
# DISABLED:             
# DISABLED:             queue = []
# DISABLED:             for row in rows:
# DISABLED:                 r = dict(row)
# DISABLED:                 display_name = r.get('name') or f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or 'Unknown'
# DISABLED:                 queue.append({
# DISABLED:                     "id": r['id'],
# DISABLED:                     "name": display_name,
# DISABLED:                     "phone": r.get('phone'),
# DISABLED:                     "mobile": r.get('phone'),
# DISABLED:                     "email": r.get('email'),
# DISABLED:                     "linkedin_url": r.get('linkedin_url'),
# DISABLED:                     "company": r.get('company'),
# DISABLED:                     "title": r.get('title'),
# DISABLED:                     "quick_fit_score": r.get('apex_score', 0),
# DISABLED:                     "priority": 1 if r.get('apex_score', 0) >= 75 else 2 if r.get('apex_score', 0) >= 50 else 3,
# DISABLED:                     "status": "new",
# DISABLED:                     "attempts": 0,
# DISABLED:                     "contact_id": r['id']
# DISABLED:                 })
# DISABLED:             
# DISABLED:             # Calculate stats
# DISABLED:             total = len(queue)
# DISABLED:             high_priority = len([q for q in queue if q['priority'] == 1])
# DISABLED:             avg_score = sum(q['quick_fit_score'] or 0 for q in queue) / total if total > 0 else 0
# DISABLED:             
# DISABLED:             cursor.close()
# DISABLED:             
# DISABLED:             return {
# DISABLED:                 "success": True,
# DISABLED:                 "queue": queue,
# DISABLED:                 "stats": {
# DISABLED:                     "total": total,
# DISABLED:                     "new": total,
# DISABLED:                     "attempted": 0,
# DISABLED:                     "connected": 0,
# DISABLED:                     "meeting_set": 0,
# DISABLED:                     "high_priority": high_priority,
# DISABLED:                     "avg_score": round(avg_score, 1)
# DISABLED:                 }
# DISABLED:             }
# DISABLED:     
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Cold call queue error: {e}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED: 
# DISABLED: 
# DISABLED: @app.post("/api/cold-call/queue/{item_id}/outcome", tags=["Cold Call"])
# DISABLED: async def log_call_outcome(item_id: int, outcome: str = Body(..., embed=True)):
# DISABLED:     """Log outcome of a cold call"""
# DISABLED:     try:
# DISABLED:         # For now, just acknowledge - can add call_logs table later
# DISABLED:         return {
# DISABLED:             "success": True,
# DISABLED:             "item_id": item_id,
# DISABLED:             "outcome": outcome,
# DISABLED:             "message": "Outcome logged"
# DISABLED:         }
# DISABLED:     except Exception as e:
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED: 
# DISABLED: 
# DISABLED: # ============================================================================
# DISABLED: # SMART LISTS ENDPOINTS
# DISABLED: # ============================================================================
# DISABLED: 
# DISABLED: @app.get("/api/smart-lists", tags=["Smart Lists"])
# DISABLED: async def get_smart_lists():
# DISABLED:     """Get predefined smart lists with counts"""
# DISABLED:     try:
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             
# DISABLED:             # Count contacts for each smart list criteria
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE apex_score >= 75")
# DISABLED:             hot_leads = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE phone IS NOT NULL")
# DISABLED:             ready_to_call = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'completed'")
# DISABLED:             enriched = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status IS NULL OR enrichment_status = 'pending'")
# DISABLED:             needs_enrichment = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE apex_score >= 50 AND apex_score < 75")
# DISABLED:             medium_priority = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE created_at > NOW() - INTERVAL '7 days'")
# DISABLED:             recent = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.close()
# DISABLED:             
# DISABLED:             return {
# DISABLED:                 "success": True,
# DISABLED:                 "lists": [
# DISABLED:                     {"id": "hot-leads", "name": "Hot Leads", "description": "APEX Score 75+", "icon": "flame", "color": "red", "count": hot_leads},
# DISABLED:                     {"id": "ready-to-call", "name": "Ready to Call", "description": "Has phone number", "icon": "phone", "color": "green", "count": ready_to_call},
# DISABLED:                     {"id": "enriched", "name": "Fully Enriched", "description": "Enrichment complete", "icon": "zap", "color": "yellow", "count": enriched},
# DISABLED:                     {"id": "needs-enrichment", "name": "Needs Enrichment", "description": "Not yet enriched", "icon": "clock", "color": "blue", "count": needs_enrichment},
# DISABLED:                     {"id": "medium-priority", "name": "Medium Priority", "description": "APEX Score 50-74", "icon": "crown", "color": "purple", "count": medium_priority},
# DISABLED:                     {"id": "recent", "name": "Added This Week", "description": "Last 7 days", "icon": "sparkles", "color": "cyan", "count": recent}
# DISABLED:                 ]
# DISABLED:             }
# DISABLED:     
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Smart lists error: {e}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED: 
# DISABLED: 
# DISABLED: @app.get("/api/smart-lists/{list_id}/contacts", tags=["Smart Lists"])
# DISABLED: async def get_smart_list_contacts(list_id: str, limit: int = 50):
# DISABLED:     """Get contacts for a specific smart list"""
# DISABLED:     try:
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             
# DISABLED:             # Map list_id to SQL filter
# DISABLED:             filters = {
# DISABLED:                 "hot-leads": "apex_score >= 75",
# DISABLED:                 "ready-to-call": "phone IS NOT NULL",
# DISABLED:                 "enriched": "enrichment_status = 'completed'",
# DISABLED:                 "needs-enrichment": "enrichment_status IS NULL OR enrichment_status = 'pending'",
# DISABLED:                 "medium-priority": "apex_score >= 50 AND apex_score < 75",
# DISABLED:                 "recent": "created_at > NOW() - INTERVAL '7 days'"
# DISABLED:             }
# DISABLED:             
# DISABLED:             where_clause = filters.get(list_id, "1=1")
# DISABLED:             
# DISABLED:             cursor.execute(f"""
# DISABLED:                 SELECT id, name, first_name, last_name, email, company, title, 
# DISABLED:                        apex_score, match_tier, enrichment_status
# DISABLED:                 FROM contacts
# DISABLED:                 WHERE {where_clause}
# DISABLED:                 ORDER BY COALESCE(apex_score, 0) DESC
# DISABLED:                 LIMIT %s
# DISABLED:             """, (limit,))
# DISABLED:             
# DISABLED:             contacts = []
# DISABLED:             for row in cursor.fetchall():
# DISABLED:                 r = dict(row)
# DISABLED:                 display_name = r.get('name') or f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or 'Unknown'
# DISABLED:                 contacts.append({
# DISABLED:                     "id": r['id'],
# DISABLED:                     "name": display_name,
# DISABLED:                     "first_name": r.get('first_name'),
# DISABLED:                     "last_name": r.get('last_name'),
# DISABLED:                     "title": r.get('title'),
# DISABLED:                     "company": r.get('company'),
# DISABLED:                     "match_score": r.get('apex_score', 0),
# DISABLED:                     "match_tier": r.get('match_tier', 'LOW')
# DISABLED:                 })
# DISABLED:             
# DISABLED:             cursor.close()
# DISABLED:             
# DISABLED:             return {
# DISABLED:                 "success": True,
# DISABLED:                 "list_id": list_id,
# DISABLED:                 "contacts": contacts,
# DISABLED:                 "total": len(contacts)
# DISABLED:             }
# DISABLED:     
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Smart list contacts error: {e}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED: 
# DISABLED: 
# DISABLED: # ============================================================================
# DISABLED: # COLD CALL QUEUE ENDPOINTS
# DISABLED: # ============================================================================
# DISABLED: 
# DISABLED: @app.get("/api/cold-call/queue", tags=["Cold Call"])
# DISABLED: async def get_cold_call_queue(status: Optional[str] = None):
# DISABLED:     """Get cold call queue - contacts needing outreach"""
# DISABLED:     try:
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             
# DISABLED:             # Get contacts sorted by apex_score, prioritize unenriched
# DISABLED:             query = """
# DISABLED:                 SELECT 
# DISABLED:                     id, name, first_name, last_name, email, phone, linkedin_url,
# DISABLED:                     company, title, apex_score, enrichment_status, created_at
# DISABLED:                 FROM contacts
# DISABLED:                 WHERE phone IS NOT NULL OR email IS NOT NULL
# DISABLED:                 ORDER BY 
# DISABLED:                     CASE WHEN enrichment_status != 'completed' THEN 0 ELSE 1 END,
# DISABLED:                     COALESCE(apex_score, 0) DESC
# DISABLED:                 LIMIT 100
# DISABLED:             """
# DISABLED:             cursor.execute(query)
# DISABLED:             rows = cursor.fetchall()
# DISABLED:             
# DISABLED:             queue = []
# DISABLED:             for row in rows:
# DISABLED:                 r = dict(row)
# DISABLED:                 display_name = r.get('name') or f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or 'Unknown'
# DISABLED:                 queue.append({
# DISABLED:                     "id": r['id'],
# DISABLED:                     "name": display_name,
# DISABLED:                     "phone": r.get('phone'),
# DISABLED:                     "mobile": r.get('phone'),
# DISABLED:                     "email": r.get('email'),
# DISABLED:                     "linkedin_url": r.get('linkedin_url'),
# DISABLED:                     "company": r.get('company'),
# DISABLED:                     "title": r.get('title'),
# DISABLED:                     "quick_fit_score": r.get('apex_score', 0),
# DISABLED:                     "priority": 1 if r.get('apex_score', 0) >= 75 else 2 if r.get('apex_score', 0) >= 50 else 3,
# DISABLED:                     "status": "new",
# DISABLED:                     "attempts": 0,
# DISABLED:                     "contact_id": r['id']
# DISABLED:                 })
# DISABLED:             
# DISABLED:             # Calculate stats
# DISABLED:             total = len(queue)
# DISABLED:             high_priority = len([q for q in queue if q['priority'] == 1])
# DISABLED:             avg_score = sum(q['quick_fit_score'] or 0 for q in queue) / total if total > 0 else 0
# DISABLED:             
# DISABLED:             cursor.close()
# DISABLED:             
# DISABLED:             return {
# DISABLED:                 "success": True,
# DISABLED:                 "queue": queue,
# DISABLED:                 "stats": {
# DISABLED:                     "total": total,
# DISABLED:                     "new": total,
# DISABLED:                     "attempted": 0,
# DISABLED:                     "connected": 0,
# DISABLED:                     "meeting_set": 0,
# DISABLED:                     "high_priority": high_priority,
# DISABLED:                     "avg_score": round(avg_score, 1)
# DISABLED:                 }
# DISABLED:             }
# DISABLED:     
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Cold call queue error: {e}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED: 
# DISABLED: 
# DISABLED: # ============================================================================
# DISABLED: # SMART LISTS ENDPOINTS
# DISABLED: # ============================================================================
# DISABLED: 
# DISABLED: @app.get("/api/smart-lists", tags=["Smart Lists"])
# DISABLED: async def get_smart_lists():
# DISABLED:     """Get predefined smart lists with counts"""
# DISABLED:     try:
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             
# DISABLED:             # Count contacts for each smart list criteria
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE apex_score >= 75")
# DISABLED:             hot_leads = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE phone IS NOT NULL")
# DISABLED:             ready_to_call = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'completed'")
# DISABLED:             enriched = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status IS NULL OR enrichment_status = 'pending'")
# DISABLED:             needs_enrichment = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE apex_score >= 50 AND apex_score < 75")
# DISABLED:             medium_priority = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.execute("SELECT COUNT(*) FROM contacts WHERE created_at > NOW() - INTERVAL '7 days'")
# DISABLED:             recent = cursor.fetchone()['count']
# DISABLED:             
# DISABLED:             cursor.close()
# DISABLED:             
# DISABLED:             return {
# DISABLED:                 "success": True,
# DISABLED:                 "lists": [
# DISABLED:                     {"id": "hot-leads", "name": "Hot Leads", "description": "APEX Score 75+", "icon": "flame", "color": "red", "count": hot_leads},
# DISABLED:                     {"id": "ready-to-call", "name": "Ready to Call", "description": "Has phone number", "icon": "phone", "color": "green", "count": ready_to_call},
# DISABLED:                     {"id": "enriched", "name": "Fully Enriched", "description": "Enrichment complete", "icon": "zap", "color": "yellow", "count": enriched},
# DISABLED:                     {"id": "needs-enrichment", "name": "Needs Enrichment", "description": "Not yet enriched", "icon": "clock", "color": "blue", "count": needs_enrichment},
# DISABLED:                     {"id": "medium-priority", "name": "Medium Priority", "description": "APEX Score 50-74", "icon": "crown", "color": "purple", "count": medium_priority},
# DISABLED:                     {"id": "recent", "name": "Added This Week", "description": "Last 7 days", "icon": "sparkles", "color": "cyan", "count": recent}
# DISABLED:                 ]
# DISABLED:             }
# DISABLED:     
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Smart lists error: {e}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED: 
# DISABLED: 
# DISABLED:         
# DISABLED: @app.get("/api/user/profile", tags=["User"])
# DISABLED: async def get_user_profile(user_id: str = "default"):
# DISABLED:     """Get user profile and preferences"""
# DISABLED:     return {
# DISABLED:         "success": True,
# DISABLED:         "user_id": user_id,
# DISABLED:         "name": "Sales User",
# DISABLED:         "role": "Sales Rep",
# DISABLED:         "preferences": {
# DISABLED:             "default_view": "board",
# DISABLED:             "notifications_enabled": True
# DISABLED:         }
# DISABLED:     }
# DISABLED:     
# DISABLED: # ============================================================================
# DISABLED: # OUTREACH CONTENT GENERATION ENDPOINTS
# DISABLED: # December 15, 2025 - 11:17 PM PST
# DISABLED: # ============================================================================
# DISABLED: 
# DISABLED: @app.post("/api/contacts/{contact_id}/generate-email", tags=["Content"])
# DISABLED: async def generate_email(contact_id: str):
# DISABLED:     """Generate 3-email outreach sequence"""
# DISABLED:     if not content_generator:
# DISABLED:         raise HTTPException(status_code=503, detail="Content generator not available")
# DISABLED:         
# DISABLED:     try:
# DISABLED:         result = await content_generator.generate_all_content(contact_id)
# DISABLED:         
# DISABLED:         if result.get('error'):
# DISABLED:             raise HTTPException(status_code=400, detail=result['error'])
# DISABLED:             
# DISABLED:         return {
# DISABLED:             'contact_id': contact_id,
# DISABLED:             'emails': result['emails'],
# DISABLED:             'generated_at': result['generated_at']
# DISABLED:         }
# DISABLED:     except HTTPException:
# DISABLED:         raise
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error generating email: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:         
# DISABLED:         
# DISABLED: @app.post("/api/contacts/{contact_id}/generate-coldcall", tags=["Content"])
# DISABLED: @app.post("/api/contacts/{contact_id}/generate-call-script", tags=["Content"])
# DISABLED: async def generate_call_script(contact_id: str):
# DISABLED:     """Generate 3 call script variants (fixes 404 issue)"""
# DISABLED:     if not content_generator:
# DISABLED:         raise HTTPException(status_code=503, detail="Content generator not available")
# DISABLED:         
# DISABLED:     try:
# DISABLED:         result = await content_generator.generate_all_content(contact_id)
# DISABLED:         
# DISABLED:         if result.get('error'):
# DISABLED:             raise HTTPException(status_code=400, detail=result['error'])
# DISABLED:             
# DISABLED:         return {
# DISABLED:             'contact_id': contact_id,
# DISABLED:             'scripts': result['scripts'],
# DISABLED:             'generated_at': result['generated_at']
# DISABLED:         }
# DISABLED:     except HTTPException:
# DISABLED:         raise
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error generating call scripts: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:         
# DISABLED:         
# DISABLED: @app.post("/api/contacts/{contact_id}/generate-linkedin", tags=["Content"])
# DISABLED: async def generate_linkedin_message(contact_id: str):
# DISABLED:     """Generate LinkedIn connection request + follow-up"""
# DISABLED:     if not content_generator or not linkedin_engine:
# DISABLED:         raise HTTPException(status_code=503, detail="LinkedIn generator not available")
# DISABLED:         
# DISABLED:     try:
# DISABLED:         result = await content_generator.generate_all_content(contact_id)
# DISABLED:         
# DISABLED:         if result.get('error'):
# DISABLED:             raise HTTPException(status_code=400, detail=result['error'])
# DISABLED:             
# DISABLED:         # Also create LinkedIn prospect record if URL exists
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             cursor.execute("""
# DISABLED:                 SELECT linkedin_url FROM contacts WHERE id = %s
# DISABLED:             """, (contact_id,))
# DISABLED:             row = cursor.fetchone()
# DISABLED:             
# DISABLED:             if row and row.get('linkedin_url'):
# DISABLED:                 linkedin_engine.add_prospect(
# DISABLED:                     linkedin_url=row['linkedin_url'],
# DISABLED:                     contact_id=contact_id
# DISABLED:                 )
# DISABLED:                 
# DISABLED:         return {
# DISABLED:             'contact_id': contact_id,
# DISABLED:             'linkedin': result['linkedin'],
# DISABLED:             'generated_at': result['generated_at']
# DISABLED:         }
# DISABLED:     except HTTPException:
# DISABLED:         raise
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error generating LinkedIn message: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:         
# DISABLED:         
# DISABLED: @app.get("/api/contacts/{contact_id}/outreach-content", tags=["Content"])
# DISABLED: async def get_outreach_content(contact_id: str):
# DISABLED:     """Get all generated outreach content for a contact"""
# DISABLED:     try:
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             cursor.execute("""
# DISABLED:                 SELECT * FROM outreach_content
# DISABLED:                 WHERE contact_id = %s
# DISABLED:             """, (contact_id,))
# DISABLED:             
# DISABLED:             content = cursor.fetchone()
# DISABLED:             
# DISABLED:             if not content:
# DISABLED:                 raise HTTPException(status_code=404, detail="No content generated yet")
# DISABLED:                 
# DISABLED:             return dict(content)
# DISABLED:         
# DISABLED:     except HTTPException:
# DISABLED:         raise
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error fetching content: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:         
# DISABLED:         
# DISABLED: @app.get("/api/contacts/{contact_id}/call-assistant-data", tags=["Content"])
# DISABLED: async def get_call_assistant_data(contact_id: str):
# DISABLED:     """Get data needed for call assistant UI"""
# DISABLED:     try:
# DISABLED:         with get_db() as conn:
# DISABLED:             cursor = conn.cursor()
# DISABLED:             
# DISABLED:             cursor.execute("""
# DISABLED:                 SELECT 
# DISABLED:                     c.id, c.name, c.email, c.company, c.title, c.phone,
# DISABLED:                     c.apex_score, c.enrichment,
# DISABLED:                     o.call_script_1, o.call_script_2, o.call_script_3
# DISABLED:                 FROM contacts c
# DISABLED:                 LEFT JOIN outreach_content o ON c.id = o.contact_id
# DISABLED:                 WHERE c.id = %s
# DISABLED:             """, (contact_id,))
# DISABLED:             
# DISABLED:             row = cursor.fetchone()
# DISABLED:             if not row:
# DISABLED:                 raise HTTPException(status_code=404, detail="Contact not found")
# DISABLED:                 
# DISABLED:             contact = dict(row)
# DISABLED:             
# DISABLED:             # Parse name
# DISABLED:             name_parts = contact.get('name', '').split(maxsplit=1)
# DISABLED:             firstname = name_parts[0] if name_parts else ''
# DISABLED:             lastname = name_parts[1] if len(name_parts) > 1 else ''
# DISABLED:             
# DISABLED:             # Determine tier from score
# DISABLED:             score = contact.get('apex_score', 0) or 0
# DISABLED:             if score >= 75:
# DISABLED:                 tier = 'HIGH'
# DISABLED:             elif score >= 50:
# DISABLED:                 tier = 'MEDIUM'
# DISABLED:             elif score >= 20:
# DISABLED:                 tier = 'LOW'
# DISABLED:             else:
# DISABLED:                 tier = 'UNQUALIFIED'
# DISABLED:                 
# DISABLED:             # Get profile context
# DISABLED:             enrichment = contact.get('enrichment', {}) or {}
# DISABLED:             sections = enrichment.get('sections', {}) or {}
# DISABLED:             profile_context = sections.get('1._overview', '')[:200] if sections else ''
# DISABLED:             
# DISABLED:             return {
# DISABLED:                 'contact_id': contact_id,
# DISABLED:                 'name': contact.get('name'),
# DISABLED:                 'firstname': firstname,
# DISABLED:                 'lastname': lastname,
# DISABLED:                 'company': contact.get('company'),
# DISABLED:                 'title': contact.get('title'),
# DISABLED:                 'phone': contact.get('phone'),
# DISABLED:                 'score': score,
# DISABLED:                 'tier': tier,
# DISABLED:                 'profile_context': profile_context,
# DISABLED:                 'call_script_1': contact.get('call_script_1'),
# DISABLED:                 'call_script_2': contact.get('call_script_2'),
# DISABLED:                 'call_script_3': contact.get('call_script_3'),
# DISABLED:                 'has_scripts': bool(contact.get('call_script_1'))
# DISABLED:             }
# DISABLED:         
# DISABLED:     except HTTPException:
# DISABLED:         raise
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error getting call assistant data: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:         
# DISABLED:         
# DISABLED: # ============================================================================
# DISABLED: # LINKEDIN AUTOMATION ENDPOINTS
# DISABLED: # ============================================================================
# DISABLED:         
# DISABLED: @app.get("/api/linkedin/quota", tags=["LinkedIn"])
# DISABLED: async def get_linkedin_quota():
# DISABLED:     """Get today's LinkedIn quota status"""
# DISABLED:     if not linkedin_engine:
# DISABLED:         raise HTTPException(status_code=503, detail="LinkedIn engine not available")
# DISABLED:         
# DISABLED:     try:
# DISABLED:         quota = linkedin_engine.get_daily_quota_status()
# DISABLED:         return quota
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error getting LinkedIn quota: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:         
# DISABLED:         
# DISABLED: @app.get("/api/linkedin/analytics", tags=["LinkedIn"])
# DISABLED: async def get_linkedin_analytics():
# DISABLED:     """Get LinkedIn outreach analytics"""
# DISABLED:     if not linkedin_engine:
# DISABLED:         raise HTTPException(status_code=503, detail="LinkedIn engine not available")
# DISABLED:         
# DISABLED:     try:
# DISABLED:         analytics = linkedin_engine.get_analytics()
# DISABLED:         return analytics
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error getting LinkedIn analytics: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:         
# DISABLED:         
# DISABLED: @app.get("/api/linkedin/pending", tags=["LinkedIn"])
# DISABLED: async def get_linkedin_pending():
# DISABLED:     """Get pending LinkedIn actions for today"""
# DISABLED:     if not linkedin_engine:
# DISABLED:         raise HTTPException(status_code=503, detail="LinkedIn engine not available")
# DISABLED:         
# DISABLED:     try:
# DISABLED:         pending = linkedin_engine.get_pending_actions()
# DISABLED:         return pending
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error getting pending actions: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:         
# DISABLED: @app.post("/api/contacts/{contact_id}/generate-all-content")
# DISABLED: async def generate_all_outreach_content(contact_id: str):
# DISABLED:     """Generate complete outreach package (emails + calls + LinkedIn)"""
# DISABLED:     if not content_generator:
# DISABLED:         raise HTTPException(status_code=503, detail="Content generator not available")
# DISABLED:     
# DISABLED:     try:
# DISABLED:         result = await content_generator.generate_all_content(contact_id)
# DISABLED:         return result
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error generating all content: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED: 
# DISABLED: # ==============================================================================
# DISABLED: # STAGE GATE SYSTEM - SPICE + BANT READINESS
# DISABLED: # ==============================================================================
# DISABLED: 
# DISABLED: @app.get("/api/contacts/{contact_id}/stage-gate-status")
# DISABLED: def get_stage_gate_status(contact_id: str):
# DISABLED:     """
# DISABLED:     Calculate sales stage readiness based on SPICE + BANT completion
# DISABLED:     Returns current stage, next action, and gate blockers
# DISABLED:     """
# DISABLED:     conn = get_db_connection()
# DISABLED:     try:
# DISABLED:         cursor = conn.cursor()
# DISABLED:         cursor.execute("""
# DISABLED:             SELECT 
# DISABLED:                 id, name, company, title,
# DISABLED:                 apex_score, mdcp_score, rss_score,
# DISABLED:                 spice_total_score,
# DISABLED:                 spice_situation_score, spice_problem_score, 
# DISABLED:                 spice_implication_score, spice_critical_event_score, 
# DISABLED:                 spice_decision_score,
# DISABLED:                 bant_total_score,
# DISABLED:                 bant_budget_score, bant_authority_score,
# DISABLED:                 bant_need_score, bant_timeline_score,
# DISABLED:                 bant_budget_confirmed, bant_authority_level,
# DISABLED:                 bant_timeline_identified,
# DISABLED:                 spice_cost_of_inaction, spice_revenue_opportunity,
# DISABLED:                 spice_critical_event_date, spice_critical_event_description
# DISABLED:             FROM contacts 
# DISABLED:             WHERE id = %s
# DISABLED:         """, (contact_id,))
# DISABLED:         
# DISABLED:         row = cursor.fetchone()
# DISABLED:         if not row:
# DISABLED:             raise HTTPException(status_code=404, detail="Contact not found")
# DISABLED:         
# DISABLED:         contact = dict(row)
# DISABLED:         
# DISABLED:         # Calculate completion percentages
# DISABLED:         spice_score = contact.get('spice_total_score') or 0
# DISABLED:         bant_score = contact.get('bant_total_score') or 0
# DISABLED:         apex_score = contact.get('apex_score') or 0
# DISABLED:         
# DISABLED:         # Determine stage and next actions
# DISABLED:         spice_complete = spice_score >= 60
# DISABLED:         bant_complete = bant_score >= 60
# DISABLED:         apex_fit = apex_score >= 60
# DISABLED:         
# DISABLED:         # Stage gate logic
# DISABLED:         if spice_score < 40 and bant_score < 40:
# DISABLED:             stage = "new_lead"
# DISABLED:             next_action = "Run initial discovery call - capture SPICE or BANT data"
# DISABLED:             blocked = True
# DISABLED:             can_propose = False
# DISABLED:             priority = "low"
# DISABLED:             
# DISABLED:         elif spice_complete and not bant_complete:
# DISABLED:             stage = "qualification_needed"
# DISABLED:             next_action = "Validate BANT - confirm budget, authority, and timeline"
# DISABLED:             blocked = True
# DISABLED:             can_propose = False
# DISABLED:             priority = "medium"
# DISABLED:             
# DISABLED:         elif bant_complete and not spice_complete:
# DISABLED:             stage = "discovery_needed"
# DISABLED:             next_action = "Deepen SPICE discovery - quantify business impact and urgency"
# DISABLED:             blocked = True
# DISABLED:             can_propose = False
# DISABLED:             priority = "medium"
# DISABLED:             
# DISABLED:         elif spice_complete and bant_complete and not apex_fit:
# DISABLED:             stage = "poor_fit"
# DISABLED:             next_action = "ICP fit too low - consider nurture track or disqualify"
# DISABLED:             blocked = True
# DISABLED:             can_propose = False
# DISABLED:             priority = "low"
# DISABLED:             
# DISABLED:         elif spice_complete and bant_complete and apex_fit:
# DISABLED:             stage = "proposal_ready"
# DISABLED:             next_action = "Generate proposal + schedule executive review"
# DISABLED:             blocked = False
# DISABLED:             can_propose = True
# DISABLED:             priority = "high"
# DISABLED:             
# DISABLED:         else:
# DISABLED:             stage = "in_discovery"
# DISABLED:             next_action = "Continue discovery - capture more SPICE and BANT data"
# DISABLED:             blocked = True
# DISABLED:             can_propose = False
# DISABLED:             priority = "medium"
# DISABLED:         
# DISABLED:         # Calculate readiness breakdown
# DISABLED:         spice_gaps = []
# DISABLED:         if (contact.get('spice_situation_score') or 0) < 15:
# DISABLED:             spice_gaps.append("Situation unclear")
# DISABLED:         if (contact.get('spice_problem_score') or 0) < 15:
# DISABLED:             spice_gaps.append("Problem not identified")
# DISABLED:         if (contact.get('spice_implication_score') or 0) < 15:
# DISABLED:             spice_gaps.append("Business impact not quantified")
# DISABLED:         if (contact.get('spice_critical_event_score') or 0) < 15:
# DISABLED:             spice_gaps.append("No critical event")
# DISABLED:         if (contact.get('spice_decision_score') or 0) < 15:
# DISABLED:             spice_gaps.append("Decision process unknown")
# DISABLED:         
# DISABLED:         bant_gaps = []
# DISABLED:         if (contact.get('bant_budget_score') or 0) < 15:
# DISABLED:             bant_gaps.append("Budget not confirmed")
# DISABLED:         if (contact.get('bant_authority_score') or 0) < 15:
# DISABLED:             bant_gaps.append("Authority not mapped")
# DISABLED:         if (contact.get('bant_need_score') or 0) < 15:
# DISABLED:             bant_gaps.append("Need not validated")
# DISABLED:         if (contact.get('bant_timeline_score') or 0) < 15:
# DISABLED:             bant_gaps.append("Timeline not established")
# DISABLED:         
# DISABLED:         # ROI signals
# DISABLED:         roi_quantified = bool(
# DISABLED:             contact.get('spice_cost_of_inaction') or 
# DISABLED:             contact.get('spice_revenue_opportunity')
# DISABLED:         )
# DISABLED:         
# DISABLED:         urgency_signal = bool(contact.get('spice_critical_event_date'))
# DISABLED:         
# DISABLED:         return {
# DISABLED:             "contact_id": contact_id,
# DISABLED:             "contact_name": contact.get('name'),
# DISABLED:             "company": contact.get('company'),
# DISABLED:             
# DISABLED:             "current_stage": stage,
# DISABLED:             "next_action": next_action,
# DISABLED:             "blocked": blocked,
# DISABLED:             "can_propose": can_propose,
# DISABLED:             "priority": priority,
# DISABLED:             
# DISABLED:             "scores": {
# DISABLED:                 "spice": spice_score,
# DISABLED:                 "bant": bant_score,
# DISABLED:                 "apex": apex_score,
# DISABLED:                 "hybrid": int((apex_score * 0.4) + (bant_score * 0.3) + (spice_score * 0.3))
# DISABLED:             },
# DISABLED:             
# DISABLED:             "completion": {
# DISABLED:                 "spice_complete": spice_complete,
# DISABLED:                 "bant_complete": bant_complete,
# DISABLED:                 "apex_fit": apex_fit,
# DISABLED:                 "spice_percentage": spice_score,
# DISABLED:                 "bant_percentage": bant_score
# DISABLED:             },
# DISABLED:             
# DISABLED:             "gaps": {
# DISABLED:                 "spice": spice_gaps,
# DISABLED:                 "bant": bant_gaps
# DISABLED:             },
# DISABLED:             
# DISABLED:             "signals": {
# DISABLED:                 "roi_quantified": roi_quantified,
# DISABLED:                 "cost_of_inaction": contact.get('spice_cost_of_inaction'),
# DISABLED:                 "revenue_opportunity": contact.get('spice_revenue_opportunity'),
# DISABLED:                 "urgency_signal": urgency_signal,
# DISABLED:                 "critical_event_date": contact.get('spice_critical_event_date'),
# DISABLED:                 "critical_event": contact.get('spice_critical_event_description')
# DISABLED:             },
# DISABLED:             
# DISABLED:             "bant_details": {
# DISABLED:                 "budget_confirmed": contact.get('bant_budget_confirmed'),
# DISABLED:                 "authority_level": contact.get('bant_authority_level'),
# DISABLED:                 "timeline_identified": contact.get('bant_timeline_identified')
# DISABLED:             }
# DISABLED:         }
# DISABLED:         
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error calculating stage gate: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:     finally:
# DISABLED:         conn.close()
# DISABLED: 
# DISABLED: 
# DISABLED: @app.get("/api/pipeline/stage-distribution")
# DISABLED: def get_pipeline_stage_distribution():
# DISABLED:     """
# DISABLED:     Get distribution of contacts across stage gates
# DISABLED:     """
# DISABLED:     conn = get_db_connection()
# DISABLED:     try:
# DISABLED:         cursor = conn.cursor()
# DISABLED:         cursor.execute("""
# DISABLED:             SELECT 
# DISABLED:                 COUNT(*) as total,
# DISABLED:                 SUM(CASE WHEN spice_total_score >= 60 AND bant_total_score >= 60 AND apex_score >= 60 THEN 1 ELSE 0 END) as proposal_ready,
# DISABLED:                 SUM(CASE WHEN spice_total_score >= 60 AND bant_total_score < 60 THEN 1 ELSE 0 END) as needs_bant,
# DISABLED:                 SUM(CASE WHEN bant_total_score >= 60 AND spice_total_score < 60 THEN 1 ELSE 0 END) as needs_spice,
# DISABLED:                 SUM(CASE WHEN spice_total_score < 40 AND bant_total_score < 40 THEN 1 ELSE 0 END) as new_leads,
# DISABLED:                 SUM(CASE WHEN spice_total_score >= 40 AND spice_total_score < 60 AND bant_total_score >= 40 AND bant_total_score < 60 THEN 1 ELSE 0 END) as in_discovery
# DISABLED:             FROM contacts
# DISABLED:         """)
# DISABLED:         
# DISABLED:         row = cursor.fetchone()
# DISABLED:         
# DISABLED:         return {
# DISABLED:             "total_contacts": row[0],
# DISABLED:             "stages": {
# DISABLED:                 "proposal_ready": row[1],
# DISABLED:                 "needs_bant_qualification": row[2],
# DISABLED:                 "needs_spice_discovery": row[3],
# DISABLED:                 "new_leads": row[4],
# DISABLED:                 "in_discovery": row[5]
# DISABLED:             },
# DISABLED:             "conversion_funnel": {
# DISABLED:                 "discovery_to_qualified": f"{(row[1] / row[0] * 100):.1f}%" if row[0] > 0 else "0%",
# DISABLED:                 "qualified_rate": f"{((row[1] / row[0]) * 100):.1f}%" if row[0] > 0 else "0%"
# DISABLED:             }
# DISABLED:         }
# DISABLED:         
# DISABLED:     except Exception as e:
# DISABLED:         logger.error(f"Error getting stage distribution: {str(e)}")
# DISABLED:         raise HTTPException(status_code=500, detail=str(e))
# DISABLED:     finally:
# DISABLED:         conn.close()
