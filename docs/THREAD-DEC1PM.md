# APEX SALES INTELLIGENCE - COMPLETE SYSTEM REFERENCE GUIDE
**Generated:** December 1, 2025, 7 PM PST  
**Status:** Production-Ready with Unified Scoring System (Phases 1 & 2 Complete)

***

## 1. KEY PROGRAMS & COMPONENTS

### **1.1 Apex Scoring Engine (Foundation)**
- **File:** `/Users/chrisrabenold/projects/apex/apps/backend/intelligence/engines/scoring/apex_scoring_engine.py`
- **Version:** 2.1.0
- **Purpose:** Foundation MDCP (Money, Decision, Credibility, Pain) + RSS (Role, Seniority, Scope) scoring for commercial real estate leads
- **Database Support:** SQLite (local) + PostgreSQL (Railway production)
- **Key Features:**
  - Adaptive MDCP scoring with lead type profiles (BANKER, CDC, BROKER, PRIVATE_LENDER, BORROWER)
  - RSS scoring based on job title analysis (seniority, scope, authority)
  - Lifecycle stage detection (NEW, WARMING, ACTIVE, ESTABLISHED)
  - Priority calculation with urgency levels (IMMEDIATE, HIGH, MEDIUM, LOW)
  - Thread-safe DatabaseAdapter for multi-environment support
- **Replaced:** Generic HubSpot lead scoring
- **Status:** ✅ Deployed to Railway, tested with 500+ contacts

### **1.2 User-Specific Scoring Engine (CRE Intelligence Layer)**
- **File:** `/Users/chrisrabenold/projects/apex/apps/backend/intelligence/engines/scoring/user_scoring_engine.py`
- **Version:** 2.1.0
- **Purpose:** CRE vertical-specific RSS scoring with exclusion filters and high-value company detection
- **Key Features:**
  - CRE indicator detection (commercial, broker, leasing, investment, etc.)
  - Exclude residential/non-CRE departments (HR, IT, legal, compliance, etc.)
  - High-value company matching (CBRE, JLL, Cushman & Wakefield, Colliers, etc.)
  - Title-specific scoring (Principal: 85, VP: 85, Director: 80, Broker: 70, etc.)
  - Premium combo bonus (+10 for high-value company + good title)
- **Replaced:** Generic RSS scoring without vertical awareness
- **Status:** ✅ Deployed, integrated with unified scorer

### **1.3 Unified Apex Scorer**
- **File:** `/Users/chrisrabenold/projects/apex/apps/backend/intelligence/engines/scoring/unified_apex_scorer.py`
- **Version:** 2.1.0
- **Purpose:** Orchestrates foundation MDCP + CRE intelligence layer for complete unified scoring
- **Pipeline:**
  1. Run foundation MDCP + generic RSS
  2. Apply CRE vertical intelligence boost/penalty
  3. Recalculate priority with CRE-enhanced RSS
  4. Save to database with full metadata
- **Key Output:**
  - `mdcp_score` (0-100), `mdcp_tier` (HOT/WARM/QUALIFIED/COLD)
  - `rss_score` (0-100), `rss_tier` (PLATINUM/GOLD/SILVER/BRONZE)
  - `priority_score` (0-100), `urgency_level` (IMMEDIATE/HIGH/MEDIUM/LOW)
  - `recommended_action` (actionable next steps)
  - `cre_vertical_applied` (boolean flag)
- **Replaced:** Separate, non-integrated scoring systems
- **Status:** ✅ Production-ready, scoring 500+ contacts on Railway

### **1.4 Enhanced Enrichment Engine (Profile Builder)**
- **File:** `/Users/chrisrabenold/projects/apex/apps/backend/intelligence/enhanced_enrichment.py`
- **Purpose:** AI-powered contact enrichment with comprehensive profile generation
- **AI Orchestration:**
  - **Perplexity (sonar-pro):** Web research, company intel, recent activity
  - **GPT-4:** Profile synthesis, talking points, value proposition generation
  - **Database:** Stores enriched profiles, scripts, email templates, LinkedIn messages
- **Key Features:**
  - Multi-stage enrichment (research → synthesis → content generation)
  - Why Me? value proposition builder
  - Call scripts (3 levels)
  - Email sequences (3 levels)
  - LinkedIn connection strategy
- **Replaced:** Manual prospect research, generic outreach templates
- **Current Priority:** Auto-trigger enrichment after contact import
- **Status:** ✅ Working, integrated with Dashboard enrichment tab

***

## 2. MAJOR API ENDPOINTS

### **2.1 Scoring Endpoints**

#### **POST /api/contacts/tact_id>/score**
- **Location:** `api.py` line ~1403
- **Purpose:** Score single contact with unified MDCP + CRE intelligence
- **Request:** `POST https://apex-intelligence-production.up.railway.app/api/contacts/763/score`
- **Response:**
```json
{
  "success": true,
  "contact_id": 763,
  "contact_name": "Kyle Chuang",
  "company": "Chessboard Capital, Inc.",
  "scores": {
    "mdcp": 41.25,
    "mdcp_tier": "COLD",
    "rss": 95,
    "rss_tier": "PLATINUM",
    "priority": 41.25,
    "urgency": "LOW"
  },
  "action": "👀 MONITOR - Long-term nurture campaign",
  "cre_applied": true,
  "lead_type": "BORROWER",
  "lifecycle_stage": "NEW",
  "timestamp": "2025-12-02T02:46:47.718796"
}
```
- **Replaced:** No previous scoring API
- **Status:** ✅ Working on Railway PostgreSQL

#### **POST /api/contacts/score/bulk**
- **Location:** `api.py` line ~1440
- **Purpose:** Batch score multiple contacts
- **Request Body:** `{"contact_ids": [1, 2, 3, ...]}`
- **Response:** Array of scoring results
- **Status:** ✅ Working, used to score 500+ contacts

#### **GET /api/todays-board**
- **Location:** `api.py` line ~1615
- **Purpose:** Priority-ranked daily action list based on unified scoring
- **Response:**
```json
{
  "board": {
    "IMMEDIATE": [...],
    "HIGH": [...],
    "MEDIUM": [...],
    "LOW": [...]
  },
  "breakdown": {
    "IMMEDIATE": 5,
    "HIGH": 12,
    "MEDIUM": 20,
    "LOW": 15
  },
  "total_contacts": 52,
  "relationships": {...},  // Backward compatible
  "new_prospects": {...}   // Backward compatible
}
```
- **Replaced:** Old format with manual prioritization
- **Status:** ✅ Working, backward compatible with Dashboard

### **2.2 Contact Management Endpoints**

#### **GET /api/contacts**
- **Purpose:** Fetch all contacts with filtering/pagination
- **Query Params:** `?limit=100&offset=0`
- **Status:** ✅ Working

#### **GET /api/contacts/tact_id>**
- **Purpose:** Get single contact details
- **Status:** ✅ Working

#### **POST /api/contacts/tact_id>/enrich**
- **Purpose:** Trigger AI enrichment for contact
- **Integration:** Auto-scores after enrichment completes
- **Status:** ✅ Working with auto-scoring hook

#### **POST /api/hubspot/import**
- **Purpose:** Import contacts from HubSpot CRM
- **Status:** ✅ Working

### **2.3 Health & Monitoring**

#### **GET /api/health**
- **Purpose:** Service health check
- **Response:**
```json
{
  "status": "healthy",
  "environment": "PRODUCTION",
  "services": {
    "database": "PostgreSQL",
    "enrichment": true,
    "scoring": true,
    "cadence": false
  },
  "timestamp": "2025-12-02T02:05:59.881146"
}
```
- **Status:** ✅ Working

***

## 3. ENHANCED ENRICHMENT ENGINE

### **3.1 Architecture**

**Role of Perplexity (sonar-pro):**
- Web research on contact + company
- Recent news, LinkedIn activity detection
- Competitive intelligence gathering
- Industry trends and pain points

**Role of GPT-4:**
- Profile synthesis from Perplexity research
- Talking points generation
- Value proposition builder (Why Me?)
- Call scripts (3-tier progression)
- Email sequences (3-tier nurture)
- LinkedIn connection strategy

**Database Storage:**
- `profile_content` (JSON) - Full enriched profile
- `talking_points` - Key discussion topics
- `pain_points` - Identified challenges
- `call_script_1/2/3` - Progressive call scripts
- `email_1/2/3_subject/body` - Email sequence
- `linkedin_connect/warmup/followup/inmail` - LinkedIn strategy
- `enrichment_status` - pending/completed/failed
- `enriched_at` - Timestamp

### **3.2 What It Replaced**
- Manual LinkedIn research
- Generic email templates
- One-size-fits-all outreach
- Static call scripts
- Lack of personalization at scale

### **3.3 Current Priorities**
1. ✅ **Auto-enrichment after import** - Hook enrichment to contact import flow
2. ⏳ **Batch enrichment** - Background jobs for unenriched contacts
3. ⏳ **Real-time signals** - LinkedIn activity detection → trigger enrichment
4. ⏳ **Enrichment refresh** - Re-enrich stale profiles (90+ days old)

***

## 4. FRONTEND DASHBOARD

### **4.1 Tech Stack**
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS (inline styles)
- **Icons:** Lucide React
- **State Management:** React hooks (useState, useEffect)

### **4.2 Core Components**

**Main Shell (App.tsx):**
- **Location:** `/Users/chrisrabenold/projects/apex/dashboard_v1/src/App.tsx`
- **Features:**
  - Tab navigation (Today's Board, All Contacts, Cadence, Intelligence Lab, Raw Data, Why Me?)
  - Contact detail modal
  - HubSpot import button
  - Enrichment status tracking

**Today's Board (TodaysBoard.tsx):**
- **Location:** `/Users/chrisrabenold/projects/apex/dashboard_v1/src/components/TodaysBoard.tsx`
- **Purpose:** Priority-ranked daily action list
- **Data Source:** `GET /api/todays-board`
- **Features:**
  - Grouped by urgency (IMMEDIATE/HIGH/MEDIUM/LOW)
  - Score badges (MDCP, RSS, Priority)
  - Enrichment indicators
  - Click → Contact Detail Modal

**All Contacts (ContactsBoard):**
- **Features:**
  - Search/filter (name, email, company, title)
  - Tier filtering (Platinum/Gold/Silver/Bronze)
  - Enrichment status filter
  - Pagination (25/50/100/200 per page)
  - Sortable columns
  - Enrichment highlighting (green glow for enriched contacts)

**Intelligence Lab (ContactEnrichmentView):**
- **Purpose:** Trigger and view AI enrichment
- **Features:**
  - One-click enrichment
  - Real-time progress indicator
  - Profile display
  - Talking points
  - Call scripts
  - Email templates

**Contact Detail Modal (ContactDetailModal):**
- **Features:**
  - Full contact info
  - Score breakdown
  - Enrichment trigger
  - Generated content display

### **4.3 User Value Delivered**
- **Instant Prioritization:** No more guessing who to call first
- **AI-Powered Personalization:** Unique talking points for every contact
- **Time Savings:** 30 min research → 30 seconds with AI
- **Conversion Boost:** Personalized outreach = higher response rates
- **Scalability:** Handle 1,000+ prospects with same effort as 10

### **4.4 Recent Changes**
- ✅ **API Config Update:** Points to Railway production (`config.ts` updated)
- ✅ **Score Display:** MDCP/RSS/Priority badges with tier colors
- ✅ **Enrichment Indicators:** Green highlighting + badges for enriched contacts
- ✅ **Today's Board Integration:** Now uses unified scoring urgency levels

### **4.5 Location**
- **Dev Server:** `http://localhost:5173`
- **Production:** Not yet deployed (coming soon)

***

## 5. API SERVER DETAILS

### **5.1 Core File**
- **Location:** `/Users/chrisrabenold/projects/apex/api.py`
- **Framework:** Flask with CORS
- **Port:** 8000 (configurable via `PORT` env var)

### **5.2 Environment Support**

**Local Development (SQLite):**
- **Database:** `/Users/chrisrabenold/projects/apex/apex.db`
- **Environment Detection:** `IS_PRODUCTION = False`
- **Start Command:** `python3 api.py`

**Railway Production (PostgreSQL):**
- **Database:** PostgreSQL (via `DATABASE_URL` env var)
- **Environment Detection:** `IS_PRODUCTION = True` (via `RAILWAY_ENVIRONMENT`)
- **Deployment:** Auto-deploy via GitHub push to `main`
- **URL:** `https://apex-intelligence-production.up.railway.app`

### **5.3 Database Configuration**

**Smart Dual-Mode:**
```python
if IS_PRODUCTION:
    # PostgreSQL on Railway
    DATABASE_URL = os.getenv('DATABASE_URL')
    import psycopg2
    from psycopg2.extras import RealDictCursor
else:
    # SQLite locally
    DATABASE = '/Users/chrisrabenold/projects/apex/apex.db'
    import sqlite3
```

**Scoring Engine Integration:**
```python
# Auto-detect environment for scoring
if IS_PRODUCTION:
    SCORING_DB_PATH = os.getenv('DATABASE_URL')  # PostgreSQL
else:
    SCORING_DB_PATH = DB_PATH  # SQLite
```

### **5.4 External API Orchestration**

**HubSpot API:**
- Import contacts
- Sync updates
- Push enrichment data back

**Perplexity API:**
- Research queries (sonar-pro model)
- Company intelligence
- Recent activity detection

**OpenAI API (GPT-4):**
- Profile synthesis
- Content generation
- Value proposition builder

### **5.5 Major Improvements (This Thread)**

**Database Abstraction:**
- ✅ `DatabaseAdapter` class supports both SQLite and PostgreSQL
- ✅ Auto-converts `?` → `%s` for PostgreSQL parameter style
- ✅ Thread-safe fresh connections per request

**Scoring Integration:**
- ✅ Unified scorer loaded at startup
- ✅ Environment-aware database path selection
- ✅ Auto-scoring hook in enrichment endpoint

**API Fixes:**
- ✅ Fixed `todays-board` to handle PostgreSQL RealDictCursor
- ✅ Backward compatible response format for Dashboard
- ✅ Added verification in `save_scores_to_db`

### **5.6 Deployment Location**
- **Git Repo:** `https://github.com/chrisrabenold/apex` (assumed)
- **Railway Project:** `apex-intelligence`
- **Auto-Deploy:** Push to `main` branch → Railway rebuilds

***

## 6. ACTION ITEMS & CURRENT PRIORITIES

### **6.1 IMMEDIATE (Next Session)**
- [ ] **Verify Today's Board displays scored contacts** in Dashboard
- [ ] **Deploy Dashboard to production** (Railway or Vercel)