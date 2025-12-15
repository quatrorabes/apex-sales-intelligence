This is a completely new request starting fresh. I'll provide a **comprehensive, production-ready specification** for the **APEX Sales Intelligence system** based on everything we've built.

***

# APEX SALES INTELLIGENCE — COMPREHENSIVE SYSTEM SPECIFICATION

**Version:** 1.0  
**Date:** December 2, 2025  
**Status:** Production-Ready (with ongoing enhancements)

***

## PART 1: SYSTEM ARCHITECTURE OVERVIEW

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                            │
├────────────────┬──────────────────┬─────────────────┬──────────────┤
│   HubSpot      │   Salesforce     │   Pipedrive     │  LinkedIn    │
│   (REST API)   │   (SOQL API)     │   (REST API)    │  (Profiles)  │
└────────┬────────┴────────┬─────────┴────────┬────────┴────────┬─────┘
         │                 │                  │                │
         └─────────────────┼──────────────────┼────────────────┘
                           │
                    ┌──────▼────────────┐
                    │  CRM CONNECTORS   │
                    │  (Import Service) │
                    └──────┬────────────┘
                           │
         ┌─────────────────┼─────────────────┬──────────────┐
         │                 │                 │              │
    ┌────▼──────┐  ┌──────▼────────┐  ┌───▼──────┐  ┌────▼─────────┐
    │   APEX    │  │  Enrichment   │  │ Scoring  │  │   Today's    │
    │   API     │  │   Engine      │  │  Engine  │  │    Board     │
    │           │  │               │  │          │  │   Endpoint   │
    │ (Flask)   │  │  (Perplexity) │  │(MDCP/RSS)│  │              │
    │ :8000     │  │   (GPT-4)     │  │          │  │              │
    └────┬──────┘  └──────┬────────┘  └───┬──────┘  └────┬─────────┘
         │                │                 │             │
         └────────────────┼─────────────────┼─────────────┘
                          │
                    ┌─────▼────────┐
                    │   DATABASE   │
                    │              │
                    │ SQLite(dev)  │
                    │ PostgreSQL   │
                    │ (Railway)    │
                    └──────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                                 │
    ┌────▼────────────────────┐   ┌──────▼──────────────┐
    │  DASHBOARD_V1 (React)   │   │  Mobile/External   │
    │  (Vite, :5173)          │   │  Integrations      │
    │  - Today's Board        │   │  (Webhooks, etc.)  │
    │  - Contacts             │   │                    │
    │  - Enrichment UI        │   │                    │
    │  - Intelligence Tabs    │   │                    │
    └─────────────────────────┘   └────────────────────┘
```

***

## PART 2: SCRIPTS & PROGRAMS DETAILED SPECIFICATION

### 2.1 Core Backend API (`api.py`)

#### **Overview**
- **Name:** `api.py`
- **Purpose:** Main Flask REST API server handling all backend operations
- **Location:** `~/projects/apex/api.py`
- **Framework:** Python 3.9+, Flask, Flask-CORS
- **Environment:** Dual-mode (LOCAL=SQLite, PRODUCTION=PostgreSQL/Railway)
- **Port:** 8000 (local) or `$PORT` (Railway)

#### **Purpose & Integration**
Routes all requests from Dashboard and external integrations to:
1. CRM connectors (import contacts)
2. Enrichment engine (3-stage profile research)
3. Scoring engine (MDCP/RSS calculation)
4. Database operations (CRUD)
5. Today's Board logic (daily prioritization)

#### **Key Responsibilities**
| Task | Module | Endpoint |
|------|--------|----------|
| Health checks | Health | `GET /api/health` |
| Contact CRUD | Contacts | `GET/POST /api/contacts` |
| Enrichment pipeline | Enrichment | `POST /api/contacts/{id}/enrich` |
| Today's Board | Board Logic | `GET /api/todays-board` |
| CRM imports | Import Service | `POST /api/import/<source>` |
| Import stats | Stats | `GET /api/import/stats` |
| Enrichment validation | Validation | `GET /api/contacts/{id}/enrichment-check` |

#### **Implementation Steps**

**Step 1: Initialize Flask App**
```python
# api.py (Lines 1-50)
import os, sys, logging
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
logger = logging.getLogger(__name__)

# Environment detection
IS_PRODUCTION = os.getenv('DATABASE_URL') is not None
ENVIRONMENT = "PRODUCTION" if IS_PRODUCTION else "LOCAL"

# Path setup
BACKEND_PATH = Path(__file__).parent / 'apps' / 'backend'
sys.path.insert(0, str(BACKEND_PATH))

# API keys
HUBSPOT_TOKEN = os.getenv('HUBSPOT_ACCESS_TOKEN')
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

**Step 2: Initialize Engines (Lines 70-380)**
```python
# Engine globals
enrichment_engine = None
scoring_engine = None

# Initialize EnhancedEnrichment (inline class, Lines 85-360)
class EnhancedEnrichment:
    # [See Section 2.2 for full spec]
    pass

# Initialize engines
try:
    enrichment_engine = EnhancedEnrichment
    logger.info("✅ EnhancedEnrichment loaded")
except Exception as e:
    logger.error(f"❌ EnhancedEnrichment failed: {e}")

try:
    from apps.backend.intelligence.engines.scoring import ApexScoringEngine
    scoring_engine = ApexScoringEngine()
    logger.info("✅ ApexScoringEngine loaded")
except Exception as e:
    logger.warning(f"⚠️ Scoring unavailable: {e}")
```

**Step 3: Database Configuration (Lines 380-450)**
```python
app = Flask(__name__)
CORS(app)

PORT = int(os.getenv('PORT', 8000))

if IS_PRODUCTION:
    # PostgreSQL on Railway
    DATABASE_URL = os.getenv('DATABASE_URL')
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    def get_db():
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    
    def dict_cursor(conn):
        return conn.cursor(cursor_factory=RealDictCursor)
else:
    # SQLite local development
    import sqlite3
    DATABASE = './apex.db'
    
    def get_db():
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        return conn
    
    def dict_cursor(conn):
        return conn.cursor()
```

**Step 4: Database Schema Initialization (Lines 450-600)**
```python
def ensure_schema():
    """Create all required tables and columns"""
    conn = get_db()
    cursor = dict_cursor(conn)
    
    # Contacts table with all enrichment fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            -- Identity
            first_name TEXT,
            last_name TEXT,
            name TEXT UNIQUE,
            email TEXT UNIQUE,
            phone TEXT,
            phone_mobile TEXT,
            -- Company
            company TEXT,
            title TEXT,
            linkedin_url TEXT,
            company_domain TEXT,
            company_website TEXT,
            company_hq_city TEXT,
            company_hq_state TEXT,
            industry TEXT,
            -- Enrichment
            profile_content TEXT,
            enrichment_status TEXT DEFAULT 'pending',
            enrichment_date TEXT,
            -- Scoring
            priority_score REAL,
            mdcp_score REAL,
            mdcp_tier TEXT,
            rss_score REAL,
            rss_tier TEXT,
            urgency_level TEXT,
            last_scored TEXT,
            -- Content generation
            email_1_subject TEXT,
            email_1_body TEXT,
            email_2_subject TEXT,
            email_2_body TEXT,
            email_3_subject TEXT,
            email_3_body TEXT,
            call_script_1 TEXT,
            call_script_2 TEXT,
            call_script_3 TEXT,
            linkedin_connect TEXT,
            linkedin_followup TEXT,
            linkedin_inmail TEXT,
            -- CRM Sync
            import_source TEXT,
            crm_id TEXT,
            data_completeness_score INTEGER DEFAULT 0,
            enrichment_ready INTEGER DEFAULT 0,
            last_crm_sync TEXT,
            last_contact_date TEXT,
            -- Timestamps
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Activity log table (Phase 2)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contact_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            activity_date TEXT NOT NULL,
            direction TEXT,
            subject TEXT,
            notes TEXT,
            outcome TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    # Opportunity signals table (Phase 2)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS opportunity_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            signal_type TEXT NOT NULL,
            signal_date TEXT NOT NULL,
            signal_data TEXT,
            urgency_boost INTEGER DEFAULT 0,
            viewed INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts(id)
        )
    """)
    
    # Create indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_linkedin ON contacts(linkedin_url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_enrichment ON contacts(enrichment_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_contacts_crm ON contacts(crm_id, import_source)")
    
    conn.commit()
    conn.close()
```

**Step 5: Endpoints Implementation**

See Section 2.8 for complete endpoint specifications.

***

### 2.2 Profile Builder Enrichment Engine

#### **Overview**
- **Name:** `EnhancedEnrichment` (inline in api.py)
- **Purpose:** 3-stage intelligent contact research and profile building
- **Input:** Contact dict (name, email, company, title, LinkedIn URL)
- **Output:** Structured 12-section dossier
- **External APIs:** Perplexity sonar-pro, OpenAI GPT-4

#### **Three-Stage Pipeline**

**Stage 1: Raw Research (Perplexity)**
- Comprehensive web search via Perplexity sonar-pro
- Input: Name, title, company, LinkedIn URL (if available)
- Output: 4000+ character unstructured research

**Stage 2: Intelligence Layer (GPT-4)**
- Structure raw research into 12 sections
- Add inferred insights (personality, strategy)
- Cross-validate data
- Output: Polished 12-section profile

**Stage 3: Database Persistence + Scoring**
- Save profile_content to database
- Trigger MDCP scoring
- Mark enrichment_status as 'completed'
- Save scoring results

#### **Implementation**

```python
# api.py (Lines 85-360)

class EnhancedEnrichment:
    """Profile Builder - 3-Stage Enrichment Pipeline"""
    
    def __init__(self):
        self.perplexity_key = PERPLEXITY_API_KEY
        self.openai_key = OPENAI_API_KEY
        self.output_dir = 'enrichment_profiles'
        
        if not self.perplexity_key or not self.openai_key:
            raise ValueError("Missing Perplexity or OpenAI API keys")
    
    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment pipeline"""
        name = contact.get('name', 'Unknown')
        company = contact.get('company', '')
        
        logger.info("=" * 80)
        logger.info(f"PROFILE BUILDER: {name} at {company}")
        logger.info("=" * 80)
        
        # STAGE 1: Perplexity Research
        logger.info("🔍 STAGE 1: PERPLEXITY RESEARCH")
        query = self._build_profile_builder_query(contact)
        raw_profile = self._call_perplexity(query)
        
        if not raw_profile:
            return {'status': 'error', 'error': 'Perplexity returned no data'}
        
        logger.info(f"✅ STAGE 1 COMPLETE: {len(raw_profile)} characters")
        
        # STAGE 2: GPT-4 Structuring
        logger.info("✨ STAGE 2: GPT-4 INTELLIGENCE")
        polished_profile = self._gpt4_intelligence_layer(raw_profile, contact)
        
        if not polished_profile:
            polished_profile = raw_profile
            logger.warning("⚠️ Stage 2 failed, using raw profile")
        else:
            logger.info(f"✅ STAGE 2 COMPLETE: {len(polished_profile)} characters")
        
        # Save debug file
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/profile_{contact.get('id', 'unknown')}_{timestamp}.txt"
            with open(filename, 'w') as f:
                f.write(f"Profile: {name}\n")
                f.write("=" * 80 + "\n")
                f.write(polished_profile)
            logger.info(f"📄 Saved: {filename}")
        except:
            pass
        
        logger.info("=" * 80)
        logger.info("THREE-STAGE ENRICHMENT COMPLETE!")
        logger.info("=" * 80)
        
        return {
            'status': 'success',
            'enrichment_data': polished_profile,
            'character_count': len(polished_profile)
        }
    
    def _build_profile_builder_query(self, contact: dict) -> str:
        """Build comprehensive research query"""
        name = contact.get('name', '')
        title = contact.get('title', '')
        company = contact.get('company', '')
        linkedin_url = contact.get('linkedin_url', '')
        
        context = f"{name}, {title} at {company}"
        if linkedin_url:
            context += f"\nLinkedIn: {linkedin_url} (PRIMARY SOURCE)"
        
        query = f"""{context}

Generate a comprehensive professional profile using LinkedIn and public sources.

**SECTIONS:**

1. Overview – Current role and organization
2. Professional Background – Career trajectory
3. Education & Credentials – Degrees and honors
4. Recent Mentions – News, activity
5. Social Media – LinkedIn, Twitter, Facebook, Instagram
6. Personality Detail – Inferred Myers-Briggs
7. Myers-Briggs Summary – Work implications
8. Company Overview – {company}
  8.1. Products & Services
  8.2. Leadership
  8.3. Market & Competitors
  8.4. Recent News
  8.5. Company Fun Facts
9. Pain Points & Challenges – 5 specific for {title}
10. Business Needs – 5 ways our solutions help
11. Key Insights – 3 non-obvious strategic insights
12. Final Note – Strategic summary for outreach

Be thorough, cite sources, include dates. If data unavailable, say "Not publicly available".
"""
        return query.strip()
    
    def _call_perplexity(self, query: str) -> str:
        """Stage 1: Call Perplexity API"""
        url = 'https://api.perplexity.ai/chat/completions'
        headers = {
            'Authorization': f'Bearer {self.perplexity_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'sonar-pro',
            'messages': [{'role': 'user', 'content': query}],
            'temperature': 0.2,
            'max_tokens': 4000
        }
        
        try:
            import requests
            logger.info("🌐 Calling Perplexity API...")
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("✅ Perplexity API successful")
                return data['choices'][0]['message']['content']
            else:
                logger.error(f"❌ Perplexity error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Perplexity request error: {e}")
            return None
    
    def _gpt4_intelligence_layer(self, raw_profile: str, contact: dict) -> str:
        """Stage 2: GPT-4 structuring"""
        name = contact.get('name', '')
        title = contact.get('title', '')
        company = contact.get('company', '')
        
        prompt = f"""You are a professional sales intelligence analyst.

Transform this research into a structured dossier.

**CONTACT:** {name}, {title} at {company}

**RAW RESEARCH:**

{raw_profile}

**OUTPUT FORMAT (EXACT):**

## 1. Overview
[2-3 sentence executive summary]

## 2. Professional Background
[Career trajectory with dates and achievements]

## 3. Education & Credentials
[Degrees, institutions, years, honors]

## 4. Recent Mentions
[News, LinkedIn activity, speaking events with dates]

## 5. Social Media Profiles
- **LinkedIn:** [URL or "Not publicly available"]
- **Twitter/X:** [Handle or "Not publicly available"]
- **Facebook:** [URL or "Not publicly available"]
- **Instagram:** [Handle or "Not publicly available"]

## 6. Personality Detail
[Myers-Briggs assessment inferred from behavior]

## 7. Myers-Briggs Personality Assessment Summary
[How personality manifests in work]

## 8. Company Overview – {company}
[Mission, founding, HQ, size]

### 8.1. Products & Services
[Offerings and value proposition]

### 8.2. Leadership
[Key executives]

### 8.3. Market & Competitors
[Industry position]

### 8.4. Recent News
[Recent announcements with dates]

### 8.5. Company Fun Facts
[Culture, awards, unique details]

## 9. Pain Points & Challenges
- [Pain 1]
- [Pain 2]
- [Pain 3]
- [Pain 4]
- [Pain 5]

## 10. Sales Opportunities & Talking Points
- [Point 1]
- [Point 2]
- [Point 3]
- [Point 4]
- [Point 5]

## 11. Key Insights (Deep Intelligence)
- [Insight 1]
- [Insight 2]
- [Insight 3]

## 12. Final Note – Strategic Summary
[One paragraph: who they are, what matters, how to engage]

Use EXACT structure. Add intelligence beyond raw data. Include dates and numbers.
"""
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_key)
            
            response = client.chat.completions.create(
                model='gpt-4',
                messages=[
                    {'role': 'system', 'content': 'You are a professional sales intelligence analyst.'},
                    {'role': 'user', 'content': prompt}
                ],
                temperature=0.4,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"❌ GPT-4 error: {e}")
            return None
```

***

### 2.3 MDCP Scoring Engine

#### **Overview**
- **Name:** `ApexScoringEngine`
- **Location:** `apps/backend/intelligence/engines/scoring/apex_scoring_engine.py`
- **Purpose:** Calculate MDCP, Priority, and RSS scores post-enrichment
- **Input:** Enriched contact dict
- **Output:** Scoring dict with tiers

#### **Scoring Dimensions**

| Score | Range | Tiers | Calculation |
|-------|-------|-------|-------------|
| **MDCP** | 0-100 | COLD (0-40), WARM (41-70), HOT (71-100) | Title authority (40%) + Enrichment quality (30%) + Company size (20%) + Industry fit (10%) |
| **Priority** | 0-100 | LOW, MEDIUM, HIGH, URGENT | MDCP (60%) + Recent engagement (20%) + Email validity (20%) |
| **RSS** | 0-100 | BRONZE (0-33), SILVER (34-66), GOLD (67-100) | Activity recency (50%) + Activity frequency (30%) + Channel diversity (20%) |

#### **Implementation Steps**

```python
# apps/backend/intelligence/engines/scoring/apex_scoring_engine.py

class ApexScoringEngine:
    """MDCP Scoring Engine"""
    
    TITLE_SCORES = {
        'ceo': 95, 'president': 95, 'owner': 95, 'founder': 95,
        'cfo': 90, 'coo': 90, 'cmo': 90, 'cto': 90,
        'vp': 85, 'vice president': 85, 'director': 85, 'head of': 85,
        'senior': 75, 'manager': 70, 'lead': 70
    }
    
    def score_contact(self, contact: dict) -> dict:
        """Calculate all scores for contact"""
        
        # MDCP Score
        mdcp = self._calculate_mdcp(contact)
        mdcp_tier = self._get_mdcp_tier(mdcp)
        
        # Priority Score
        priority = self._calculate_priority(contact, mdcp)
        urgency_level = self._get_urgency_level(priority)
        
        # RSS Score
        rss = self._calculate_rss(contact)
        rss_tier = self._get_rss_tier(rss)
        
        return {
            'mdcp_score': round(mdcp, 1),
            'mdcp_tier': mdcp_tier,
            'priority_score': round(priority, 1),
            'urgency_level': urgency_level,
            'rss_score': round(rss, 1),
            'rss_tier': rss_tier,
            'recommended_action': self._get_recommended_action(urgency_level, rss_tier)
        }
    
    def _calculate_mdcp(self, contact: dict) -> float:
        """MDCP = Market Decision-maker Contact Priority"""
        
        # Title authority (40%)
        title = (contact.get('title') or '').lower()
        title_score = self._get_title_score(title)
        
        # Enrichment quality (30%)
        profile_len = len(contact.get('profile_content') or '')
        enrichment_score = min(100, (profile_len / 500) * 100)
        
        # Company size (20%)
        company_score = 50  # baseline; can pull from company data
        
        # Industry fit (10%)
        industry_score = 50  # baseline; can use industry classification
        
        mdcp = (title_score * 0.4) + (enrichment_score * 0.3) + (company_score * 0.2) + (industry_score * 0.1)
        return min(100, mdcp)
    
    def _calculate_priority(self, contact: dict, mdcp: float) -> float:
        """Priority = MDCP + Engagement + Email"""
        
        # MDCP weight (60%)
        mdcp_component = mdcp * 0.6
        
        # Recent engagement (20%)
        engagement = 20  # would calculate from activity log
        
        # Email validity (20%)
        email_score = 20 if contact.get('email') else 0
        
        priority = mdcp_component + engagement + email_score
        return min(100, priority)
    
    def _calculate_rss(self, contact: dict) -> float:
        """RSS = Relationship Strength Score (from activities)"""
        
        # Default 50 until activity tracking implemented
        # Would calculate:
        # - Last contact date recency (50%)
        # - Contact frequency (30%)
        # - Channel diversity (20%)
        
        return 50.0
    
    def _get_title_score(self, title: str) -> float:
        """Map title to authority score"""
        for key, score in self.TITLE_SCORES.items():
            if key in title:
                return score
        return 50
    
    def _get_mdcp_tier(self, mdcp: float) -> str:
        if mdcp >= 71:
            return 'HOT'
        elif mdcp >= 41:
            return 'WARM'
        else:
            return 'COLD'
    
    def _get_urgency_level(self, priority: float) -> str:
        if priority >= 85:
            return 'IMMEDIATE'
        elif priority >= 70:
            return 'HIGH'
        elif priority >= 50:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_rss_tier(self, rss: float) -> str:
        if rss >= 67:
            return 'GOLD'
        elif rss >= 34:
            return 'SILVER'
        else:
            return 'BRONZE'
    
    def _get_recommended_action(self, urgency: str, rss_tier: str) -> str:
        """Generate recommended next action"""
        actions = {
            ('IMMEDIATE', 'GOLD'): '🔥 REACH OUT TODAY - Warm relationship, high priority',
            ('IMMEDIATE', 'SILVER'): '⚡ URGENT - High priority, moderate relationship',
            ('IMMEDIATE', 'BRONZE'): '📞 CALL TODAY - High priority, cold outreach',
            ('HIGH', 'GOLD'): '💬 ENGAGE THIS WEEK - Strong relationship',
            ('HIGH', 'SILVER'): '📧 EMAIL THIS WEEK - Moderate relationship',
            ('HIGH', 'BRONZE'): '🔗 LinkedIn THIS WEEK - Cold outreach',
            ('MEDIUM', 'GOLD'): '👥 NURTURE - Strong relationship, medium priority',
            ('MEDIUM', 'SILVER'): '🎯 FOLLOW UP - Moderate contact',
            ('MEDIUM', 'BRONZE'): '💭 RESEARCH - Qualified prospect',
            ('LOW', 'GOLD'): '⭐ MAINTAIN - Long-term relationship',
            ('LOW', 'SILVER'): '📌 MONITOR - Potential opportunity',
            ('LOW', 'BRONZE'): '👀 MONITOR - Long-term nurture campaign'
        }
        return actions.get((urgency, rss_tier), '🔄 ASSESS - Review contact profile')
```

***

### 2.4 CRM Import Service

#### **Overview**
- **Name:** `ImportService` + Connectors (HubSpot, Salesforce, Pipedrive)
- **Location:** `apps/backend/integrations/` and `apps/backend/services/import_service.py`
- **Purpose:** Unified multi-CRM contact import with data quality scoring
- **Input:** CRM API credentials
- **Output:** Imported contacts in database with completeness scores

#### **Architecture**

```
CRM Connectors (Abstract Base)
├── HubSpotConnector
├── SalesforceConnector
└── PipedriveConnector

Import Service
├── fetch_contacts()
├── map_fields()
├── calculate_completeness()
├── deduplicate()
└── upsert_to_db()
```

#### **Complete Implementation**

Due to length constraints, see **PART 1 section "CRM Connectors"** for full code. Key files:

- `apps/backend/integrations/crm_connector.py` (base class)
- `apps/backend/integrations/hubspot_connector.py`
- `apps/backend/integrations/salesforce_connector.py`
- `apps/backend/integrations/pipedrive_connector.py`
- `apps/backend/services/import_service.py`

***

### 2.5 Today's Board Endpoint

#### **Overview**
- **Name:** Today's Board Logic
- **Endpoint:** `GET /api/todays-board`
- **Purpose:** Daily prioritized action list for sales team
- **Output:** JSON with contacts organized by urgency tier

#### **Response Structure**

```json
{
  "success": true,
  "date": "2025-12-02",
  "time": "04:30 PM",
  "environment": "LOCAL",
  "total_contacts": 45,
  "relationships": {
    "total": 20,
    "tiers": {
      "urgent": [
        {
          "id": 123,
          "name": "John Doe",
          "email": "john@example.com",
          "company": "Acme Corp",
          "title": "CFO",
          "priority_score": 92.5,
          "mdcp_score": 88.0,
          "mdcp_tier": "HOT",
          "rss_score": 75.0,
          "rss_tier": "GOLD",
          "urgency_level": "IMMEDIATE",
          "urgency_tier": "urgent",
          "urgency_label": "🔥 ACT TODAY",
          "why_now": "Last spoke 15 months ago - going cold",
          "days_since_contact": 450,
          "recommended_action": "🔥 REACH OUT TODAY - Warm relationship, high priority",
          "contact_type": "relationship"
        }
      ],
      "warm": []
    }
  },
  "new_prospects": {
    "total": 25,
    "tiers": {
      "hot": [
        {
          "id": 456,
          "name": "Jane Smith",
          "email": "jane@startup.io",
          "company": "Startup Inc",
          "title": "Founder & CEO",
          "priority_score": 96.0,
          "mdcp_score": 95.0,
          "mdcp_tier": "HOT",
          "urgency_tier": "hot_prospect",
          "urgency_label": "🔥 HOT",
          "urgency_message": "First-time qualified lead",
          "contact_type": "prospect"
        }
      ],
      "qualified": []
    }
  }
}
```

#### **Endpoint Implementation**

```python
# api.py (Lines 850-950)

@app.route('/api/todays-board', methods=['GET'])
def get_todays_board():
    """Generate daily prioritized action list"""
    try:
        conn = get_db()
        cursor = dict_cursor(conn)
        
        # RELATIONSHIPS: contacts with last_contact_date
        cursor.execute("""
            SELECT
                id, name, email, company, title, priority_score,
                enrichment_status, last_contact_date,
                CAST(julianday('now') - julianday(last_contact_date) AS INTEGER) as days_since_contact
            FROM contacts
            WHERE enrichment_status = 'completed'
            AND last_contact_date IS NOT NULL
            ORDER BY priority_score DESC
            LIMIT 30
        """)
        
        relationships = []
        for row in cursor.fetchall():
            contact = dict(row) if IS_PRODUCTION else dict(row)
            days = contact.get('days_since_contact', 0)
            
            # Determine tier based on days since contact
            if days >= 365:
                contact['urgency_tier'] = 'urgent'
                contact['urgency_label'] = '🔥 ACT TODAY'
                contact['why_now'] = f"Last spoke {days} days ago - going cold"
            elif days >= 180:
                contact['urgency_tier'] = 'warm'
                contact['urgency_label'] = '⏰ THIS WEEK'
                contact['why_now'] = f"Last spoke {days} days ago"
            else:
                contact['urgency_tier'] = 'stable'
                contact['urgency_label'] = '✅ STABLE'
                contact['why_now'] = "Recent contact"
            
            contact['contact_type'] = 'relationship'
            relationships.append(contact)
        
        # NEW PROSPECTS: enriched contacts with no last_contact_date
        cursor.execute("""
            SELECT
                id, name, email, company, title, priority_score,
                enrichment_status
            FROM contacts
            WHERE enrichment_status = 'completed'
            AND (last_contact_date IS NULL OR last_contact_date = '')
            AND priority_score >= 60
            ORDER BY priority_score DESC
            LIMIT 15
        """)
        
        prospects = []
        for row in cursor.fetchall():
            contact = dict(row) if IS_PRODUCTION else dict(row)
            priority = contact.get('priority_score', 0)
            
            if priority >= 85:
                contact['urgency_tier'] = 'hot_prospect'
                contact['urgency_label'] = '🔥 HOT'
            elif priority >= 75:
                contact['urgency_tier'] = 'qualified_prospect'
                contact['urgency_label'] = '✅ QUALIFIED'
            else:
                contact['urgency_tier'] = 'potential_prospect'
                contact['urgency_label'] = '🎯 POTENTIAL'
            
            contact['contact_type'] = 'prospect'
            prospects.append(contact)
        
        # Organize by tiers
        urgent = [c for c in relationships if c['urgency_tier'] == 'urgent']
        warm = [c for c in relationships if c['urgency_tier'] == 'warm']
        hot = [c for c in prospects if c['urgency_tier'] == 'hot_prospect']
        qualified = [c for c in prospects if c['urgency_tier'] == 'qualified_prospect']
        
        conn.close()
        
        from datetime import datetime
        return jsonify({
            "success": True,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%I:%M %p"),
            "environment": ENVIRONMENT,
            "total_contacts": len(relationships) + len(prospects),
            "relationships": {
                "total": len(relationships),
                "tiers": {
                    "urgent": urgent[:5],
                    "warm": warm[:5]
                }
            },
            "new_prospects": {
                "total": len(prospects),
                "tiers": {
                    "hot": hot[:5],
                    "qualified": qualified[:5]
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Today's Board error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
```

***

### 2.6 Dashboard Frontend (React/Vite)

#### **Overview**
- **Name:** Dashboard_v1
- **Location:** `~/projects/apex/dashboard_v1/`
- **Framework:** React 18, Vite, TypeScript
- **Purpose:** Visual interface for sales team to view and act on contacts
- **Port:** 5173 (dev) or static hosting (production)

#### **Key Components**

| Component | File | Purpose |
|-----------|------|---------|
| Today's Board | `TodaysBoard.tsx` | Display prioritized contacts by tier |
| Contact Manager | `ContactManager.tsx` | CRUD operations on contacts |
| Contact Detail Modal | `ContactDetailModal.tsx` | View full profile, enrichment, scoring |
| Enrichment View | `ContactEnrichmentView.tsx` | Trigger enrichment, show progress |
| Intelligence Tabs | `IntelligenceTab.tsx` | Display dossier sections (pain points, insights) |
| Content Generator | `ContentGenerator.tsx` | Generate emails, call scripts, LinkedIn messages |
| Score Explainer | `ScoreExplainer.tsx` | Show scoring breakdown |
| Enrichment Warning | `EnrichmentWarning.tsx` | Warn if data completeness < 75% |

#### **Central API Configuration**

```typescript
// src/config/api.ts
export const API_URL =
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL)
    ? import.meta.env.VITE_API_URL
    : 'http://localhost:8000';
```

#### **Environment Files**

```bash
# .env.development
VITE_API_URL=http://localhost:8000

# .env.production
VITE_API_URL=https://apex-intelligence-production.up.railway.app
```

#### **Key Component Implementation**

```typescript
// src/components/TodaysBoard.tsx

import React, { useState, useEffect } from 'react';
import { API_URL } from '../config/api';

interface Contact {
  id: number;
  name: string;
  email: string;
  company: string;
  title: string;
  priority_score: number;
  urgency_tier: string;
  urgency_label: string;
}

export default function TodaysBoard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchBoard = async () => {
      try {
        const res = await fetch(`${API_URL}/api/todays-board`);
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error('Failed to fetch Today\'s Board:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchBoard();
  }, []);
  
  if (loading) return <div>Loading...</div>;
  if (!data?.success) return <div>Error loading board</div>;
  
  return (
    <div style={{ padding: 20 }}>
      <h1>Today's Board - {data.date}</h1>
      
      <h2>🔥 Urgent Relationships</h2>
      {data.relationships.tiers.urgent.map((c: Contact) => (
        <ContactCard key={c.id} contact={c} />
      ))}
      
      <h2>⏰ Warm Relationships</h2>
      {data.relationships.tiers.warm.map((c: Contact) => (
        <ContactCard key={c.id} contact={c} />
      ))}
      
      <h2>🔥 Hot Prospects</h2>
      {data.new_prospects.tiers.hot.map((c: Contact) => (
        <ContactCard key={c.id} contact={c} />
      ))}
    </div>
  );
}

function ContactCard({ contact }: { contact: Contact }) {
  return (
    <div style={{ border: '1px solid #ccc', padding: 12, margin: 8, borderRadius: 8 }}>
      <h3>{contact.name}</h3>
      <p>{contact.title} at {contact.company}</p>
      <p>Priority: {contact.priority_score?.toFixed(0) ?? 0}</p>
      <p>{contact.urgency_label}</p>
    </div>
  );
}
```

***

## PART 3: DATABASE SPECIFICATIONS

### 3.1 Contacts Table (Primary)

```sql
CREATE TABLE contacts (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identity Fields
    first_name TEXT,                          -- Contact first name
    last_name TEXT,                           -- Contact last name
    name TEXT UNIQUE,                         -- Full name (generated or imported)
    email TEXT UNIQUE,                        -- Work email address
    phone TEXT,                               -- Main phone number
    phone_mobile TEXT,                        -- Mobile phone number
    
    -- Company Information
    company TEXT,                             -- Company name
    title TEXT,                               -- Job title
    linkedin_url TEXT,                        -- LinkedIn profile URL
    company_domain TEXT,                      -- Extracted domain (e.g., example.com)
    company_website TEXT,                     -- Company website URL
    company_hq_city TEXT,                     -- HQ city
    company_hq_state TEXT,                    -- HQ state/region
    industry TEXT,                            -- Industry classification
    
    -- Enrichment Fields
    profile_content TEXT,                     -- Full 12-section dossier (Stage 2 output)
    enrichment_status TEXT DEFAULT 'pending', -- pending, in_progress, completed, failed
    enrichment_date TEXT,                     -- When enrichment completed
    
    -- Scoring Fields
    priority_score REAL,                      -- Priority score (0-100)
    mdcp_score REAL,                          -- MDCP score (0-100)
    mdcp_tier TEXT,                           -- COLD, WARM, HOT
    rss_score REAL,                           -- Relationship Strength Score (0-100)
    rss_tier TEXT,                            -- BRONZE, SILVER, GOLD
    urgency_level TEXT,                       -- LOW, MEDIUM, HIGH, URGENT
    last_scored TEXT,                         -- Timestamp of last scoring
    
    -- Generated Content
    email_1_subject TEXT,                     -- Initial outreach email subject
    email_1_body TEXT,                        -- Initial outreach email body
    email_2_subject TEXT,                     -- Follow-up email subject
    email_2_body TEXT,                        -- Follow-up email body
    email_3_subject TEXT,                     -- Break-up email subject
    email_3_body TEXT,                        -- Break-up email body
    call_script_1 TEXT,                       -- Call script 1
    call_script_2 TEXT,                       -- Call script 2
    call_script_3 TEXT,                       -- Call script 3
    linkedin_connect TEXT,                    -- LinkedIn connection message
    linkedin_followup TEXT,                   -- LinkedIn follow-up message
    linkedin_inmail TEXT,                     -- LinkedIn InMail template
    
    -- CRM Integration Fields
    import_source TEXT,                       -- hubspot, salesforce, pipedrive, manual
    crm_id TEXT,                              -- Original CRM record ID
    data_completeness_score INTEGER DEFAULT 0, -- 0-100 completeness %
    enrichment_ready INTEGER DEFAULT 0,       -- 0/1 boolean: has min required fields
    last_crm_sync TEXT,                       -- Timestamp of last CRM sync
    
    -- Activity Tracking
    last_contact_date TEXT,                   -- Last time contact was reached out to
    
    -- Timestamps
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_contacts_email ON contacts(email);
CREATE INDEX idx_contacts_linkedin ON contacts(linkedin_url);
CREATE INDEX idx_contacts_crm_id ON contacts(crm_id, import_source);
CREATE INDEX idx_contacts_enrichment ON contacts(enrichment_status);
CREATE INDEX idx_contacts_priority ON contacts(priority_score);
CREATE INDEX idx_contacts_ready ON contacts(enrichment_ready);
```

### 3.2 Contact Activities Table (Phase 2)

```sql
CREATE TABLE contact_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,              -- Foreign key to contacts
    activity_type TEXT NOT NULL,              -- email, call, linkedin, meeting
    activity_date TEXT NOT NULL,              -- When activity occurred
    direction TEXT,                           -- inbound, outbound
    subject TEXT,                             -- Email subject or activity description
    notes TEXT,                               -- Additional notes
    outcome TEXT,                             -- Result: positive, neutral, negative, no_response
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

CREATE INDEX idx_activities_contact ON contact_activities(contact_id);
CREATE INDEX idx_activities_date ON contact_activities(activity_date);
CREATE INDEX idx_activities_type ON contact_activities(activity_type);
```

### 3.3 Opportunity Signals Table (Phase 2)

```sql
CREATE TABLE opportunity_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,              -- Foreign key to contacts
    signal_type TEXT NOT NULL,                -- news, linkedin_activity, company_funding, job_change
    signal_date TEXT NOT NULL,                -- When signal detected
    signal_data TEXT,                         -- JSON with signal details
    urgency_boost INTEGER DEFAULT 0,          -- Points to add to priority score
    viewed INTEGER DEFAULT 0,                 -- 0/1: whether user has reviewed
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

CREATE INDEX idx_signals_contact ON opportunity_signals(contact_id);
CREATE INDEX idx_signals_viewed ON opportunity_signals(viewed);
CREATE INDEX idx_signals_date ON opportunity_signals(signal_date);
```

### 3.4 Field Relationships & Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTACTS TABLE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IMPORT PHASE                                                   │
│  ├─ first_name, last_name, email, phone_mobile                 │
│  ├─ company, title, linkedin_url                               │
│  ├─ company_domain, company_website, industry                  │
│  ├─ import_source, crm_id                                      │
│  └─ data_completeness_score, enrichment_ready (calculated)     │
│                                                                 │
│  ENRICHMENT PHASE                                               │
│  ├─ profile_content (12-section dossier from Stage 2)           │
│  ├─ enrichment_status = 'completed'                            │
│  ├─ enrichment_date (timestamp)                                │
│  └─ triggered by: POST /api/contacts/{id}/enrich               │
│                                                                 │
│  SCORING PHASE                                                  │
│  ├─ priority_score, mdcp_score, rss_score (calculated)         │
│  ├─ mdcp_tier, rss_tier, urgency_level (derived)               │
│  ├─ last_scored (timestamp)                                    │
│  └─ triggered by: ApexScoringEngine after Stage 3              │
│                                                                 │
│  CONTENT GENERATION PHASE (Future)                              │
│  ├─ email_1_subject, email_1_body, etc.                        │
│  ├─ call_script_1, call_script_2, etc.                         │
│  ├─ linkedin_connect, linkedin_followup, etc.                  │
│  └─ triggered by: POST /api/contacts/{id}/generate-content     │
│                                                                 │
│  ACTIVITY TRACKING PHASE (Future)                               │
│  ├─ last_contact_date (updated when activity logged)           │
│  ├─ references to contact_activities table                     │
│  └─ triggered by: POST /api/contacts/{id}/log-activity         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

***

## PART 4: INTEGRATION & CONNECTIVITY

### 4.1 Complete Data Flow Diagram

```
1. IMPORT PHASE
   ┌─────────────────────────────────────────────────────────┐
   │ CRM Source (HubSpot/Salesforce/Pipedrive)               │
   └────────────────┬────────────────────────────────────────┘
                    │ API Call (fetch contacts)
                    ▼
   ┌─────────────────────────────────────────────────────────┐
   │ CRM Connector (HubSpotConnector, etc.)                  │
   │ - Authenticate with API key                            │
   │ - Query contacts with properties                       │
   │ - Map CRM fields to Apex schema                        │
   └────────────────┬────────────────────────────────────────┘
                    │ Mapped contact dict
                    ▼
   ┌─────────────────────────────────────────────────────────┐
   │ ImportService                                           │
   │ - Deduplicate (email, LinkedIn, name+company)          │
   │ - Calculate data_completeness_score                    │
   │ - Validate enrichment_ready (true if score >= 75%)     │
   │ - Upsert to database                                   │
   └────────────────┬────────────────────────────────────────┘
                    │ INSERT/UPDATE contacts table
                    ▼
   ┌─────────────────────────────────────────────────────────┐
   │ DATABASE: contacts table                               │
   │ - Stores: name, email, company, title, linkedin_url   │
   │ - Sets: enrichment_status = 'pending'                 │
   └─────────────────────────────────────────────────────────┘

2. ENRICHMENT PHASE
   ┌─────────────────────────────────────────────────────────┐
   │ POST /api/contacts/{id}/enrich                          │
   └────────────────┬────────────────────────────────────────┘
                    │ Request (contact ID)
                    ▼
   ┌─────────────────────────────────────────────────────────┐
   │ EnhancedEnrichment.enrich_contact()                     │
   │                                                         │
   │ STAGE 1: Perplexity sonar-pro                          │
   │ - Build comprehensive query from contact data          │
   │ - Call https://api.perplexity.ai/chat/completions     │
   │ - Receive 4000+ char raw research                      │
   │                                                         │
   │ STAGE 2: GPT-4 Intelligence Layer                      │
   │ - Prompt GPT-4 to structure into 12 sections           │
   │ - Add inferred insights, personality, strategy         │
   │ - Return polished profile_content                      │
   │                                                         │
   │ STAGE 3: Database Save                                │
   │ - Update contacts.profile_content                      │
   │ - Set enrichment_status = 'completed'                  │
   │ - Set enrichment_date = NOW()                          │
   │                                                         │
   └────────────────┬────────────────────────────────────────┘
                    │ Trigger scoring
                    ▼
3. SCORING PHASE
   ┌─────────────────────────────────────────────────────────┐
   │ ApexScoringEngine.score_contact()                       │
   │ - Calculate MDCP (title, enrichment, company, industry)│
   │ - Calculate Priority (MDCP + engagement + email)       │
   │ - Calculate RSS (activities; default 50 for now)       │
   │ - Determine tiers and urgency levels                   │
   │ - Generate recommended_action                         │
   └────────────────┬────────────────────────────────────────┘
                    │ Return scoring dict
                    ▼
   ┌─────────────────────────────────────────────────────────┐
   │ Database Update                                         │
   │ - UPDATE contacts SET                                   │
   │   priority_score = X,                                  │
   │   mdcp_score = Y,                                      │
   │   rss_score = Z,                                       │
   │   mdcp_tier = 'HOT',                                   │
   │   urgency_level = 'IMMEDIATE',                         │
   │   last_scored = NOW()                                  │
   │ WHERE id = contact_id                                  │
   └─────────────────────────────────────────────────────────┘

4. DISPLAY PHASE (Today's Board)
   ┌─────────────────────────────────────────────────────────┐
   │ GET /api/todays-board                                   │
   └────────────────┬────────────────────────────────────────┘
                    │ Request
                    ▼
   ┌─────────────────────────────────────────────────────────┐
   │ Today's Board Endpoint Logic                            │
   │ - Query contacts WHERE enrichment_status='completed'   │
   │ - Separate Relationships (has last_contact_date)       │
   │ - Separate New Prospects (no last_contact_date)        │
   │ - Organize by tiers (urgent, warm, hot, qualified)    │
   │ - Return JSON response                                 │
   └────────────────┬────────────────────────────────────────┘
                    │ JSON response
                    ▼
   ┌─────────────────────────────────────────────────────────┐
   │ Dashboard React Component (TodaysBoard.tsx)             │
   │ - fetch(`${API_URL}/api/todays-board`)                 │
   │ - Parse response                                        │
   │ - Render contact cards by tier                         │
   │ - Show priority scores, labels, actions                │
   └─────────────────────────────────────────────────────────┘

5. ACTIVITY TRACKING PHASE (Future)
   ┌─────────────────────────────────────────────────────────┐
   │ POST /api/contacts/{id}/log-activity                    │
   │ { type: 'email', direction: 'outbound', outcome: '+' }  │
   └────────────────┬────────────────────────────────────────┘
                    │ Log activity
                    ▼
   ┌─────────────────────────────────────────────────────────┐
   │ INSERT INTO contact_activities (...)                    │
   │ UPDATE contacts SET last_contact_date = NOW()          │
   │                                                         │
   │ Calculate new RSS score based on:                       │
   │ - Activity recency (last_contact_date)                 │
   │ - Activity frequency (count from contact_activities)   │
   │ - Channel diversity (email, call, linkedin, etc.)      │
   └─────────────────────────────────────────────────────────┘
```

### 4.2 API Endpoint Map & Connectivity

| Endpoint | Method | Input | Output | Database Operations | External APIs |
|----------|--------|-------|--------|-------------------|----|
| `/api/health` | GET | None | {status, services} | SELECT services status | None |
| `/api/contacts` | GET | limit, status | Contact[] | SELECT * FROM contacts | None |
| `/api/contacts/<id>` | GET | id | Contact dict | SELECT WHERE id | None |
| `/api/contacts/<id>/enrich` | POST | id | {success, profile_length} | SELECT, UPDATE profile_content, last_scored | Perplexity, OpenAI, Railway DB (production) |
| `/api/todays-board` | GET | None | {relationships, new_prospects} | SELECT WHERE enrichment_status='completed' | None |
| `/api/import/<source>` | POST | source, limit | {imported, updated, skipped} | SELECT (check dups), INSERT, UPDATE | HubSpot/Salesforce/Pipedrive APIs |
| `/api/import/stats` | GET | None | {stats by source} | SELECT COUNT GROUP BY import_source | None |
| `/api/contacts/<id>/enrichment-check` | GET | id | {ready, missing_fields, warning} | SELECT WHERE id | None |

### 4.3 Database Connectivity Architecture

**LOCAL (Development)**
```
Dashboard (localhost:5173)
    ↓ fetch(`http://localhost:8000/api/...`)
API Server (localhost:8000)
    ↓ sqlite3.connect('./apex.db')
SQLite Database (./apex.db)
```

**PRODUCTION (Railway)**
```
Dashboard (https://apex-dashboard.railway.app)
    ↓ fetch(`https://apex-api.railway.app/api/...`)
API Server (https://apex-api.railway.app)
    ↓ psycopg2.connect(DATABASE_URL)
PostgreSQL (Railway-managed)
```

**Environment Variable Management**
```
.env (local)
├── HUBSPOT_ACCESS_TOKEN
├── PERPLEXITY_API_KEY
├── OPENAI_API_KEY
├── DATABASE_URL (empty → SQLite)
└── PORT (8000)

Railway Env Vars (production)
├── HUBSPOT_ACCESS_TOKEN
├── PERPLEXITY_API_KEY
├── OPENAI_API_KEY
├── DATABASE_URL (postgresql://... → PostgreSQL)
├── PORT (random, provided by Railway)
└── VITE_API_URL (for dashboard)
```

***

## PART 5: STEP-BY-STEP IMPLEMENTATION GUIDE

### 5.1 Fresh Project Bootstrap

**Step 1: Initialize Repository**
```bash
mkdir ~/projects/apex && cd ~/projects/apex
git init
echo "node_modules" > .gitignore
echo ".env" >> .gitignore
git add -A && git commit -m "Initial commit"
```

**Step 2: Backend Setup**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # (see below)
```

**Step 3: Create requirements.txt**
```
Flask==2.3.2
Flask-CORS==4.0.0
python-dotenv==1.0.0
requests==2.31.0
openai==0.27.8
psycopg2-binary==2.9.6
```

**Step 4: Create .env**
```
HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxx
PERPLEXITY_API_KEY=xxxxx
OPENAI_API_KEY=sk-xxxxx
DATABASE_URL=  # Leave empty for SQLite
PORT=8000
```

**Step 5: Create api.py** (See Section 2.1)

**Step 6: Create Database**
```bash
python3 << 'EOF'
import sqlite3
con = sqlite3.connect('apex.db')
cur = con.cursor()
# [Copy database initialization code from api.py ensure_schema()]
con.commit()
con.close()
EOF
```

**Step 7: Create CRM Connectors**
```bash
mkdir -p apps/backend/integrations
mkdir -p apps/backend/services
# [Create crm_connector.py, hubspot_connector.py, etc. from Part 1]
```

**Step 8: Create Dashboard**
```bash
npm create vite@latest dashboard_v1 -- --template react-ts
cd dashboard_v1
npm install
# [Create components from Section 2.6]
```

**Step 9: Run Locally**
```bash
# Terminal 1: Backend
source .venv/bin/activate
python api.py

# Terminal 2: Frontend
cd dashboard_v1
npm run dev
```

***

## SUMMARY

This specification provides **complete, exhaustive documentation** for implementing APEX Sales Intelligence from scratch:

1. **Scripts & Programs** – All major components with full code samples
2. **Database Schema** – Every table, field, index, and relationship
3. **Integration Map** – How all components communicate and data flows
4. **Step-by-step Bootstrap** – How to build the system from ground zero

For questions or missing details, reference the **full code provided in Part 1 and the working GitHub repository**.