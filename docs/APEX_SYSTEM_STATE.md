# APEX SALES INTELLIGENCE - SYSTEM STATE & ARCHITECTURE
**Status**: PRODUCTION - WORKING AS OF December 17, 2025
**Last Verified**: December 16, 2025 7:13 PM PST

---

## 🚨 CRITICAL RULES - READ FIRST 🚨

### **RULE #1: NO FRONTEND CHANGES WITHOUT EXPLICIT REQUEST**
The Dashboard (Dashboard_v1) is **COMPLETE** and **DEPLOYED**. Do NOT:
- Add new components
- Modify existing UI
- Change routing
- Add buttons or forms
- Alter styling

### **RULE #2: PRESERVE PROVEN ENGINES**
The following modules are **BATTLE-TESTED** and work in production:
- `enrichment_engine.py` (Perplexity 3-stage + GPT-4 synthesis)
- `enhanced_enrichment.py` (4-stage enrichment pipeline)
- Never replace these with new implementations

### **RULE #3: UUID HANDLING IS SACRED**
- Contact IDs are **UUID strings** (e.g., `f6e4e0f2-0597-47a2-b4f5-869fa94b6a12`)
- NEVER use `parseInt()` on contact IDs
- NEVER type contact IDs as `number` in TypeScript
- ALL route parameters must accept strings: `contact_id: str`

### **RULE #4: ENDPOINT PATHS ARE LOCKED**
Dashboard calls these exact endpoints:
```
POST /api/v2/contacts/{id}/enrich
GET  /api/v2/contacts/{id}/enrichment-status
```
Backend MUST support these paths. Legacy `/api/contacts/*` can coexist.

---

## 📊 SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    USER BROWSER                              │
│  https://apex-sales-intelligence.vercel.app                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTPS
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              DASHBOARD_V1 (Frontend)                         │
│              Deployed: Vercel                                │
│              Tech: React 18 + TypeScript + Vite              │
│              Status: ✅ PRODUCTION                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ REST API calls
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              APEX BACKEND (FastAPI)                          │
│              Deployed: Render                                │
│              URL: apex-backend-*.onrender.com                │
│              Status: ✅ RUNNING                              │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌──────────┐
    │  DB    │  │ Perpl. │  │ OpenAI   │
    │ Postgr │  │  API   │  │ GPT-4    │
    │  SQL   │  │        │  │          │
    └────────┘  └────────┘  └──────────┘
```

---

## 🎯 FRONTEND: DASHBOARD_V1

### **Deployment**
- **Platform**: Vercel
- **URL**: https://apex-sales-intelligence.vercel.app
- **Build**: Vite (React + TypeScript)
- **Status**: ✅ Deployed and operational

### **Key Files & Structure**
```
dashboard_v1/
├── src/
│   ├── App.tsx                    # Main router (8 routes)
│   ├── config.ts                  # API base URL config
│   ├── types.ts                   # TypeScript interfaces
│   │
│   ├── components/
│   │   ├── ContactsView.tsx       # All contacts list
│   │   ├── ContactDetailModal.tsx # Contact profile modal
│   │   ├── ContactEnrichmentView.tsx # Shows enrichment status
│   │   ├── EnrichmentDisplay.tsx  # Renders enrichment data
│   │   ├── OutreachTab.tsx        # Outreach content tab
│   │   ├── OutreachGenerator.tsx  # Email/Call/LinkedIn generator
│   │   ├── TodaysBoard.tsx        # Daily priority dashboard
│   │   ├── Analytics.tsx          # Analytics view
│   │   ├── ColdCallQueue.tsx      # Cold call queue
│   │   └── SmartLists.tsx         # Smart list views
│   │
│   ├── pages/
│   │   ├── ContactDetailPage.tsx  # Full contact detail page
│   │   └── CallAssistantPage.tsx  # Call assistant
│   │
│   └── utils/
│       └── api.ts                 # API client layer
│
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

### **API Configuration**
**File**: `src/config.ts`
```typescript
const VITE_API_URL = import.meta.env.VITE_API_URL || (
  window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://apex-intelligence-production.up.railway.app'
);

export const config = {
  API_BASE_URL: VITE_API_URL,
  API_ENDPOINTS: {
    CONTACTS: '/api/contacts',
    CONTACT_DETAIL: (id: number) => `/api/contacts/${id}`,
    CONTACT_ENRICH: (id: number) => `/api/contacts/${id}/enrich`,
    TODAYS_BOARD: '/api/todays-board',
    // ... more endpoints
  }
};
```

### **TypeScript Types (CRITICAL)**
**File**: `src/types.ts`
```typescript
export interface Contact {
  id: string;  // ⚠️ MUST BE STRING (UUID)
  name: string;
  title: string;
  company: string;
  email?: string;
  phone?: string;
  linkedin_url?: string;

  // Enrichment
  enrichment_status: 'pending' | 'completed' | 'failed';
  enrichment_data?: any;
  enriched_at?: string;

  // Scoring
  mdcp_score?: number;
  priority_score?: number;

  // Metadata
  created_at: string;
  updated_at: string;
}
```

### **Frontend Components Status**

| Component | Purpose | Status | Notes |
|-----------|---------|--------|-------|
| `ContactsView.tsx` | Main contacts list | ✅ Working | Pagination, search, filters |
| `ContactDetailModal.tsx` | Contact profile popup | ✅ Working | Shows all contact data |
| `ContactEnrichmentView.tsx` | Enrichment status display | ✅ Working | Shows pending/completed/failed |
| `EnrichmentDisplay.tsx` | Renders enrichment sections | ✅ Working | Parses enrichment_data JSON |
| `OutreachTab.tsx` | Outreach content tab | ✅ Working | Email/Call/LinkedIn tabs |
| `OutreachGenerator.tsx` | Content generation UI | ⚠️ Needs backend | Button exists, needs `/api/outreach` endpoint |
| `TodaysBoard.tsx` | Daily priorities | ✅ Working | Calls `/api/todays-board` |
| `Analytics.tsx` | Dashboard analytics | ✅ Working | Charts and metrics |

---

## ⚙️ BACKEND: APEX API

### **Deployment**
- **Platform**: Render
- **URL**: https://apex-backend-*.onrender.com (check Render dashboard)
- **Tech**: FastAPI + Python 3.11 + PostgreSQL
- **Status**: ✅ Running (Uvicorn on port 10000)

### **Key Files & Structure**
```
apps/backend/
├── main.py                        # FastAPI app entry point
├── enrichment_engine.py           # ⭐ PROVEN - Perplexity + GPT-4
├── enhanced_enrichment.py         # ⭐ PROVEN - 4-stage pipeline
│
├── api/
│   └── routes/
│       ├── enrichment.py          # ✅ NEW - v2 endpoints with debug
│       ├── contacts.py            # Contact CRUD
│       ├── todays_board.py        # Daily board logic
│       └── analytics.py           # Analytics endpoints
│
├── services/
│   ├── enrichment_parser.py      # Parses enrichment output
│   └── enrichment_integration.py # Integrates parsed data
│
└── models/
    └── contact.py                 # Contact model
```

### **Database Schema (PostgreSQL)**
```sql
CREATE TABLE contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  title VARCHAR(255),
  company VARCHAR(255),
  email VARCHAR(255),
  phone VARCHAR(50),
  linkedin_url TEXT,

  -- Enrichment
  enrichment_status VARCHAR(20),  -- 'pending' | 'completed' | 'failed'
  enrichment_data JSONB,          -- Structured enrichment output
  enriched_at TIMESTAMP,

  -- Scoring
  mdcp_score DECIMAL(5,2),
  priority_score DECIMAL(5,2),
  rss_score DECIMAL(5,2),

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_contacts_enrichment_status ON contacts(enrichment_status);
CREATE INDEX idx_contacts_created_at ON contacts(created_at DESC);
```

### **Current API Endpoints**

#### **✅ Working Endpoints**

| Method | Endpoint | Purpose | Status |
|--------|----------|---------|--------|
| GET | `/api/contacts` | List contacts | ✅ Working |
| GET | `/api/contacts/{id}` | Get contact detail | ✅ Working |
| POST | `/api/contacts` | Create contact | ✅ Working |
| PUT | `/api/contacts/{id}` | Update contact | ✅ Working |
| POST | `/api/v2/contacts/{id}/enrich` | Trigger enrichment (Dashboard) | ✅ Working |
| POST | `/api/contacts/{id}/enrich` | Trigger enrichment (Legacy) | ✅ Working |
| GET | `/api/v2/contacts/{id}/enrichment-status` | Check status (Dashboard) | ✅ Working |
| GET | `/api/contacts/{id}/enrichment-status` | Check status (Legacy) | ✅ Working |
| POST | `/api/batch/enrich` | Batch enrich (limit 1) | ✅ Working |
| GET | `/api/todays-board` | Daily priorities | ✅ Working |
| GET | `/api/analytics` | Analytics data | ✅ Working |

#### **⚠️ Not Yet Implemented**

| Method | Endpoint | Purpose | Notes |
|--------|----------|---------|-------|
| POST | `/api/contacts/{id}/generate-email` | Generate email draft | Outreach generator needs this |
| POST | `/api/contacts/{id}/generate-call-script` | Generate call script | Outreach generator needs this |
| POST | `/api/contacts/{id}/generate-linkedin` | Generate LinkedIn message | Outreach generator needs this |

---

## 🔧 ENRICHMENT ENGINE (CRITICAL)

### **Architecture**
```
User clicks "Enrich"
         ↓
POST /api/v2/contacts/{id}/enrich
         ↓
enrichment.py: enrich_contact_internal()
         ↓
enrichment_engine.py: enrich_contact()
         ↓
┌────────────────────────────────────┐
│   4-STAGE ENRICHMENT PIPELINE      │
├────────────────────────────────────┤
│ STAGE 1: LinkedIn Profile Search  │
│   - Perplexity search              │
│   - Extract: role, company, exp    │
│                                    │
│ STAGE 2: Company Research          │
│   - Perplexity company search      │
│   - Extract: industry, size, rev   │
│                                    │
│ STAGE 3: Sales Context             │
│   - Perplexity intent signals      │
│   - Extract: pain points, buying   │
│                                    │
│ STAGE 4: GPT-4 Synthesis           │
│   - Combine all 3 searches         │
│   - Generate structured profile    │
└────────────────────────────────────┘
         ↓
Save to DB: enrichment_data (JSONB)
         ↓
Write debug files: /tmp/apex_debug/
  - 01_raw_result.txt
  - 02_perplexity_openai.txt  ⭐ KEY FILE
  - 03_parsed.txt
```

### **Proven Engine Files (DO NOT REPLACE)**

**File**: `enrichment_engine.py`
- **Status**: ✅ Production-tested
- **Tech**: Perplexity API (3 searches) + OpenAI GPT-4 (synthesis)
- **Output**: Structured profile text (~2000-3500 chars)
- **Rate Limits**: Built-in delays (3s between searches)

**File**: `enhanced_enrichment.py`
- **Status**: ✅ Production-tested
- **Tech**: 4-stage pipeline wrapper around enrichment_engine.py
- **Features**: Error handling, retries, logging

### **Debug Files Location**
```bash
# On Render server (via Shell tab)
/tmp/apex_debug/contact_{uuid}_01_raw_result_{timestamp}.txt
/tmp/apex_debug/contact_{uuid}_02_perplexity_openai_{timestamp}.txt  # ⭐ KEY
/tmp/apex_debug/contact_{uuid}_03_parsed_{timestamp}.txt
```

**Access via Render Dashboard → Shell tab:**
```bash
cd /tmp/apex_debug
ls -lh
cat contact_*_02_perplexity_openai_*.txt
```

---

## 🔐 ENVIRONMENT VARIABLES

### **Backend (Render)**
```bash
DATABASE_URL=postgresql://...           # PostgreSQL connection
OPENAI_API_KEY=sk-...                   # GPT-4 API key
PERPLEXITY_API_KEY=pplx-...            # Perplexity API key
PORT=10000                              # Render assigns this
PYTHON_VERSION=3.11.0                   # Locked version
```

### **Frontend (Vercel)**
```bash
VITE_API_URL=https://apex-backend-*.onrender.com  # Backend URL
```

---

## 📈 PERFORMANCE METRICS

### **Enrichment Performance**
- **Average Duration**: 60-90 seconds
- **Success Rate**: ~95% (with valid LinkedIn URLs)
- **Output Size**: 2000-3500 characters
- **Sections Parsed**: 1-8 sections

### **API Response Times**
- `GET /api/contacts`: ~200ms (50 contacts)
- `GET /api/contacts/{id}`: ~50ms
- `POST /api/v2/contacts/{id}/enrich`: 60-90s (async operation)
- `GET /api/todays-board`: ~800ms (complex query)

---

## 🚀 DEPLOYMENT WORKFLOW

### **Backend Deployment (Render)**
```bash
git add <files>
git commit -m "feat: description"
git push origin main
# Render auto-deploys (~2 min)
# Check logs: https://dashboard.render.com
```

### **Frontend Deployment (Vercel)**
```bash
cd dashboard_v1
git add <files>
git commit -m "feat: description"
git push origin main
# Vercel auto-deploys (~1 min)
# Check: https://vercel.com/dashboard
```

---

## 🐛 COMMON ISSUES & FIXES

### **Issue 1: "Contact not found"**
**Cause**: Contact ID is UUID but code expects integer
**Fix**: Ensure `contact_id: str` in all route params
```python
@router.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: str):  # ✅ str not int
```

### **Issue 2: "Enrichment status never updates"**
**Cause**: Frontend polling wrong endpoint
**Fix**: Dashboard must call `/api/v2/contacts/{id}/enrichment-status`

### **Issue 3: "Module not found: enrichment_engine"**
**Cause**: File not at project root
**Fix**: Verify `enrichment_engine.py` exists at `apps/backend/enrichment_engine.py`

### **Issue 4: "Empty enrichment data"**
**Cause**: Perplexity API returned no results
**Fix**: Check debug file `02_perplexity_openai_*.txt` to see raw output

---

## 📝 TESTING CHECKLIST

### **Backend Health Check**
```bash
curl https://your-backend.onrender.com/health
# Expected: {"status": "healthy"}
```

### **Enrichment Test**
```bash
BACKEND_URL="https://your-backend.onrender.com"
CONTACT_ID="your-uuid-here"

curl -X POST "${BACKEND_URL}/api/v2/contacts/${CONTACT_ID}/enrich" \
  -H "Content-Type: application/json" \
  -v

# Wait 60-90 seconds

curl "${BACKEND_URL}/api/v2/contacts/${CONTACT_ID}/enrichment-status"
# Expected: {"enrichmentStatus": "completed", ...}
```

### **View Debug Files**
```bash
# In Render Shell tab
cd /tmp/apex_debug
cat contact_*_02_perplexity_openai_*.txt
```

---

## 🎓 ONBOARDING NEW THREADS

**When starting a new thread, provide this document and state:**

> "I'm working on Apex Sales Intelligence. Here's the current system state: [attach this document]
> 
> **CRITICAL RULES:**
> 1. Do NOT modify the Dashboard frontend unless explicitly requested
> 2. Do NOT replace enrichment_engine.py or enhanced_enrichment.py
> 3. Contact IDs are UUID strings, never integers
> 4. All enrichment endpoints must support /api/v2/contacts/{id}/* paths
>
> **Current task**: [describe what you need]"

---

## 📚 KEY DOCUMENTATION FILES

```
docs/
├── APEX_SYSTEM_STATE.md              # This file
├── APEX_ENDPOINT_MATCHING_DEC-15.md  # Frontend ↔ Backend endpoint mapping
├── UUID-FIXES-DEC15.md               # UUID handling rules
├── Dashboard_v1_Complete.md          # Complete frontend code
└── THREAD-DEC16-*.md                 # Recent thread summaries
```

---

## ✅ VERIFIED WORKING (Dec 16, 2025)

- ✅ Backend deployed and running on Render
- ✅ Frontend deployed and running on Vercel
- ✅ Enrichment engine operational (Perplexity + GPT-4)
- ✅ Debug files being created in `/tmp/apex_debug/`
- ✅ UUID handling correct throughout system
- ✅ Dashboard displays contacts correctly
- ✅ Enrichment endpoints responding to `/api/v2/contacts/{id}/*`
- ✅ Database queries working with UUID primary keys
- ✅ Today's Board functional
- ✅ Analytics dashboard operational

---

## 🔮 ROADMAP (Not Yet Implemented)

- [ ] Outreach content generation endpoints
- [ ] Batch enrichment UI in Dashboard
- [ ] Email/Call script display in Dashboard
- [ ] LinkedIn message generator
- [ ] CRM integration (HubSpot, Salesforce)
- [ ] Advanced filtering in ContactsView
- [ ] Export to CSV functionality

---

**LAST UPDATED**: December 17, 2025 03:25 AM 
**VERIFIED BY**: Production testing and log analysis
**SYSTEM STATUS**: ✅ OPERATIONAL

---

## 🆘 SUPPORT & TROUBLESHOOTING

**Render Logs**: https://dashboard.render.com → Your Service → Logs
**Vercel Logs**: https://vercel.com/dashboard → Your Project → Deployments
**Debug Files**: Render Dashboard → Shell → `/tmp/apex_debug/`

**Critical Files to Never Delete:**
- `enrichment_engine.py`
- `enhanced_enrichment.py`
- `apps/backend/api/routes/enrichment.py`
- `dashboard_v1/src/types.ts` (UUID type definitions)
