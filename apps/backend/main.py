"""
APEX SALES INTELLIGENCE v2.0 - PRODUCTION BACKEND
Multi-Vertical Sales Intelligence Platform
Frameworks: APEX (MDCP + RSS) + BANT + SPICE
Verticals: SaaS, Insurance, Equipment Leasing, Custom
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from decimal import Decimal

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


# =============================================================================
# V2 API ROUTES (Clean Schema)
# =============================================================================
from api.routes.contacts_v2 import router as contacts_v2_router
app.include_router(contacts_v2_router)
from api.routes.contacts_v2_enrichment import router as contacts_v2_enrichment_router
app.include_router(contacts_v2_enrichment_router)
from api.routes.enrichment_apex_custom import router as apex_enrichment_router
from api.routes.enrichment_premium import router as premium_enrichment_router
from api.routes.playbook import router as playbook_router
app.include_router(premium_enrichment_router)
app.include_router(apex_enrichment_router)
app.include_router(playbook_router)

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

try:
    from enrichment_engine import EnhancedEnrichment
    enrichment_engine = EnhancedEnrichment()
    logger.info("✅ Enrichment engine loaded")
except ImportError:
    enrichment_engine = None
    logger.warning("⚠️ Enrichment engine not available")

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
    contact_id: int
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
async def get_contact(contact_id: int):
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
async def update_contact(contact_id: int, contact: ContactUpdate):
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
async def delete_contact(contact_id: int):
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
async def enrich_contact(contact_id: int):
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
async def deep_enrich_contact(contact_id: int):
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
async def qualify_contact_bant(contact_id: int, bant_data: BANTQualification):
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
async def qualify_contact_spice(contact_id: int, spice_data: SPICEQualification):
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
async def get_qualification_report(contact_id: int, framework: str = Query('HYBRID', regex='^(APEX|BANT|SPICE|HYBRID)$')):
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
async def score_contact(contact_id: int):
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
async def contact_dashboard(contact_id: int):
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
async def get_icp_match(contact_id: int):
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
async def generate_persona(contact_id: int):
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
async def get_enrollments(contact_id: int):
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
async def enroll_contact(contact_id: int, request: EnrollmentRequest):
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
async def generate_call_script(contact_id: int):
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
async def generate_email(contact_id: int):
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
async def generate_linkedin_message(contact_id: int):
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

@app.post("/api/batch/enrich")
async def batch_enrich_endpoint(request_body: dict = Body(...)):
    """
    POST /api/batch/enrich - Queue batch enrichment
    Body: {"contact_ids": [1,2,3]} or {"limit": 10}
    """
    contact_ids = request_body.get("contact_ids", [])
    limit = request_body.get("limit", 10)
    
    if not contact_ids:
        try:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM contacts 
                    WHERE enrichment_status IS NULL OR enrichment_status = 'pending'
                    LIMIT %s
                """, (limit,))
                contact_ids = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    return {
        "queued": contact_ids,
        "status": "queued",
        "count": len(contact_ids)
    }
    

# ============================================================================
# STARTUP
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize"""
    logger.info("=" * 70)
    logger.info("🚀 APEX SALES INTELLIGENCE v2.0 - MULTI-FRAMEWORK PLATFORM")
    logger.info("=" * 70)
    logger.info("Frameworks: APEX (MDCP+RSS), BANT, SPICE")
    logger.info("Verticals: SaaS, Insurance, Equipment Leasing, Custom")
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM contacts")
            total = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()["count"]
            cursor.execute("SELECT COUNT(*) as count FROM contacts WHERE unified_qualification_score > 0")
            qualified = cursor.fetchone()["count"]
            cursor.close()
        
        logger.info(f"✅ Database: {total} contacts ({enriched} enriched, {qualified} qualified)")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
    
    if enrichment_engine:
        logger.info("✅ Enrichment engine loaded")
    else:
        logger.warning("⚠️ Enrichment engine not available")
    
    logger.info("=" * 70)
    logger.info("🎯 APEX v2.0 OPERATIONAL")
    logger.info("=" * 70)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

# =============================================================================

# ============================================================================
# TODAYS BOARD ENDPOINT (for Dashboard v1 TodaysBoard component)
# ============================================================================

@app.get("/api/todays-board", tags=["Dashboard"])
async def get_todays_board():
    """Get aggregated dashboard data for TodaysBoard component"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get all contacts with scores
            cursor.execute("""
                SELECT 
                    id, first_name, last_name, email, phone, company, title,
                    apex_score, unified_qualification_score, enrichment_status,
                    enriched_at, match_tier
                FROM contacts
                ORDER BY COALESCE(apex_score, 0) DESC
            """)
            
            contacts = [dict(row) for row in cursor.fetchall()]
            
            # Calculate stats
            total = len(contacts)
            enriched = sum(1 for c in contacts if c.get('enrichment_status') == 'completed')
            
            # Segment by apex_score (HIGH >= 75, MEDIUM 50-74, LOW < 50)
            high_contacts = [c for c in contacts if c.get('apex_score', 0) >= 75]
            medium_contacts = [c for c in contacts if 50 <= c.get('apex_score', 0) < 75]
            low_contacts = [c for c in contacts if c.get('apex_score', 0) < 50]
            
            cursor.close()
            
            return {
                "success": True,
                "date": datetime.now().strftime("%B %d, %Y"),
                "time": datetime.now().strftime("%I:%M %p"),
                "stats": {
                    "total_contacts": total,
                    "enriched": enriched,
                    "high_match": len(high_contacts),
                    "medium_match": len(medium_contacts),
                    "low_match": len(low_contacts),
                    "cold_call_queue": len(low_contacts)
                },
                "segments": {
                    "high": [
                        {
                            "id": c['id'],
                            "first_name": c.get('first_name'),
                            "last_name": c.get('last_name'),
                            "name": f"{c.get('first_name', '')} {c.get('last_name', '')}".strip(),
                            "email": c.get('email'),
                            "phone": c.get('phone'),
                            "company": c.get('company'),
                            "title": c.get('title'),
                            "match_score": c.get('apex_score', 0),
                            "match_tier": "HIGH",
                            "enrichment_status": c.get('enrichment_status'),
                            "enriched_at": c.get('enriched_at')
                        }
                        for c in high_contacts[:20]
                    ],
                    "medium": [
                        {
                            "id": c['id'],
                            "first_name": c.get('first_name'),
                            "last_name": c.get('last_name'),
                            "name": f"{c.get('first_name', '')} {c.get('last_name', '')}".strip(),
                            "email": c.get('email'),
                            "phone": c.get('phone'),
                            "company": c.get('company'),
                            "title": c.get('title'),
                            "match_score": c.get('apex_score', 0),
                            "match_tier": "MEDIUM",
                            "enrichment_status": c.get('enrichment_status'),
                            "enriched_at": c.get('enriched_at')
                        }
                        for c in medium_contacts[:20]
                    ],
                    "low": [
                        {
                            "id": c['id'],
                            "first_name": c.get('first_name'),
                            "last_name": c.get('last_name'),
                            "name": f"{c.get('first_name', '')} {c.get('last_name', '')}".strip(),
                            "email": c.get('email'),
                            "phone": c.get('phone'),
                            "company": c.get('company'),
                            "title": c.get('title'),
                            "match_score": c.get('apex_score', 0),
                            "match_tier": "LOW",
                            "enrichment_status": c.get('enrichment_status'),
                            "enriched_at": c.get('enriched_at')
                        }
                        for c in low_contacts[:20]
                    ]
                },
                "top_priority": high_contacts[:5],
                "cold_call_stats": {
                    "total": total,
                    "new": len([c for c in contacts if c.get('enrichment_status') != 'completed']),
                    "meeting_set": 0
                }
            }
    
    except Exception as e:
        logger.error(f"Todays board error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COLD CALL QUEUE ENDPOINTS
# ============================================================================

@app.get("/api/cold-call/queue", tags=["Cold Call"])
async def get_cold_call_queue(status: Optional[str] = None):
    """Get cold call queue - contacts needing outreach"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get contacts sorted by apex_score, prioritize unenriched
            query = """
                SELECT 
                    id, name, first_name, last_name, email, phone, linkedin_url,
                    company, title, apex_score, enrichment_status, created_at
                FROM contacts
                WHERE phone IS NOT NULL OR email IS NOT NULL
                ORDER BY 
                    CASE WHEN enrichment_status != 'completed' THEN 0 ELSE 1 END,
                    COALESCE(apex_score, 0) DESC
                LIMIT 100
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            queue = []
            for row in rows:
                r = dict(row)
                display_name = r.get('name') or f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or 'Unknown'
                queue.append({
                    "id": r['id'],
                    "name": display_name,
                    "phone": r.get('phone'),
                    "mobile": r.get('phone'),
                    "email": r.get('email'),
                    "linkedin_url": r.get('linkedin_url'),
                    "company": r.get('company'),
                    "title": r.get('title'),
                    "quick_fit_score": r.get('apex_score', 0),
                    "priority": 1 if r.get('apex_score', 0) >= 75 else 2 if r.get('apex_score', 0) >= 50 else 3,
                    "status": "new",
                    "attempts": 0,
                    "contact_id": r['id']
                })
            
            # Calculate stats
            total = len(queue)
            high_priority = len([q for q in queue if q['priority'] == 1])
            avg_score = sum(q['quick_fit_score'] or 0 for q in queue) / total if total > 0 else 0
            
            cursor.close()
            
            return {
                "success": True,
                "queue": queue,
                "stats": {
                    "total": total,
                    "new": total,
                    "attempted": 0,
                    "connected": 0,
                    "meeting_set": 0,
                    "high_priority": high_priority,
                    "avg_score": round(avg_score, 1)
                }
            }
    
    except Exception as e:
        logger.error(f"Cold call queue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cold-call/queue/{item_id}/outcome", tags=["Cold Call"])
async def log_call_outcome(item_id: int, outcome: str = Body(..., embed=True)):
    """Log outcome of a cold call"""
    try:
        # For now, just acknowledge - can add call_logs table later
        return {
            "success": True,
            "item_id": item_id,
            "outcome": outcome,
            "message": "Outcome logged"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SMART LISTS ENDPOINTS
# ============================================================================

@app.get("/api/smart-lists", tags=["Smart Lists"])
async def get_smart_lists():
    """Get predefined smart lists with counts"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Count contacts for each smart list criteria
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE apex_score >= 75")
            hot_leads = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE phone IS NOT NULL")
            ready_to_call = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status IS NULL OR enrichment_status = 'pending'")
            needs_enrichment = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE apex_score >= 50 AND apex_score < 75")
            medium_priority = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE created_at > NOW() - INTERVAL '7 days'")
            recent = cursor.fetchone()['count']
            
            cursor.close()
            
            return {
                "success": True,
                "lists": [
                    {"id": "hot-leads", "name": "Hot Leads", "description": "APEX Score 75+", "icon": "flame", "color": "red", "count": hot_leads},
                    {"id": "ready-to-call", "name": "Ready to Call", "description": "Has phone number", "icon": "phone", "color": "green", "count": ready_to_call},
                    {"id": "enriched", "name": "Fully Enriched", "description": "Enrichment complete", "icon": "zap", "color": "yellow", "count": enriched},
                    {"id": "needs-enrichment", "name": "Needs Enrichment", "description": "Not yet enriched", "icon": "clock", "color": "blue", "count": needs_enrichment},
                    {"id": "medium-priority", "name": "Medium Priority", "description": "APEX Score 50-74", "icon": "crown", "color": "purple", "count": medium_priority},
                    {"id": "recent", "name": "Added This Week", "description": "Last 7 days", "icon": "sparkles", "color": "cyan", "count": recent}
                ]
            }
    
    except Exception as e:
        logger.error(f"Smart lists error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/smart-lists/{list_id}/contacts", tags=["Smart Lists"])
async def get_smart_list_contacts(list_id: str, limit: int = 50):
    """Get contacts for a specific smart list"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Map list_id to SQL filter
            filters = {
                "hot-leads": "apex_score >= 75",
                "ready-to-call": "phone IS NOT NULL",
                "enriched": "enrichment_status = 'completed'",
                "needs-enrichment": "enrichment_status IS NULL OR enrichment_status = 'pending'",
                "medium-priority": "apex_score >= 50 AND apex_score < 75",
                "recent": "created_at > NOW() - INTERVAL '7 days'"
            }
            
            where_clause = filters.get(list_id, "1=1")
            
            cursor.execute(f"""
                SELECT id, name, first_name, last_name, email, company, title, 
                       apex_score, match_tier, enrichment_status
                FROM contacts
                WHERE {where_clause}
                ORDER BY COALESCE(apex_score, 0) DESC
                LIMIT %s
            """, (limit,))
            
            contacts = []
            for row in cursor.fetchall():
                r = dict(row)
                display_name = r.get('name') or f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or 'Unknown'
                contacts.append({
                    "id": r['id'],
                    "name": display_name,
                    "first_name": r.get('first_name'),
                    "last_name": r.get('last_name'),
                    "title": r.get('title'),
                    "company": r.get('company'),
                    "match_score": r.get('apex_score', 0),
                    "match_tier": r.get('match_tier', 'LOW')
                })
            
            cursor.close()
            
            return {
                "success": True,
                "list_id": list_id,
                "contacts": contacts,
                "total": len(contacts)
            }
    
    except Exception as e:
        logger.error(f"Smart list contacts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COLD CALL QUEUE ENDPOINTS
# ============================================================================

@app.get("/api/cold-call/queue", tags=["Cold Call"])
async def get_cold_call_queue(status: Optional[str] = None):
    """Get cold call queue - contacts needing outreach"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get contacts sorted by apex_score, prioritize unenriched
            query = """
                SELECT 
                    id, name, first_name, last_name, email, phone, linkedin_url,
                    company, title, apex_score, enrichment_status, created_at
                FROM contacts
                WHERE phone IS NOT NULL OR email IS NOT NULL
                ORDER BY 
                    CASE WHEN enrichment_status != 'completed' THEN 0 ELSE 1 END,
                    COALESCE(apex_score, 0) DESC
                LIMIT 100
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            queue = []
            for row in rows:
                r = dict(row)
                display_name = r.get('name') or f"{r.get('first_name', '')} {r.get('last_name', '')}".strip() or 'Unknown'
                queue.append({
                    "id": r['id'],
                    "name": display_name,
                    "phone": r.get('phone'),
                    "mobile": r.get('phone'),
                    "email": r.get('email'),
                    "linkedin_url": r.get('linkedin_url'),
                    "company": r.get('company'),
                    "title": r.get('title'),
                    "quick_fit_score": r.get('apex_score', 0),
                    "priority": 1 if r.get('apex_score', 0) >= 75 else 2 if r.get('apex_score', 0) >= 50 else 3,
                    "status": "new",
                    "attempts": 0,
                    "contact_id": r['id']
                })
            
            # Calculate stats
            total = len(queue)
            high_priority = len([q for q in queue if q['priority'] == 1])
            avg_score = sum(q['quick_fit_score'] or 0 for q in queue) / total if total > 0 else 0
            
            cursor.close()
            
            return {
                "success": True,
                "queue": queue,
                "stats": {
                    "total": total,
                    "new": total,
                    "attempted": 0,
                    "connected": 0,
                    "meeting_set": 0,
                    "high_priority": high_priority,
                    "avg_score": round(avg_score, 1)
                }
            }
    
    except Exception as e:
        logger.error(f"Cold call queue error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SMART LISTS ENDPOINTS
# ============================================================================

@app.get("/api/smart-lists", tags=["Smart Lists"])
async def get_smart_lists():
    """Get predefined smart lists with counts"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Count contacts for each smart list criteria
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE apex_score >= 75")
            hot_leads = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE phone IS NOT NULL")
            ready_to_call = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status = 'completed'")
            enriched = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE enrichment_status IS NULL OR enrichment_status = 'pending'")
            needs_enrichment = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE apex_score >= 50 AND apex_score < 75")
            medium_priority = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) FROM contacts WHERE created_at > NOW() - INTERVAL '7 days'")
            recent = cursor.fetchone()['count']
            
            cursor.close()
            
            return {
                "success": True,
                "lists": [
                    {"id": "hot-leads", "name": "Hot Leads", "description": "APEX Score 75+", "icon": "flame", "color": "red", "count": hot_leads},
                    {"id": "ready-to-call", "name": "Ready to Call", "description": "Has phone number", "icon": "phone", "color": "green", "count": ready_to_call},
                    {"id": "enriched", "name": "Fully Enriched", "description": "Enrichment complete", "icon": "zap", "color": "yellow", "count": enriched},
                    {"id": "needs-enrichment", "name": "Needs Enrichment", "description": "Not yet enriched", "icon": "clock", "color": "blue", "count": needs_enrichment},
                    {"id": "medium-priority", "name": "Medium Priority", "description": "APEX Score 50-74", "icon": "crown", "color": "purple", "count": medium_priority},
                    {"id": "recent", "name": "Added This Week", "description": "Last 7 days", "icon": "sparkles", "color": "cyan", "count": recent}
                ]
            }
    
    except Exception as e:
        logger.error(f"Smart lists error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


        
@app.get("/api/user/profile", tags=["User"])
async def get_user_profile(user_id: str = "default"):
    """Get user profile and preferences"""
    return {
        "success": True,
        "user_id": user_id,
        "name": "Sales User",
        "role": "Sales Rep",
        "preferences": {
            "default_view": "board",
            "notifications_enabled": True
        }
    }
    