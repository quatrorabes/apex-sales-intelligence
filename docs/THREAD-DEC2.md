# APEX SALES INTELLIGENCE – SYSTEM REFERENCE GUIDE

**Date**: December 2, 2025  
**Status**: Production-ready with active persona classification system  
**Environment**: Dual (Local: SQLite + localhost:8000 | Production: PostgreSQL on Railway)

***

## 1. SYSTEM OVERVIEW

**Apex Sales Intelligence** is a production AI-powered sales intelligence platform for commercial real estate and business lending. It automates contact enrichment, persona classification, lead scoring (MDCP), and outreach prioritization for sales teams targeting bankers, brokers, SBA lenders, and borrowers.

**Core Value Proposition**: Transforms basic contact data (name, title, company) into actionable sales intelligence with automated persona classification, comprehensive professional profiles, and prioritized daily action lists.

***

## 2. KEY PROGRAMS & COMPONENTS

### A. Apex Intelligence API Server (`api.py`)

**Location**: `projects/apex/api.py` (654+ lines)  
**Type**: Python Flask REST API  
**Database**: 
- Local: SQLite (`apex.db`)
- Production: PostgreSQL on Railway

**Purpose**: Core backend orchestrating enrichment, scoring, persona classification, contact CRUD, and Today's Board generation.

**What It Replaced**: Manual LinkedIn research, spreadsheet-based scoring, disconnected HubSpot workflows.

**Key Features**:
- 3-stage enrichment pipeline (Perplexity → GPT-4 → Database)
- Unified Apex Scoring Engine (MDCP + Priority scores)
- 8-Persona classification system
- Dual-environment configuration
- External API orchestration (Perplexity, OpenAI, HubSpot)

**Deployment**: Railway at `apex-intelligence-production.up.railway.app`

**Current Priorities**:
1. ✅ COMPLETE: Persona classification system integrated
2. Add retry logic for Perplexity/OpenAI timeouts
3. Implement `/api/contacts/:id/score` manual trigger endpoint
4. Add health monitoring on Railway
5. Document scoring weights and tier thresholds

***

### B. Enhanced Enrichment Engine (Profile Builder)

**Location**: Inline class in `api.py` (lines 60-400)  
**Type**: 3-stage AI intelligence pipeline

**Architecture**:

**Stage 1: Perplexity Research**
- Model: `sonar-pro`
- Purpose: Open-ended professional research
- Input: Name, title, company, LinkedIn URL (if available)
- Output: Raw research data with citations

**Stage 2: GPT-4 Intelligence Layer**
- Model: `gpt-4`
- Purpose: Structure raw data + add strategic intelligence
- Output: 12-section markdown profile

**Stage 3: Database Persistence**
- Saves to `contacts.profile_content`
- Triggers auto-scoring (MDCP + Priority)
- Updates `enrichment_status = 'completed'`

**Output Format** (12 sections):
1. Overview – Executive summary
2. Professional Background – Career trajectory with dates
3. Education & Credentials – Degrees, institutions, honors
4. Recent Mentions – News, LinkedIn activity
5. Social Media Profiles – LinkedIn, Twitter, etc.
6. Personality Detail – Myers-Briggs assessment
7. Myers-Briggs Summary – Work style implications
8. Company Overview – Mission, HQ, size
9. Pain Points & Challenges – 5 specific pain points
10. Sales Opportunities & Talking Points – 5 actionable items
11. Key Insights – 3 non-obvious intelligence points
12. Final Note – Strategic summary for engagement

**What It Replaced**: Manual web research, unstructured notes, inconsistent profile quality.

**Current Priorities**:
1. Improve LinkedIn profile discovery (add `site:linkedin.com/in` to queries)
2. Add citation enforcement to Stage 2 prompt
3. Flag low-quality enrichments (`profile_content < 1000 chars`)
4. Implement retry logic for sparse results

***

### C. 8-Persona Classification System

**Location**: `apps/backend/intelligence/engines/classification/apex_8persona_classifier.py`  
**Type**: Rule-based keyword classifier with confidence scoring

**8 Personas**:
1. **banker** – Commercial lenders, BDOs, relationship managers
2. **sba_banker** – SBA specialists, 504/7(a) lenders
3. **loan_broker** – Commercial mortgage brokers, capital advisors
4. **sales_broker** – CRE brokers, business brokers, M&A advisors
5. **referral_network_other** – EDOs, chamber executives, coaches
6. **internal** – Harvest staff (identified by company name)
7. **borrower** – Business owners, CEOs, founders (with LLC/Inc)
8. **past_borrower** – Former owners, retired executives

**Scoring Logic**:
- Title match: up to 60 pts (keyword density × 25)
- Company match: up to 25 pts (keyword density × 15)
- Profile/industry match: up to 15 pts (keyword density × 8)
- Minimum threshold: 20 pts (below = `unclassified`)

**Seeded Company Lists**:
- Top US banks: JPMorgan Chase, Bank of America, Wells Fargo, PNC, Truist, etc.
- Top SBA lenders: Live Oak Bank, Celtic Bank, Newtek, ReadyCap, etc.
- Top CRE brokerages: CBRE, Cushman & Wakefield, JLL, Colliers, Newmark, Marcus & Millichap
- Top commercial mortgage shops: Meridian Capital, Berkadia, Walker & Dunlop, etc.

**Bulk Classification Script**: `bulk_classify_personas_prod.py`

**Current Status**:
- ✅ Classifier loaded and tested
- ✅ Bulk script operational
- ⚠️ `personaconfidence` column showing `None` – needs investigation

**Current Priorities**:
1. **URGENT**: Fix `personaconfidence = None` issue (column exists but values not writing)
2. Run full classification: `python bulk_classify_personas_prod.py --limit 10000 --reclassify-existing`
3. Verify high-ID contacts (2000+) get classified
4. Add more bank/broker names to keyword lists (target 50+ each)

***

### D. MDCP Scoring Engine (ApexScoringEngine)

**Location**: `apps/backend/intelligence/engines/scoring/unified_apex_scorer.py`  
**Type**: Multi-factor scoring algorithm

**Scores**:
- **MDCP Score** (0-100): Market + Decision-maker + Contact quality + Priority
- **Priority Score**: Weighted composite for urgency ranking
- **RSS Score** (Relationship Strength): Placeholder (50.0) – requires activity tracking

**Integration**: Auto-triggered after Stage 3 enrichment completion.

**What It Replaced**: Manual lead scoring, static tier assignments, gut-feel prioritization.

**Current Priorities**:
1. Verify scoring populates on enrichment
2. Implement RSS score calculation (requires `contact_activities` data)
3. Document scoring weights and tier thresholds
4. Add user feedback loop for score adjustments

***

### E. Dashboard_v1 (React Frontend)

**Location**: `projects/apex/dashboard_v1`  
**Tech Stack**: React + TypeScript + Vite + Tailwind CSS  
**Deployment**: Railway static hosting

**Key Components**:

**TodaysBoard.tsx**
- Displays prioritized contacts: Urgent Relationships, Warm Relationships, Hot Prospects, Qualified Prospects
- Maps MDCP scores to urgency tiers
- Shows "Why Now" messages and recommended actions

**ContactEnrichmentView.tsx**
- Contact list with enrichment status badges
- Trigger enrichment with one click
- Search, filter, pagination

**ContactDetailModal.tsx**
- Tabs: Dossier, Intelligence, Outreach
- Intelligence subtabs: Pain Points, Product Fit, Insights
- Email/call/LinkedIn templates

**ApexIntelligence.tsx**
- Displays 12-section enriched profiles
- Markdown rendering with section extraction

**CadenceDashboard.tsx**
- Multi-touch sequence management
- Track emails, calls, LinkedIn touches
- Auto-advance logic

**What It Replaced**: Excel tracking sheets, manual HubSpot views, no centralized intelligence display.

**Current Status**:
- ✅ All components use env-based API URLs (`VITE_API_URL`)
- ✅ Today's Board parsing fixed (matches API response structure)
- ✅ Markdown cleanup applied to Intelligence tabs
- ✅ NaN score warnings eliminated

**Current Priorities**:
1. Add persona badges/columns to contact list
2. Wire up persona filtering in Today's Board
3. Test enrichment workflow end-to-end on Railway
4. Add EnrichmentWarning component (if LinkedIn URL missing)
5. Remove debug banner before production launch

***

## 3. MAJOR API ENDPOINTS

### `/api/health` (GET)
**Purpose**: Health check with service status  
**Returns**: Environment, timestamp, service availability (enrichment, scoring, database)  
**Location**: `api.py` line ~580

***

### `/api/contacts` (GET)
**Purpose**: List contacts with filtering and pagination  
**Params**: `?status=pending&limit=100`  
**Returns**: Array of contacts ordered by `created_at DESC`  
**Location**: `api.py` line ~450  
**What It Replaced**: Manual database queries

**Current Issue**: Returns high-ID contacts first (2000+), which haven't been classified yet. Need to run full bulk classification.

***

### `/api/contacts/:id` (GET)
**Purpose**: Get single contact with full profile  
**Returns**: Contact object including `profile_content`, `persona`, `personaconfidence`, scores  
**Location**: `api.py` line ~480

***

### `/api/contacts/:id/enrich` (POST)
**Purpose**: Trigger 3-stage enrichment for a contact  
**Process**:
1. Fetch contact from DB
2. Run Perplexity research (Stage 1)
3. GPT-4 structuring + intelligence (Stage 2)
4. Save to DB + auto-score (Stage 3)

**Returns**:
```json
{
  "success": true,
  "contact_id": 123,
  "status": "enriched",
  "profile_length": 4500,
  "scores": {
    "mdcp_score": 85,
    "priority_score": 78,
    "tier": "A"
  }
}
```

**Location**: `api.py` line ~420  
**What It Replaced**: Manual LinkedIn research, copy-paste enrichment

**Current Priorities**:
1. Add retry logic for API timeouts
2. Require LinkedIn URL or show warning
3. Track `profile_content` length and flag low-quality results

***

### `/api/todays-board` (GET)
**Purpose**: Daily prioritized action list  
**Returns**:
```json
{
  "date": "Dec 2, 2025",
  "recommendation": "Focus on 5 urgent relationships...",
  "relationships": {
    "urgent": [...],
    "warm": [...],
    "nurture": [...],
    "stable": [...]
  },
  "newprospects": {
    "tiers": {
      "hot": [...],
      "qualified": [...]
    }
  }
}
```

**Filtering Logic**:
- Relationships: `persona IN ('banker', 'sba_banker', 'loan_broker', 'sales_broker', 'referral_network_other')`
- Tiers: `mdcp_score >= 80` = urgent, `>= 60` = warm, `>= 40` = nurture, else stable
- New Prospects: `persona IN ('borrower')`, sorted by priority

**Location**: `api.py` lines 730-820  
**What It Replaced**: Static Excel priority lists, manual calendar planning

**Current Priorities**:
1. Add RSS score integration (when activity tracking is ready)
2. Implement relationship tiers (nurture, stable)
3. Add date filters
4. Create "Why Now" message generator
5. Add "Mark Contacted" quick action

***

## 4. DATABASE SCHEMA

### `contacts` Table (Primary)

**Key Columns**:
```
id                   SERIAL PRIMARY KEY
name                 VARCHAR(255)
title                VARCHAR(255)
company              VARCHAR(255)
email                VARCHAR(255)
phone                VARCHAR(50)
linkedin_url         TEXT
profile_content      TEXT              -- Stage 3 enrichment output
enrichment_status    VARCHAR(50)       -- pending/completed/failed
enrichment_date      TIMESTAMP

-- Scoring
mdcp_score           REAL
priority_score       REAL
rss_score            REAL              -- Placeholder (50.0)

-- Persona (NEW)
persona              VARCHAR(50)       -- banker, sba_banker, loan_broker, etc.
personaconfidence    REAL              -- 0-100 confidence score

-- Metadata
created_at           TIMESTAMP DEFAULT NOW()
updated_at           TIMESTAMP DEFAULT NOW()
last_contact_date    DATE
```

**Current Issue**: `personaconfidence` column exists but values are `None` after bulk classification. Need to debug UPDATE statement.

***

### `contact_activities` Table

**Purpose**: Track engagement history (calls, emails, meetings)  
**Status**: Schema created, not yet populated  
**Future Use**: Calculate RSS (Relationship Strength Score)

```sql
id                INTEGER PRIMARY KEY
contact_id        INTEGER REFERENCES contacts(id)
activity_type     VARCHAR(50)  -- call, email, meeting, linkedin
activity_date     TIMESTAMP
direction         VARCHAR(20)  -- inbound, outbound
subject           TEXT
notes             TEXT
outcome           VARCHAR(100)
created_at        TIMESTAMP DEFAULT NOW()
```

***

### `opportunity_signals` Table

**Purpose**: Track buying signals (LinkedIn activity, company news, etc.)  
**Status**: Schema created, not yet populated

```sql
id                INTEGER PRIMARY KEY
contact_id        INTEGER REFERENCES contacts(id)
signal_type       VARCHAR(50)  -- linkedin_activity, company_news, job_change
signal_date       TIMESTAMP
signal_data       TEXT         -- JSON payload
urgency_boost     INTEGER      -- +10 points to priority score
viewed            BOOLEAN      DEFAULT FALSE
created_at        TIMESTAMP DEFAULT NOW()
```

***

## 5. DEPLOYMENT & ENVIRONMENTS

### Local Development
- **API**: `localhost:8000` (SQLite `apex.db`)
- **Dashboard**: `localhost:5173` (Vite dev server)
- **Start Commands**:
```bash
cd projects/apex
source .venv/bin/activate
python api.py                    # Backend on 8000

cd dashboard_v1
npm run dev                      # Frontend on 5173
```

***

### Production (Railway)
- **API**: `apex-intelligence-production.up.railway.app`
- **Database**: PostgreSQL on Railway
- **Dashboard**: Railway static deployment
- **Deploy Process**: Push to `origin/main` triggers auto-deploy

**Environment Variables** (Railway):
```
DATABASE_URL=postgresql://...
PERPLEXITY_API_KEY=...
OPENAI_API_KEY=...
HUBSPOT_ACCESS_TOKEN=...
PORT=8000
```

***

## 6. CURRENT ACTION ITEMS (PRIORITY ORDER)

### 🚨 CRITICAL (Do Now)

1. **Fix `personaconfidence = None` Issue**
   - Debug: Check actual column name in Postgres
   - Run: `python -c "import os; import psycopg2; conn = psycopg2.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name = 'contacts' AND column_name LIKE '%persona%'\"); print([row[0] for row in cur.fetchall()]); conn.close()"`
   - Fix UPDATE statement if column name is mismatched

2. **Run Full Persona Classification**
   ```bash
   python bulk_classify_personas_prod.py --limit 10000 --reclassify-existing
   ```

3. **Verify High-ID Contacts Are Classified**
   - Check IDs 2000+ have persona values
   - Dashboard shows these first (ORDER BY created_at DESC)

***

### 🔥 HIGH PRIORITY (This Week)

4. **Add Persona Display to Dashboard**
   - Add persona badge/column to contact list in `ContactEnrichmentView.tsx`
   - Add persona filter to Today's Board
   - Show persona in `ContactDetailModal.tsx`

5. **Improve LinkedIn Discovery in Enrichment**
   - Update Perplexity query: `"site:linkedin.com/in {name} {company}"`
   - Add verification step to confirm profile matches contact

6. **Add Enrichment Validation**
   - Show warning if LinkedIn URL is missing
   - Flag profiles with `profile_content < 1000 chars` for re-enrichment

7. **Test End-to-End Enrichment Workflow**
   - Enrich contact from Dashboard → verify profile displays → verify scores populate

***

### 📋 MEDIUM PRIORITY (Next Sprint)

8. **Implement RSS Score Calculation**
   - Requires populating `contact_activities` table
   - Algorithm: recency × frequency × outcome quality

9. **Add Retry Logic to Enrichment**
   - Exponential backoff for Perplexity/OpenAI timeouts
   - Store failed attempts in `enrichment_errors` table

10. **Expand Persona Keyword Lists**
    - Target 50+ banks, SBA lenders, brokerages per category
    - Add regional banks, community banks, credit unions

11. **Document Scoring Logic**
    - MDCP weight breakdown
    - Tier thresholds (A/B/C/D)
    - User feedback loop design

***

### 🔮 FUTURE ENHANCEMENTS

12. **CRM Import Pipeline**
    - HubSpot connector (priority 1)
    - Salesforce connector (priority 2)
    - Pipedrive connector (priority 3)

13. **Activity Tracking Integration**
    - Sync HubSpot activities → `contact_activities`
    - Manual activity logging from Dashboard
    - Calendar integration for meetings

14. **Signal Detection System**
    - LinkedIn activity monitoring
    - Company news alerts (funding, expansion, M&A)
    - Job change notifications

15. **Cadence Automation**
    - Multi-touch sequences (email + call + LinkedIn)
    - Auto-advance based on response
    - A/B testing for messaging

***

## 7. QUICK REFERENCE COMMANDS

### Check System Health
```bash
curl http://localhost:8000/api/health | jq
```

### Check Persona Columns in Postgres
```bash
python -c "import os; import psycopg2; conn = psycopg2.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(); cur.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name = 'contacts' AND column_name LIKE '%persona%'\"); print([row[0] for row in cur.fetchall()]); conn.close()"
```

### View Classified Contacts
```bash
python -c "import os; import psycopg2; from psycopg2.extras import RealDictCursor; conn = psycopg2.connect(os.getenv('DATABASE_URL')); cur = conn.cursor(cursor_factory=RealDictCursor); cur.execute('SELECT id, name, company, persona, personaconfidence FROM contacts WHERE persona IS NOT NULL ORDER BY id DESC LIMIT 10'); [print(f\"ID={r['id']} | {r['name']} | {r['company']} | {r['persona']} ({r['personaconfidence']})\") for r in cur.fetchall()]; conn.close()"
```

### Test Enrichment
```bash
curl -X POST http://localhost:8000/api/contacts/123/enrich | jq
```

### View Today's Board
```bash
curl http://localhost:8000/api/todays-board | jq '.newprospects.tiers.hot'
```

### Run Bulk Classification
```bash
python bulk_classify_personas_prod.py --limit 10000 --reclassify-existing
```

### Deploy to Railway
```bash
git add -A
git commit -m "Update message"
git push origin main
railway logs
```

***

## 8. KEY DECISIONS & PATTERNS

### Why Inline `EnhancedEnrichment` Class?
- Avoids import path issues on Railway
- Keeps enrichment logic self-contained
- Single source of truth for Profile Builder

### Why Dual Environment Support?
- SQLite for fast local development
- PostgreSQL for production scale
- Same codebase, different `DATABASE_URL`

### Why 8 Personas (Not More)?
- Covers 95%+ of commercial lending ecosystem
- Simple enough for sales reps to understand
- Extensible (can add more without breaking existing)

### Why MDCP Scoring?
- **M**arket: Industry attractiveness
- **D**ecision-maker: Title authority
- **C**ontact: Data completeness
- **P**riority: Urgency signals
- Proven framework from sales methodology

***

## 9. TROUBLESHOOTING

### "Persona classifier unavailable"
- Check `CLASSIFICATION_PATH` in `bulk_classify_personas_prod.py`
- Verify `apex_8persona_classifier.py` exists at `apps/backend/intelligence/engines/classification/`

### "Column 'personaconfidence' does not exist"
- Run migration: `python scripts/add_persona_confidence_column.py`
- Or manually: `ALTER TABLE contacts ADD COLUMN personaconfidence REAL;`

### "Enrichment returns empty profile"
- Check LinkedIn URL is present
- Verify Perplexity API key is valid
- Check API logs for timeout errors

### "Dashboard shows old contact data"
- Clear browser cache
- Check API endpoint returns updated data
- Verify `updated_at` timestamp in DB

***

**END OF REFERENCE GUIDE**

This document should serve as the canonical reference for Apex Sales Intelligence. Update it as new features ship or architecture changes.
This document should serve as the canonical reference for Apex Sales Intelligence. Update it as new features ship or architecture changes.