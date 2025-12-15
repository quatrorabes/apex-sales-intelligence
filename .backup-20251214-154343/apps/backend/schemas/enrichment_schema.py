"""
APEX Enrichment Schema v1.0
Single source of truth for all enrichment data structures
"""
from typing import Optional, List, Literal
from pydantic import BaseModel
from datetime import datetime

# =============================================================================
# PROFESSIONAL PROFILE
# =============================================================================
class CurrentRole(BaseModel):
    title: str
    company: str
    tenure: Optional[str] = None
    responsibilities: List[str] = []

class CareerTrajectory(BaseModel):
    previous_roles: List[str] = []
    industry_experience: List[str] = []
    expertise_areas: List[str] = []

class ProfessionalProfile(BaseModel):
    executive_summary: str
    current_role: CurrentRole
    career_trajectory: CareerTrajectory
    education: List[str] = []
    achievements: List[str] = []
    community_involvement: List[str] = []

# =============================================================================
# COMPANY INTELLIGENCE
# =============================================================================
class CompanyOverview(BaseModel):
    name: str
    industry: str
    business_model: str
    founded: Optional[str] = None
    headquarters: Optional[str] = None
    employee_count: Optional[str] = None

class CompanyFinancials(BaseModel):
    revenue: Optional[str] = None
    growth_rate: Optional[str] = None
    funding: Optional[str] = None
    key_metrics: List[str] = []

class MarketPosition(BaseModel):
    target_market: str
    competitive_advantages: List[str] = []
    competitors: List[str] = []

class CompanyIntelligence(BaseModel):
    overview: CompanyOverview
    financials: Optional[CompanyFinancials] = None
    market_position: MarketPosition
    recent_news: List[str] = []
    strategic_priorities: List[str] = []

# =============================================================================
# SALES INTELLIGENCE
# =============================================================================
class PainPoint(BaseModel):
    title: str
    description: str
    priority: Literal['high', 'medium', 'low'] = 'medium'

class Opportunity(BaseModel):
    title: str
    description: str
    alignment: str  # How your product helps

class Objection(BaseModel):
    objection: str
    response: str

class SalesIntelligence(BaseModel):
    match_score: int  # 0-100
    match_reasoning: str
    pain_points: List[PainPoint] = []
    opportunities: List[Opportunity] = []
    buying_triggers: List[str] = []
    decision_factors: List[str] = []
    objections: List[Objection] = []
    why_now: str
    why_us: str

# =============================================================================
# PERSONALITY PROFILE
# =============================================================================
class MBTIDimension(BaseModel):
    dimension: str
    preference: str
    evidence: str

class MBTI(BaseModel):
    type: str  # e.g., "ENTJ"
    dimensions: List[MBTIDimension] = []

class DISC(BaseModel):
    primary: str  # e.g., "D - Dominant"
    secondary: Optional[str] = None

class CommunicationStyle(BaseModel):
    preferences: List[str] = []
    dos: List[str] = []
    donts: List[str] = []

class PersonalityProfile(BaseModel):
    mbti: Optional[MBTI] = None
    disc: Optional[DISC] = None
    communication_style: CommunicationStyle
    best_opening_approach: str

# =============================================================================
# OUTREACH ASSETS
# =============================================================================
class CallScript(BaseModel):
    level: int  # 1, 2, 3
    script: str

class EmailTemplate(BaseModel):
    type: Literal['initial', 'followup', 'breakup']
    subject: str
    body: str

class OutreachAssets(BaseModel):
    talking_points: List[str] = []
    call_scripts: List[CallScript] = []
    email_templates: List[EmailTemplate] = []
    linkedin_message: Optional[str] = None
    voicemail_script: Optional[str] = None

# =============================================================================
# MAIN ENRICHMENT DATA STRUCTURE
# =============================================================================
class EnrichmentData(BaseModel):
    version: str = "1.0"
    generated_at: str  # ISO timestamp
    professional: ProfessionalProfile
    company: CompanyIntelligence
    sales: SalesIntelligence
    personality: PersonalityProfile
    outreach: OutreachAssets

# =============================================================================
# CONTACT MODEL
# =============================================================================
class Contact(BaseModel):
    id: str
    hubspot_id: Optional[str] = None
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    enrichment: Optional[EnrichmentData] = None
    created_at: datetime
    updated_at: datetime
    enriched_at: Optional[datetime] = None
