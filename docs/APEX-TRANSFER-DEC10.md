# Apex Sales Intelligence – Transfer Document
**Date:** December 10, 2025  
**Status:** Production Live | 500 HubSpot Contacts Synced  
**Backend:** Render (https://apex-backend-i7b0.onrender.com)  
**Frontend:** Dashboard_v1 (local dev)

---

## Executive Summary

Apex is a **production-ready sales intelligence system** with three clean layers:

1. **Backend (Apex):** FastAPI + SQLite database on Render
2. **Enrichment Engine:** Your existing 3-stage multi-search (untouched, working)
3. **Frontend (Dashboard_v1):** React + TypeScript rendering contacts and enrichment data

**Current Status:**
- ✅ Clean SQLite schema in `apex.db` (contacts + enrichment tables)
- ✅ 500 HubSpot contacts synced with filters (email, company, name required)
- ✅ Enrichment adapter wired to your existing `enhanced_enrichment.py`
- ✅ v2 API endpoints live (`/api/v2/contacts/*`)
- ⏳ Frontend needs wiring to use new API (not HubSpot directly anymore)

---

## Database Architecture

### Location
```
apps/backend/apex.db
```

### Schema

#### `contacts` table
```sql
CREATE TABLE contacts (
    id TEXT PRIMARY KEY,
    hubspot_id TEXT UNIQUE,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    title TEXT,
    company TEXT,
    enrichment JSON,           -- Stores enrichment data
    enriched_at TIMESTAMP,     -- When enrichment was last run
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Key Fields:**
- `id`: UUID (generated on create)
- `hubspot_id`: Links back to HubSpot for sync updates
- `enrichment`: JSON blob with structure:
  ```json
  {
    "version": "1.0",
    "raw_profile": "Ed Colunga's publicly visible...",  // 20K+ chars from enhanced_enrichment
    "character_count": 20480
  }
  ```
- `enriched_at`: Timestamp when last enriched (allows bulk re-enrichment)

#### `enrichment_history` table (optional, not yet created)
Could store multiple enrichment runs per contact for audit trail.

### Backup & Safety
- `apex.db.backup.20251210_152658` created before schema migrations
- All historical data preserved; migrations are additive only

---

## Backend Architecture

### Root Directory
```
apps/backend/
```

### Key Files & Their Roles

#### **1. Core Application**

**`main.py`** (1,738 lines)
- **What it does:** FastAPI application entry point
- **Key components:**
  - CORS configuration (allows Dashboard_v1 to call backend)
  - Database connection pooling
  - Route registration (v1 legacy + v2 new)
  - Enrichment engine initialization (if available)
- **Status:** ✅ Live on Render
- **Note:** Routes are registered at line 53 with:
  ```python
  from api.routes.contacts_v2 import router as contacts_v2_router
  app.include_router(contacts_v2_router)
  ```

#### **2. Database & Schema**

**`services/contact_service.py`** (CRUD operations)
- **What it does:** All database operations for contacts table
- **Key methods:**
  - `create_contact()` – Insert new contact
  - `get_contact(id)` – Fetch single contact with enrichment
  - `get_all_contacts(limit, offset)` – List with pagination
  - `get_contact_by_hubspot_id(hubspot_id)` – Check for duplicates during sync
  - `save_enrichment(contact_id, enrichment_data)` – Save enrichment JSON
  - `get_stats()` – Returns {total, enriched, pending}
  - `update_contact(id, **kwargs)` – Update fields
- **Database:** Directly opens `apex.db` using SQLite3
- **Status:** ✅ Stable
- **Change this to:** Never (stable interface)

**`schemas/enrichment_schema.py`** (Pydantic models)
- **What it does:** Defines expected enrichment data structure (for reference, not strict validation yet)
- **Models:**
  - `EnrichmentData` – Expected shape of enrichment JSON
  - Sub-models for sales, personality, company, etc.
- **Status:** ✅ Reference only (frontend parses raw_profile text)
- **Future:** Convert `raw_profile` → structured JSON using this schema

**`schemas/migrate_db.py`**
- **What it does:** Creates the `contacts` and `enrichment_history` tables
- **Run:** `python schemas/migrate_db.py` (only needed once, already run)
- **Status:** ✅ Complete

#### **3. Enrichment Pipeline**

**`services/enrichment_adapter.py`** (Glue layer)
- **What it does:** Bridges v2 API → your existing enrichment engine
- **Key method:**
  ```python
  enrich_and_save(contact_id: str) -> Dict
  ```
  1. Fetches contact from `apex.db`
  2. Calls your existing `EnhancedEnrichment` (3-stage multi-search)
  3. Saves raw_profile to `contacts.enrichment` JSON
- **Calls:** `intelligence/engines/enrichment/enhanced_enrichment.py` (your code, untouched)
- **Status:** ✅ Tested and working
- **Critical rule:** Never modify this flow; only call it via API

**`intelligence/engines/enrichment/enhanced_enrichment.py`** (Your enrichment engine)
- **What it does:** 3-stage multi-search strategy
  - Stage 1: LinkedIn/Person search
  - Stage 2: Company/News search
  - Stage 3: Combined person+company context
  - Stage 4: Generate profile (8000+ chars)
- **APIs used:** Perplexity AI (multi-search with open-ended questions)
- **Output:** `{success: bool, profile_text: str, character_count: int}`
- **Status:** ✅ Golden – Do NOT touch
- **Environment vars:** `PERPLEXITY_API_KEY` required

#### **4. HubSpot Integration**

**`services/hubspot_service.py`** (Legacy, still exists)
- **What it does:** Maps HubSpot properties to contact fields
- **Status:** ⏳ Superseded by v2 but kept for reference

**`services/hubspot_sync_v2.py`** (New, production)
- **What it does:** Sync HubSpot contacts to `apex.db` with filters
- **Key method:**
  ```python
  sync_hubspot_contacts(limit=100, apply_filters=True) -> Dict
  ```
- **Filters applied:**
  - Must have: email, company, name
  - Exclude: `hs_lead_status == "unqualified"`
  - Exclude lifecycle: unsubscribe, customer, evangelist
- **Pagination:** Handles HubSpot's 100-contact-per-request limit; auto-pages for 500+ contacts
- **Deduplication:** Checks `hubspot_id` to avoid duplicates on re-sync
- **Status:** ✅ Live and tested (500 contacts synced)
- **Environment vars:** `HUBSPOT_API_KEY` required (set in Render dashboard)

**`intelligence/hubspot_sync.py`** (Legacy, still exists)
- **What it does:** Older sync logic (pre-v2)
- **Status:** ⏳ Superseded, kept for reference only

#### **5. API Routes**

**`api/routes/contacts_v2.py`** (New v2 API)
- **What it does:** FastAPI router with all v2 endpoints
- **Endpoints:**
  - `GET /api/v2/contacts` – List all contacts (paginated)
  - `GET /api/v2/contacts/stats` – Returns {total, enriched, pending}
  - `GET /api/v2/contacts/{id}` – Fetch single contact + enrichment
  - `POST /api/v2/contacts` – Create contact manually
  - `POST /api/v2/contacts/{id}/enrich` – Run enrichment on single contact
  - `POST /api/v2/contacts/bulk-enrich` – Run enrichment on multiple contacts
  - `POST /api/v2/contacts/sync/hubspot` – Sync from HubSpot (with filters)
  - `POST /api/v2/contacts/import/csv` – Import from CSV file
- **Status:** ✅ Live on Render
- **Response format:**
  ```json
  {
    "id": "38efdb4b-64b2-464b-a537-53f5d07d093d",
    "first_name": "Ed",
    "last_name": "Colunga",
    "company": "SunWest Bank",
    "enrichment": {
      "version": "1.0",
      "raw_profile": "Ed Colunga's publicly visible...",
      "character_count": 20480
    },
    "enriched_at": "2025-12-10T23:50:47.321295"
  }
  ```

#### **6. Configuration & Dependencies**

**`requirements.txt`**
- Key packages:
  - `fastapi` – Web framework
  - `uvicorn` – ASGI server
  - `pydantic` – Data validation
  - `psycopg2-binary` – PostgreSQL (legacy, not used in v2)
  - `hubspot-api-client` – HubSpot SDK
  - `openai` – OpenAI for enrichment
  - `python-multipart` – For CSV file uploads
  - `requests`, `python-dotenv`, etc.
- **Status:** ✅ All installed on Render

**`.env` (local)**
```
OPENAI_API_KEY=sk-proj-...
PERPLEXITY_API_KEY=pplx-...
HUBSPOT_API_KEY=pat-na2-...
DATABASE_URL=... (for legacy v1, not used in v2)
```

**Render Environment Variables**
Set in Render dashboard under "Environment":
- `HUBSPOT_API_KEY` – Required for sync endpoint
- `PERPLEXITY_API_KEY` – Required for enrichment
- `OPENAI_API_KEY` – Required for enrichment

---

## Frontend Architecture

### Root Directory
```
dashboard_v1/src/
```

### Key Files & Their Roles

#### **1. Entry Point**

**`App.tsx`**
- **What it does:** Main application shell, routing, layout
- **Routes:**
  - `/contacts` → `ContactsPage`
  - `/contacts/:id` → `ContactDetailPage`
- **Status:** ✅ Basic structure in place
- **Need to do:** Update to call new Apex API instead of HubSpot directly

#### **2. Pages**

**`pages/ContactDetailPage.tsx`** (New, Apex-specific)
- **What it does:** Single contact detail + enrichment display
- **Features:**
  - Displays contact info (name, email, company, title)
  - Parses enrichment `raw_profile` text using markdown patterns
  - Renders 20+ enrichment cards (Person, Company, Sales, Personality, etc.)
  - Fallback: If parsing fails or data is fragmented, shows cleaned raw text
- **Data source:** Currently reads from HubSpot; **NEEDS TO BE UPDATED** to call `/api/v2/contacts/{id}`
- **Status:** ✅ Rendering logic works, but wired to wrong API
- **Lines of code:** 850+
- **Key function:** `extractSection(title, delimiter)` – Parses markdown headers

**`pages/ContactsPage.tsx`**
- **What it does:** List of contacts with filters, search, enrichment status
- **Features:**
  - Table/grid view of all contacts
  - Filter by enrichment status (enriched, pending, failed)
  - Search by name/email/company
  - Bulk actions: enrich, export, etc.
- **Data source:** Currently reads from HubSpot; **NEEDS TO BE UPDATED** to call `/api/v2/contacts`
- **Status:** ⏳ Needs API wiring
- **Key function:** `fetchContacts()` – Should hit `/api/v2/contacts?limit=50&offset=0`

#### **3. Components** (Reusable)

**`components/ContactsView.tsx`**
- **What it does:** Contact list renderer
- **Status:** ✅ Used by ContactsPage

**`components/ContactDetail.tsx`** (Legacy)
- **What it does:** Old contact detail component
- **Status:** ⏳ Superseded by ContactDetailPage.tsx

**`components/ContactEnrichmentView.tsx`** (Legacy)
- **What it does:** Old enrichment display
- **Status:** ⏳ Superseded by enrichment cards in ContactDetailPage.tsx

#### **4. Utilities & Configuration**

**`config/api.ts`** (NEW – Created in this thread)
- **What it does:** Centralized API configuration
- **Current content:**
  ```typescript
  const API_BASE_URL = 'https://apex-backend-i7b0.onrender.com';
  export const API_ENDPOINTS = {
    contacts: `${API_BASE_URL}/api/v2/contacts`,
    stats: `${API_BASE_URL}/api/v2/contacts/stats`,
    enrich: (id) => `${API_BASE_URL}/api/v2/contacts/${id}/enrich`,
    bulkEnrich: `${API_BASE_URL}/api/v2/contacts/bulk-enrich`,
  };
  ```
- **Status:** ✅ Created, not yet used by pages

**`utils/enrichmentParser.ts`**
- **What it does:** Parses enrichment `raw_profile` text into structured data
- **Key functions:**
  - `extractSection(text, header)` – Find markdown section by header
  - `parseEnrichmentProfile(text)` – Break into Person/Company/Sales/Personality
- **Status:** ⏳ Exists but could be improved
- **Note:** Regex-based parsing; fragile if enrichment format changes

**`types/EnrichmentSchema.ts`**
- **What it does:** TypeScript interfaces matching backend enrichment schema
- **Status:** ✅ Reference only

#### **5. Build & Dependencies**

**`package.json`**
- Key packages: React, TypeScript, Vite, Axios, etc.
- **Status:** ✅ All installed locally

**`.env.local` (local development)**
```
VITE_API_URL=http://localhost:8000  # For local backend
# or
VITE_API_URL=https://apex-backend-i7b0.onrender.com  # For production
```

---

## What Changed This Thread

### Backend Changes

1. **Created `services/contact_service.py`**
   - Clean CRUD for `apex.db` contacts table
   - Replaces direct database access scattered in main.py

2. **Created `services/enrichment_adapter.py`**
   - Bridges API → your existing enrichment engine
   - Ensures no changes to `enhanced_enrichment.py`

3. **Created `services/hubspot_sync_v2.py`**
   - Production HubSpot sync with pagination + filters
   - Successfully synced 500 contacts

4. **Created `api/routes/contacts_v2.py`**
   - New v2 API endpoints for all CRUD operations
   - Wired to contact_service.py (not direct DB access)

5. **Updated `main.py`**
   - Registered v2 router at line 53 (before `if __name__`)
   - Moved HubSpot key setup to Render environment variables

6. **Created `schemas/` package**
   - `enrichment_schema.py` – Pydantic models for future validation
   - `migrate_db.py` – Schema creation script

7. **Added `python-multipart` to requirements.txt**
   - Needed for CSV file upload endpoint

8. **Added `__init__.py` files**
   - `api/__init__.py`, `api/routes/__init__.py`, `services/__init__.py`, `schemas/__init__.py`
   - Allows Python to import from these packages

### Frontend Changes

1. **Created `config/api.ts`**
   - Centralized API endpoint configuration
   - Points to Render backend

2. **Updated `ContactDetailPage.tsx`**
   - Added fallback rendering for enrichment data
   - Fixed markdown parsing edge cases
   - **Still needs wiring:** Should fetch from `/api/v2/contacts/{id}` instead of HubSpot

3. **Created `types/EnrichmentSchema.ts`**
   - TS interfaces for enrichment data shape

### Database Changes

1. **Created `apex.db`**
   - Clean SQLite database with `contacts` table
   - Schema: id, hubspot_id, first_name, last_name, email, phone, title, company, enrichment (JSON), enriched_at, created_at, updated_at

2. **Ed Colunga enriched**
   - Test contact with 20,480 character enrichment profile
   - Stored in database as proof of concept

3. **500 HubSpot contacts synced**
   - Filtered: email, company, name required
   - Excluded: unqualified lead_status, unsubscribe/customer/evangelist lifecycle
   - 48 skipped due to missing required fields
   - 500 successfully imported

---

## What We Need to Do Next

### Priority 1: Frontend API Wiring (CRITICAL)

**File:** `dashboard_v1/src/pages/ContactsPage.tsx`
- Replace HubSpot API calls with:
  ```typescript
  const response = await fetch('https://apex-backend-i7b0.onrender.com/api/v2/contacts?limit=50');
  const contacts = await response.json();
  ```
- Wire enrichment status detection to `contact.enriched_at` field

**File:** `dashboard_v1/src/pages/ContactDetailPage.tsx`
- Replace HubSpot contact fetch with:
  ```typescript
  const response = await fetch(`https://apex-backend-i7b0.onrender.com/api/v2/contacts/${contactId}`);
  const contact = await response.json();
  ```
- Use `contact.enrichment.raw_profile` as data source

**Deliverable:** Dashboard_v1 should read from Apex backend, not HubSpot

---

### Priority 2: Enrichment UI Integration

**File:** `dashboard_v1/src/pages/ContactDetailPage.tsx`
- Add "Enrich Now" button that calls:
  ```typescript
  POST /api/v2/contacts/{id}/enrich
  ```
- Show enrichment loading state
- Display enrichment timestamp (`enriched_at`)

**File:** `dashboard_v1/src/pages/ContactsPage.tsx`
- Add "Bulk Enrich" button:
  ```typescript
  POST /api/v2/contacts/bulk-enrich?limit=50
  ```
- Show progress (X of Y contacts enriched)

**Deliverable:** Users can trigger enrichment from dashboard UI

---

### Priority 3: CSV Import UI

**File:** `dashboard_v1/src/pages/ContactsPage.tsx` (or new ImportModal)
- Add file upload for CSV
- Call endpoint:
  ```typescript
  POST /api/v2/contacts/import/csv
  Content-Type: multipart/form-data
  ```
- Show success/error messages

**Deliverable:** Users can import contacts from CSV without command line

---

### Priority 4: Enrichment Schema Refinement (OPTIONAL)

**Currently:** Enrichment stored as `raw_profile` text (20K+ chars)

**Future:** Parse `raw_profile` → structured JSON matching `EnrichmentSchema`
- Pros: Easier to query, filter, and display specific fields
- Cons: Requires parsing logic, schema must stay stable

**Optional for now – raw_profile works fine for MVP**

---

### Priority 5: Deployment & Scaling

**Local Dev:**
```bash
# Terminal 1: Backend
cd apps/backend
export HUBSPOT_API_KEY=... PERPLEXITY_API_KEY=... OPENAI_API_KEY=...
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd dashboard_v1
npm run dev  # Vite dev server on port 5173
```

**Production:**
- Backend: Already on Render (auto-deploys from GitHub)
- Frontend: Can deploy to Vercel, Netlify, or Render
- Environment variables: Set in each platform's dashboard

**Deliverable:** Dashboard_v1 deployed and calling Render backend

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    APEX SALES INTELLIGENCE v2.0                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   FRONTEND (Dashboard_v1)                     │
│                     React + TypeScript                        │
│                                                                │
│  ContactsPage.tsx ──┐                                         │
│  ContactDetailPage  │──→ API Calls ──→ http://...             │
│  ContactsView.tsx   │                                         │
│                                                                │
│  Endpoints Used:                                              │
│  - GET /api/v2/contacts                                       │
│  - GET /api/v2/contacts/{id}                                  │
│  - POST /api/v2/contacts/{id}/enrich                          │
│  - POST /api/v2/contacts/bulk-enrich                          │
└──────────────────────────────────────────────────────────────┘
                              ↓
                    Network (HTTPS)
                              ↓
┌──────────────────────────────────────────────────────────────┐
│                 BACKEND (Apex) – Render.com                   │
│                    FastAPI + Python                           │
│                                                                │
│  main.py ────────────────────────────────────────────────┐   │
│  (FastAPI app, CORS, router registration)               │   │
│                                                            │   │
│  ├─ api/routes/contacts_v2.py (API endpoints)            │   │
│  │  ├─ GET /api/v2/contacts                              │   │
│  │  ├─ POST /api/v2/contacts/{id}/enrich                 │   │
│  │  ├─ POST /api/v2/contacts/sync/hubspot                │   │
│  │  └─ ...                                               │   │
│  │                                                         │   │
│  ├─ services/contact_service.py (CRUD)                   │   │
│  │  ├─ create_contact()                                  │   │
│  │  ├─ get_contact()                                     │   │
│  │  ├─ save_enrichment()                                 │   │
│  │  └─ ...                                               │   │
│  │                                                         │   │
│  ├─ services/enrichment_adapter.py (Glue)                │   │
│  │  └─ enrich_and_save(contact_id)                       │   │
│  │     └─ Calls intelligence/engines/enrichment/         │   │
│  │        enhanced_enrichment.py (YOUR CODE)             │   │
│  │                                                         │   │
│  └─ services/hubspot_sync_v2.py (Sync)                   │   │
│     └─ sync_hubspot_contacts(limit, filters)             │   │
└──────────────────────────────────────────────────────────┘   │
         │                                  │                    │
         ↓                                  ↓                    │
┌──────────────────┐            ┌──────────────────────┐        │
│   apex.db        │            │  HubSpot API         │        │
│   (SQLite)       │            │  (Read-only sync)    │        │
│                  │            │                      │        │
│  contacts table: │            │  500+ contacts       │        │
│  - id            │            │  with filters        │        │
│  - hubspot_id    │            │                      │        │
│  - name, email   │            │  Synced via:         │        │
│  - company       │            │  POST .../sync/      │        │
│  - enrichment    │            │  hubspot             │        │
│    (JSON)        │            │                      │        │
│  - enriched_at   │            │                      │        │
└──────────────────┘            └──────────────────────┘        │
                                                                  │
         │ ← Save enriched data                                  │
         │                                                       │
         └─→ Enhanced Enrichment Engine                         │
             (3-stage multi-search)                             │
             Uses: Perplexity API, OpenAI                       │
             Output: 20K+ char profile_text                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Key Files Reference

### Backend
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `main.py` | 1,738 | FastAPI entry point | ✅ Live |
| `api/routes/contacts_v2.py` | 200+ | v2 REST API | ✅ Live |
| `services/contact_service.py` | 150+ | CRUD + stats | ✅ Stable |
| `services/enrichment_adapter.py` | 80 | Enrichment glue | ✅ Working |
| `services/hubspot_sync_v2.py` | 120 | HubSpot sync | ✅ Tested |
| `intelligence/engines/enrichment/enhanced_enrichment.py` | 400+ | 3-stage enrichment | ✅ Golden |
| `schemas/enrichment_schema.py` | 100+ | Pydantic models | ✅ Reference |

### Frontend
| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `App.tsx` | 50+ | Router + shell | ✅ Basic |
| `pages/ContactDetailPage.tsx` | 850+ | Single contact detail | ⏳ API wiring needed |
| `pages/ContactsPage.tsx` | 300+ | Contact list | ⏳ API wiring needed |
| `config/api.ts` | 10 | API config | ✅ Created |
| `utils/enrichmentParser.ts` | 200+ | Text parsing | ✅ Working |
| `types/EnrichmentSchema.ts` | 50+ | TS interfaces | ✅ Reference |

### Database
| File | Size | Purpose | Status |
|------|------|---------|--------|
| `apex.db` | ~2 MB | SQLite database | ✅ Live (500 contacts) |
| `schemas/migrate_db.py` | 100 | Schema creation | ✅ Run once |

---

## Deployment Checklist

### Backend (Already Done ✅)
- [x] Create `apex.db` with clean schema
- [x] Build v2 API with contact_service, enrichment_adapter, hubspot_sync
- [x] Deploy to Render with `main.py`
- [x] Set HUBSPOT_API_KEY in Render environment
- [x] Sync 500 HubSpot contacts
- [x] Test enrichment on Ed Colunga

### Frontend (TODO)
- [ ] Update ContactsPage.tsx to call `/api/v2/contacts` instead of HubSpot
- [ ] Update ContactDetailPage.tsx to call `/api/v2/contacts/{id}` instead of HubSpot
- [ ] Add "Enrich Now" and "Bulk Enrich" buttons
- [ ] Test locally with backend
- [ ] Deploy to Vercel/Netlify/Render
- [ ] Verify end-to-end flow: Dashboard → Enrich → Display

### Database (Already Done ✅)
- [x] Created `apex.db` with contacts table
- [x] Added enrichment JSON field
- [x] Synced 500 HubSpot contacts
- [x] Verified enrichment save (Ed Colunga)

---

## Environment Variables Needed

### Local Development (`.env` in apps/backend)
```
OPENAI_API_KEY=sk-proj-...
PERPLEXITY_API_KEY=pplx-...
HUBSPOT_API_KEY=pat-na2-...
```

### Render Production (Set in Render Dashboard)
```
HUBSPOT_API_KEY=pat-na2-...
PERPLEXITY_API_KEY=pplx-...
OPENAI_API_KEY=sk-proj-...
```

### Frontend (`.env.local` in dashboard_v1)
```
VITE_API_URL=https://apex-backend-i7b0.onrender.com  (production)
# or
VITE_API_URL=http://localhost:8000  (local dev)
```

---

## How to Brief the Next Thread

**Opening message to new thread:**

> We're shipping **Apex Sales Intelligence v2.0**, a production-ready sales AI system.
> 
> **Current Status:**
> - Backend: Live on Render with 500 HubSpot contacts in clean SQLite DB
> - API: v2 endpoints fully functional (`/api/v2/contacts/*`)
> - Enrichment: 3-stage multi-search working (Ed Colunga = 20K+ char profile)
> - Frontend: React dashboard ready for API wiring
> 
> **Golden Rules:**
> 1. Do NOT modify `enhanced_enrichment.py` (enrichment engine is locked)
> 2. Only call enrichment via `services/enrichment_adapter.py`
> 3. Database schema: `apex.db` with contacts + enrichment JSON
> 4. API contract: `/api/v2/contacts` is the source of truth
> 
> **Next Priority:**
> Wire Dashboard_v1 to use Apex API instead of HubSpot directly.
> 
> **Files:**
> - Backend: `apps/backend/api/routes/contacts_v2.py` (API), `services/contact_service.py` (CRUD), `services/enrichment_adapter.py` (enrichment glue)
> - Frontend: `dashboard_v1/src/pages/ContactDetailPage.tsx`, `pages/ContactsPage.tsx`
> - Database: `apex.db`
> 
> **See APEX-TRANSFER-DEC10.md for full architecture and file reference.**

---

## Questions? Clarifications?

**Key Contacts in Codebase:**
- Ed Colunga: Test enriched contact (ID: `38efdb4b-64b2-464b-a537-53f5d07d093d`)
- Render Backend: https://apex-backend-i7b0.onrender.com
- GitHub: https://github.com/quatrorabes/apex-sales-intelligence

**When opening new thread:**
- Paste this transfer doc as context
- Mention current production status
- Ask only about next priority (frontend API wiring)
- Never suggest re-architecting the enrichment engine or database schema

---

**Document created:** December 10, 2025, 6:46 PM PST  
**Status:** ✅ Production Ready | ⏳ Frontend API Wiring Pending  
**Last Updated:** This thread
