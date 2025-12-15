# APEX INTELLIGENCE - COMPLETE SYSTEM ARCHITECTURE
## Comprehensive Technical Documentation for Thread Handoff
**Generated:** 2025-11-26 | **Status:** Production | **Scope:** Full Stack

---

## EXECUTIVE SUMMARY

**Apex Intelligence** is an AI-powered sales intelligence platform that enriches contact data, scores leads, and generates personalized outreach content (emails, call scripts, LinkedIn messages). The system integrates HubSpot for contact import, Perplexity + OpenAI for enrichment, and a custom scoring engine for lead prioritization.

### **Core Functions:**
1. **Contact Import** → HubSpot → SQLite Database
2. **AI Enrichment** → Perplexity (research) + OpenAI (polishing)
3. **Lead Scoring** → MDCP, Role/RSS, Priority scores
4. **Content Generation** → 3 emails + 3 call scripts + 2 LinkedIn messages
5. **Frontend Dashboard** → React/TypeScript with contact detail views

---

## SYSTEM ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APEX INTELLIGENCE PLATFORM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────┐         ┌──────────────┐        ┌─────────────────────┐   │
│  │  HubSpot   │────────→│   Flask API  │        │   SQLite Database   │   │
│  │   CRM      │ Import  │   (Port 8000)│←──────→│  apex.db            │   │
│  └────────────┘         └──────┬───────┘        └─────────────────────┘   │
│                                 │                         ▲                 │
│                                 │ Routes                  │ Read/Write      │
│                                 ▼                         │                 │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                    BACKEND INTELLIGENCE ENGINES                     │   │
│  ├────────────────────────────────────────────────────────────────────┤   │
│  │                                                                    │   │
│  │  ┌──────────────────┐    ┌──────────────────┐   ┌──────────────┐ │   │
│  │  │  ENRICHMENT      │    │  SCORING ENGINE  │   │  CONTENT     │ │   │
│  │  │  ──────────────  │    │  ──────────────  │   │  GENERATOR   │ │   │
│  │  │                  │    │                  │   │  ──────────  │ │   │
│  │  │ • Perplexity API │    │ • MDCP Scoring   │   │ • EmailGen   │ │   │
│  │  │ • Enhanced       │    │ • RSS Scoring    │   │ • CallScript │ │   │
│  │  │   Research       │    │ • Priority       │   │ • LinkedIn   │ │   │
│  │  │ • Profile Parsing│    │ • Urgency       │   │   Messages   │ │   │
│  │  │ • Markdown       │    │ • Tiers         │   │ • Uses GPT-4 │ │   │
│  │  │   Extraction     │    │ • Vertical      │   │              │ │   │
│  │  │                  │    │ • Multi-tenant  │   │              │ │   │
│  │  └──────────────────┘    └──────────────────┘   └──────────────┘ │   │
│  │                                                                    │   │
│  └────────────────────────────────────────────────────────────────────┘   │
│           │ perplexity_key    │ scoring wrappers    │ openai_key         │
│           ▼                   ▼                     ▼                     │
│  ┌──────────────────┐ ┌─────────────────┐ ┌──────────────────┐         │
│  │ Perplexity API   │ │ Intelligence DB │ │  OpenAI API      │         │
│  │ (sonar-pro)      │ │ Calculations    │ │  (gpt-4o)        │         │
│  └──────────────────┘ └─────────────────┘ └──────────────────┘         │
│                                                                              │
│                          ┌────────────────────┐                            │
│                          │  Frontend (React)  │                            │
│                          │  ──────────────    │                            │
│                          │ • Dashboard        │                            │
│                          │ • Contact Lists    │                            │
│                          │ • Detail Modal     │                            │
│                          │ • Enrichment View  │                            │
│                          │ • Content Viewer   │                            │
│                          └────────────────────┘                            │
│                                 ▲                                          │
│                                 │ HTTP Requests (Port 3000)               │
│                                 │                                          │
│                          ┌────────────────────┐                            │
│                          │   User Browser     │                            │
│                          └────────────────────┘                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## DETAILED COMPONENT BREAKDOWN

### 1. **BACKEND - Flask API Server** (`api.py`)
**Location:** `~/projects/apex/apps/backend/api.py`  
**Port:** 8000  
**Framework:** Flask + CORS  
**Database:** SQLite3 (`~/projects/apex/apex.db`)

#### Key Endpoints:

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/health` | GET | Health check | ✅ Works |
| `/api/contacts` | GET | List all contacts | ✅ Works |
| `/api/contacts/<id>` | GET | Get single contact | ✅ Works |
| `/api/hubspot/import` | POST | Import from HubSpot | ✅ Works |
| `/api/contacts/<id>/enrich` | POST | Run AI enrichment | ✅ Works |
| `/api/contacts/<id>/generate-content` | POST | Generate emails/scripts/LinkedIn | ⚠️ **ISSUE** |
| `/api/contacts/<id>/intelligence` | GET | Get intelligence data | ✅ Works |
| `/api/contacts/<id>/score` | POST | Score single contact | ✅ Works |
| `/api/contacts/score-batch` | POST | Batch score | ✅ Works |
| `/api/apex/scores` | GET | All scored contacts | ✅ Works |

#### Database Schema (contacts table):

```sql
CREATE TABLE contacts (
  id INTEGER PRIMARY KEY,
  name TEXT,
  firstname TEXT,
  lastname TEXT,
  email TEXT,
  phone TEXT,
  company TEXT,
  title TEXT,
  hubspotid TEXT,
  linkedinurl TEXT,
  leadstatus TEXT,
  lifecyclestage TEXT,
  
  -- Enrichment
  enrichmentstatus TEXT (pending|enriching|complete),
  enrichmentdata TEXT (JSON),
  profilecontent TEXT (Full markdown profile),
  perplexitydata TEXT (JSON),
  enrichedat TIMESTAMP,
  
  -- Scoring
  mdcpscore REAL,
  mdcptier TEXT,
  rssscore REAL,
  rsstier TEXT,
  priorityscore REAL,
  urgencylevel TEXT,
  recommendedaction TEXT,
  
  -- Content Generation
  email1subject TEXT,
  email1body TEXT,
  callscript1 TEXT,
  linkedinrequest TEXT,
  contentgeneratedat TIMESTAMP,
  
  -- Metadata
  createdat TIMESTAMP,
  lastscored TIMESTAMP
);
```

---

### 2. **ENRICHMENT ENGINE**
**Location:** `~/projects/apex/apps/backend/intelligence/engines/enrichment/`

#### 2.1 **EnhancedPerplexityEnrichment** (`enhanced_perplexity.py`)

**Purpose:** Deep research on contact + company  
**Uses:** Perplexity API (sonar-pro model)  
**Output:** Structured markdown profile

**Sections Generated:**
1. Professional Profile (Overview, Background, Education, Recent Mentions, Social Profiles)
2. Personality Detail (MBTI assessment)
3. Myers-Briggs Assessment Summary
4. Sales Talking Points
5. **ENTIRE Company Corporate Profile** (Overview, Products, Leadership, Competitors, News, Fun Facts)
6. Strategic Intelligence (Pain Points, SBA Interests, Key Insights)

**Process:**
```
Contact (name, title, company) 
  → Perplexity Research 
  → Structured Markdown 
  → OpenAI Polish 
  → Extracted Sections 
  → Database Storage
```

**Column Stored:** `enrichmentdata` (JSON) + `profilecontent` (full markdown text)

---

### 3. **SCORING ENGINE**
**Location:** `~/projects/apex/apps/backend/intelligence/engines/scoring/`

**Three Parallel Scoring Models:**

#### 3.1 **MDCP Score** (Market, Deal, Company, Person)
- Market fit: 25 points
- Deal timing: 20 points
- Company size/vertical: 25 points
- Person seniority/fit: 30 points
- **Range:** 0-100

#### 3.2 **RSS Score** (Role, Seniority, Signals)
- Role match: 40 points
- Seniority level: 35 points
- Engagement signals: 25 points
- **Range:** 0-100

#### 3.3 **Priority Score** (Weighted Composite)
- (MDCP × 0.4) + (RSS × 0.3) + (Data Completeness × 0.3)
- **Range:** 0-100

#### Tier Assignment:
```
Priority ≥ 80  → MDCP Tier = "HOT"    | Urgency = "IMMEDIATE"
Priority 60-79 → MDCP Tier = "WARM"   | Urgency = "HIGH"
Priority < 60  → MDCP Tier = "COLD"   | Urgency = "MEDIUM"
```

---

### 4. **CONTENT GENERATION ENGINE**
**Location:** `~/projects/apex/apps/backend/intelligence/engines/content/`

#### 4.1 **Email Generator** (`email_generator.py`)
**Generates:** 3 personalized emails (Introduction, Value Add, Breakup)
**Uses:** GPT-4o model
**Input:** Contact name, title, company, enrichment text (2000 chars)
**Output:** Subject line + body (150-200 words)
**Stored in:** `email1subject`, `email1body` columns

#### 4.2 **Call Script Generator** (`call_script_generator.py`)
**Generates:** 3 call scripts (Cold Call, Follow-up, Executive Brief)
**Uses:** GPT-4o model
**Input:** Same as email generator
**Output:** Natural conversation script with objection handling
**Stored in:** `callscript1` column

#### 4.3 **LinkedIn Message Generator** (inline in api.py)
**Generates:** 2 LinkedIn messages (Connection Request, Follow-up)
**Uses:** GPT-4o model
**Constraints:** < 300 chars for connection, < 600 for follow-up
**Output:** Single message text
**Stored in:** `linkedinrequest` column

#### **⚠️ KNOWN ISSUE - Content Not Populating:**

**Problem:** Content is generated in API but not displaying in frontend modal.

**Root Cause Analysis:**
1. **API endpoint** `/api/contacts/<id>/generate-content` creates content ✅
2. **Database columns** are being written: `email1subject`, `email1body`, `callscript1`, `linkedinrequest` ✅
3. **Frontend** calls endpoint via `ContentGenerator.tsx` component ✅
4. **Frontend** doesn't properly read/display the saved data ❌

**Likely Culprits:**
- ContentGenerator component isn't fetching from database after generation
- Column names might be inconsistent (email1body vs email_body)
- Response structure from API doesn't match component expectations
- Component state not updating after API response

---

### 5. **FRONTEND - React Dashboard**
**Location:** `~/projects/apex/dashboard_v1/src/`
**Port:** 3000
**Framework:** React 18 + TypeScript + Vite

#### 5.1 **Main Components:**

| Component | File | Purpose |
|-----------|------|---------|
| **App** | `App.tsx` | Main entry, routing |
| **ApexIntelligence** | `ApexIntelligence.tsx` | Dashboard grid layout |
| **ContactDetailModal** | `ContactDetailModal.tsx` | Contact detail view with 6 tabs |
| **ContentGenerator** | `ContentGenerator.tsx` | Email/call/LinkedIn content display |
| **ContactEnrichmentView** | `ContactEnrichmentView.tsx` | Enrichment status + details |
| **CadenceDashboard** | `CadenceDashboard.tsx` | Outreach sequence visualization |
| **RawDataViewer** | `RawDataViewer.tsx` | Debug JSON view |

#### 5.2 **ContactDetailModal - Tab Structure (CORRECTED):**

```
┌─────────────────────────────────────────────────────┐
│  CONTACT DETAIL MODAL                               │
├─────────────────────────────────────────────────────┤
│  Tabs: [Overview] [Personal] [Company] [Personality] [Chat Things] [Content]
│
│  🔹 OVERVIEW TAB
│     ├─ Section 1: Professional Overview
│     └─ Section 8: Sales Talking Points (bullet list)
│
│  👤 PERSONAL TAB
│     ├─ Section 2: Background & Experience (bullets)
│     ├─ Section 3: Education
│     └─ Section 4: Recent Mentions
│
│  🏢 COMPANY TAB
│     └─ ENTIRE "MARCUS & MILLICHAP CAPITAL CORP: CORPORATE PROFILE"
│        ├─ Section 1: Overview
│        ├─ Section 2: Products & Services
│        ├─ Section 3: Leadership
│        ├─ Section 4: Market & Competitors
│        ├─ Section 5: Recent News
│        └─ Section 6: Company Fun Facts
│
│  🧠 PERSONALITY TAB
│     ├─ MBTI Badge (ENTJ, INTJ, etc.)
│     ├─ Section 6: Personality Detail
│     └─ Section 7: Myers-Briggs Assessment Summary
│
│  💬 CHAT THINGS TAB (Strategic Intelligence)
│     ├─ Pain Points for 1st Vice President (bullets)
│     ├─ SBA Financing Interest & Client Benefits (bullets)
│     └─ Key Insights (bullets)
│
│  ✉️ CONTENT TAB
│     ├─ Email Generator
│     │  ├─ 3 Generated Emails (with subjects)
│     │  └─ Copy buttons
│     ├─ Call Script Generator
│     │  ├─ 3 Call Scripts
│     │  └─ Copy buttons
│     └─ LinkedIn Message Generator
│        ├─ 2 LinkedIn Messages
│        └─ Copy buttons
│
└─────────────────────────────────────────────────────┘
```

---

### 6. **DATA FLOW - Contact Enrichment Lifecycle**

```
[1] IMPORT PHASE
├─ User triggers HubSpot import
├─ API fetches contacts from HubSpot CRM
├─ Filters: removes personal, unqualified, missing fields
├─ Stores in SQLite: enrichmentstatus = "pending"
└─ Returns: imported count, filtered count, existing count

[2] ENRICHMENT PHASE
├─ User clicks "Enrich Contact" button
├─ Frontend calls POST /api/contacts/<id>/enrich
├─ Backend:
│  ├─ Calls EnhancedPerplexityEnrichment
│  ├─ Perplexity API researches contact + company
│  ├─ Returns structured markdown (8 sections)
│  ├─ OpenAI polishes markdown
│  ├─ Parses into JSON structure
│  ├─ Stores in DB columns:
│  │  ├─ enrichmentdata (JSON)
│  │  ├─ profilecontent (full markdown)
│  │  ├─ perplexitydata (backup JSON)
│  │  └─ enrichmentstatus = "complete"
│  └─ AUTO-TRIGGERS scoring engine
└─ Returns: datasize, profilefile, scores

[3] SCORING PHASE (auto-triggered after enrichment)
├─ Calculates 3 scores: MDCP, RSS, Priority
├─ Assigns tiers: HOT/WARM/COLD
├─ Assigns urgency: IMMEDIATE/HIGH/MEDIUM
├─ Updates columns: mdcpscore, rssscore, priorityscore, etc.
└─ Returns: all score values

[4] CONTENT GENERATION PHASE
├─ User clicks "Generate All" in Content tab
├─ Frontend calls POST /api/contacts/<id>/generate-content
├─ Backend processes ONE AT A TIME for reliability:
│  ├─ Email Generator (3 emails)
│  │  ├─ GPT-4o call with contact + enrichment
│  │  ├─ Extracts subject + body
│  │  └─ Stores: email1subject, email1body
│  ├─ Call Script Generator (3 scripts)
│  │  ├─ GPT-4o call with contact + enrichment
│  │  └─ Stores: callscript1
│  └─ LinkedIn Generator (2 messages)
│     ├─ GPT-4o call with contact (shortened enrichment)
│     └─ Stores: linkedinrequest
├─ Updates: contentgeneratedat = NOW()
└─ Returns: results object with all content

[5] DISPLAY PHASE
├─ Frontend reads response from generate-content endpoint
├─ Should display:
│  ├─ Emails with subjects + bodies + copy buttons
│  ├─ Call scripts with copy buttons
│  └─ LinkedIn messages with copy buttons
└─ ⚠️ CURRENTLY NOT WORKING - data not displaying
```

---

### 7. **Environment Variables & Configuration**

**File:** `~/.env` or `.env` in project root

```env
# API Keys
HUBSPOT_ACCESS_TOKEN=<your_hubspot_token>
PERPLEXITY_API_KEY=<your_perplexity_key>
OPENAI_API_KEY=<your_openai_key>

# Database
DATABASE_URL=~/projects/apex/apex.db
# Or in code: Userschrisrabenoldprojectsapexapex.db

# Server
FLASK_PORT=8000
FLASK_DEBUG=True
REACT_PORT=3000

# Paths
BACKEND_PATH=~/projects/apex/apps/backend/
```

---

### 8. **Installation & Startup**

#### **Backend:**
```bash
cd ~/projects/apex/apps/backend

# Install Python dependencies
pip install flask flask-cors requests python-dotenv openai

# Start Flask API server
python api.py
# Runs on http://localhost:8000
```

#### **Frontend:**
```bash
cd ~/projects/apex/dashboard_v1

# Install Node dependencies
npm install

# Start React dev server
npm start
# Runs on http://localhost:3000
```

#### **Database:**
- Auto-created at `~/projects/apex/apex.db` on first run
- SQLite3 format
- Tables auto-generated with schema migrations

---

### 9. **Known Issues & TODO**

#### **CRITICAL:**
1. **Content Generation Not Displaying** (ACTIVE ISSUE)
   - Email, call script, LinkedIn content generated but not shown in modal
   - API returns data, frontend doesn't display
   - Fix needed in `ContentGenerator.tsx` or state management

#### **HIGH PRIORITY:**
2. **Company Profile Tab Truncation** (FIXED in latest update)
   - Was cutting off mid-sentence - now displays full content

3. **Dual Personality Tabs**
   - Same content shows in both Personality section of two different places

#### **MEDIUM PRIORITY:**
4. **Error Handling**
   - No retry logic for API failures
   - Missing timeout handling

5. **Performance**
   - Content generation takes 30-60 seconds per contact
   - No progress indicator

#### **LOW PRIORITY:**
6. **UI Polish**
   - Mobile responsiveness needs work
   - Dark mode toggles need refinement
   - Icon consistency across tabs

---

### 10. **API Response Examples**

#### **Enrich Contact - Response:**
```json
{
  "success": true,
  "message": "Enhanced enrichment complete with strategic intelligence",
  "contactId": 42,
  "dataSize": 8750,
  "enrichmentCount": 1,
  "lastEnriched": "2025-11-26T07:28:08",
  "scores": {
    "mdcpScore": 85,
    "mdcpTier": "HOT",
    "rssScore": 72,
    "rssTier": "WARM",
    "priorityScore": 80,
    "urgencyLevel": "IMMEDIATE"
  }
}
```

#### **Generate Content - Response:**
```json
{
  "success": true,
  "contactId": 42,
  "results": {
    "emails": [
      {
        "subject": "Real Estate Capital Markets Opportunity",
        "body": "[email body here]",
        "type": "Introduction",
        "generatedAt": "2025-11-26T07:29:15"
      }
    ],
    "callScripts": [
      {
        "script": "[call script here]",
        "type": "Cold Call",
        "generatedAt": "2025-11-26T07:29:45"
      }
    ],
    "linkedinMessages": [
      {
        "message": "[linkedin message here]",
        "type": "Connection Request",
        "generatedAt": "2025-11-26T07:30:10"
      }
    ]
  }
}
```

---

### 11. **Thread Handoff Checklist**

Before passing to next developer:

- [ ] All API endpoints tested with curl/Postman
- [ ] Database migrations verified
- [ ] HubSpot import running without errors
- [ ] Enrichment engine producing valid markdown
- [ ] Scoring calculations verified
- [ ] Content generation working (once fixed)
- [ ] Frontend displaying all contact detail tabs correctly
- [ ] All environment variables configured
- [ ] Backend and frontend running without crashes
- [ ] Error logs reviewed and understood
- [ ] Performance baseline established

---

## QUICK START FOR NEW DEV

```bash
# Terminal 1 - Backend
cd ~/projects/apex/apps/backend
python api.py

# Terminal 2 - Frontend
cd ~/projects/apex/dashboard_v1
npm start

# Terminal 3 - Testing
curl http://localhost:8000/api/health
# Should return: {"status": "healthy", ...}

# Then navigate to http://localhost:3000 in browser
```

---

**For questions about specific modules or further details, refer to individual file headers and inline comments.**

End of Comprehensive System Documentation.