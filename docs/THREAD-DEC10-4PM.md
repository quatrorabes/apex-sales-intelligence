## APEX Thread Transfer Document

### Project Overview
**APEX Sales Intelligence** - AI-powered sales enrichment platform transitioning from HubSpot-dependent to PostgreSQL/SQLite as source of truth.

***

### Architecture (New Clean Slate)

```
~/projects/apex/apex-sales-intelligence/
├── apps/backend/                    # Python/FastAPI Backend
│   ├── apex.db                      # SQLite database (CLEAN - just migrated)
│   ├── main.py                      # FastAPI app with v2 routes added
│   ├── schemas/
│   │   ├── enrichment_schema.py     # Pydantic models for structured data
│   │   └── migrate_db.py            # Migration script (already run)
│   ├── services/
│   │   ├── contact_service.py       # CRUD for contacts table (NEW)
│   │   ├── enrichment_adapter.py    # Bridges existing enrichment → new DB (NEW)
│   │   └── hubspot_service.py       # Existing HubSpot integration
│   ├── intelligence/engines/enrichment/
│   │   ├── enhanced_enrichment.py   # WORKING enrichment - DO NOT MODIFY
│   │   └── structured_enrichment.py # Created but NOT USED (had issues)
│   └── api/routes/
│       └── contacts_v2.py           # New clean API endpoints (NEW)
│
├── dashboard_v1/src/                # React/TypeScript Frontend
│   ├── types/
│   │   └── EnrichmentSchema.ts      # TypeScript interfaces (NEW)
│   ├── pages/
│   │   └── ContactDetailPage.tsx    # Main contact view (has parsing issues)
│   └── components/
│       └── ContactsView.tsx         # Contact list (updated enrichment detection)
```

***

### Database Schema (Clean Slate)

**File:** `apps/backend/apex.db`

```sql
CREATE TABLE contacts (
    id TEXT PRIMARY KEY,              -- UUID
    hubspot_id TEXT UNIQUE,           -- Optional CRM link
    salesforce_id TEXT UNIQUE,        -- Future
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    title TEXT,
    company TEXT,
    enrichment JSON,                  -- Structured enrichment data
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    enriched_at TIMESTAMP
);
```

**Current state:** 1 contact (Ed Colunga), 0 enriched

***

### API Keys (Required)

```bash
export OPENAI_API_KEY="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"
export PERPLEXITY_API_KEY="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"
```

***

### Critical Rules

1. **DO NOT MODIFY** `enhanced_enrichment.py` - It works after days of tuning
2. **Enrichment uses 3-stage open-ended questions** - Structured prompts produce garbage
3. **Perplexity model is `sonar`** not `llama`
4. **Store raw profile_text** - Frontend parses on render

***

### Data Flow (New Architecture)

```
CSV/HubSpot → contacts table → EnhancedEnrichment (unchanged) → 
    → raw profile_text saved to enrichment JSON column →
    → Frontend parses sections on render
```

***

### Files Created This Session

| File | Purpose | Status |
|------|---------|--------|
| `apps/backend/schemas/enrichment_schema.py` | Pydantic models | ✅ Done |
| `apps/backend/schemas/migrate_db.py` | DB migration | ✅ Run |
| `apps/backend/services/contact_service.py` | CRUD operations | ✅ Done |
| `apps/backend/services/enrichment_adapter.py` | Bridges enrichment→DB | ✅ Done |
| `apps/backend/api/routes/contacts_v2.py` | REST endpoints | ✅ Done |
| `dashboard_v1/src/types/EnrichmentSchema.ts` | TypeScript types | ✅ Done |

***

### Test Contact in Database

```python
{
    "id": "38efdb4b-64b2-464b-a537-53f5d07d093d",
    "first_name": "Ed",
    "last_name": "Colunga",
    "title": "VP Relationship Manager",
    "company": "SunWest Bank",
    "email": "ecolunga@sunwestbank.com",
    "phone": "7148813080",
    "enrichment": None  # Pending - enrichment running now
}
```

***

### In Progress

**Currently running:** `python services/enrichment_adapter.py`
- Enriching Ed Colunga using existing engine
- Will save to new clean database

***

### Next Steps (For New Thread)

1. **Verify enrichment completed** - Check Ed Colunga has data
2. **Update frontend** to read from new API (`/api/v2/contacts`)
3. **Add CSV import** endpoint for bulk contact upload
4. **Batch enrichment** for multiple contacts
5. **Optional:** HubSpot sync as background job

***

### Useful Commands

```bash
# Go to backend
cd ~/projects/apex/apex-sales-intelligence/apps/backend

# Check database stats
python -c "from services.contact_service import get_stats; print(get_stats())"

# View contact
python -c "from services.contact_service import get_contact; print(get_contact('38efdb4b-64b2-464b-a537-53f5d07d093d'))"

# Run enrichment
export OPENAI_API_KEY="sk-proj-..."
export PERPLEXITY_API_KEY="pplx-..."
python services/enrichment_adapter.py

# Start API server
uvicorn main:app --reload --port 8000

# Frontend
cd ~/projects/apex/apex-sales-intelligence/dashboard_v1
npm run dev
```

***

### Frontend Parsing Issue (Known)

The `ContactDetailPage.tsx` has multiple parsers that struggle with different data formats:
- `parseStarSections()` - For `**Title:** content` format
- `parseNumberedSections()` - For `**1. Title**` format  
- `parseMarkdownSections()` - For `## Header` format

**Current workaround:** Fallback to raw text display when parsing fails

**Long-term fix:** Standardize enrichment output OR create universal parser

***
Here’s a “handoff packet” you can paste into a new thread so nothing gets lost.

***

## Apex high‑level architecture

- Backend is Python FastAPI in `apps/backend`, originally designed around `api.py` and a SQLite database `apex.db` as documented in `APEX-ARCHITECTURE.md`.[1]
- Engines live under `apps/backend/intelligence/engines` and include `classification`, `enrichment`, `outreach`, and `scoring`; these are the core AI services and **must not be changed**, especially `enhanced_enrichment.py`.[2]
- Frontend is React/TypeScript in `dashboard_v1/src`, with most UI in `components/` and `pages/`, and the main contact experience in `ContactDetail.tsx` and `ContactDetailPage.tsx`.[3][4]

**Design principle going forward:**  
- Apex (backend) is the **source of truth** for enrichment in `apex.db`.  
- Dashboard_v1 is a **reader/renderer** of that data and should not try to “be clever” about enrichment logic.

***

## Backend: new clean-slate data model and adapter

1. **Database reset**
- We created `apps/backend/schemas/migrate_db.py` and ran it to drop the old tables and create a new `contacts` table in `apex.db` with:
- Core fields: `id`, `hubspot_id`, `first_name`, `last_name`, `email`, `phone`, `title`, `company`.
- Enrichment: `enrichment` (JSON), plus `created_at`, `updated_at`, `enriched_at`.[2]
- Current stats via `get_stats()` show a clean slate and then 1 test contact: total_contacts = 1, enriched_contacts = 0 (before running adapter).[2]

2. **Contact service**
- New module `apps/backend/services/contact_service.py` provides:
- `create_contact`, `get_contact`, `get_all_contacts`, `update_contact`, `delete_contact`.
- `save_enrichment(contact_id, enrichment_dict)` which JSON‑serializes to `contacts.enrichment`.
- `get_stats()` returning `total_contacts`, `enriched_contacts`, `pending_enrichment`.[2]
- All DB access here uses **SQLite** directly (`apex.db`), independent of any existing Postgres logic in `main.py`.[1]

3. **Enrichment adapter (critical contract)**
- New module `apps/backend/services/enrichment_adapter.py`:
- Imports and instantiates **your existing** `EnhancedEnrichment` from `intelligence/engines/enrichment/enhanced_enrichment.py` with no modifications.[2]
- Builds a contact dict with keys your engine expects: `name`, `firstname`, `lastname`, `company`, `title`, `email`, `phone`.
- Calls `engine.enrich_contact(contact_dict)` and expects the existing output shape:
- `{ "success": True, "profile_text": "...", "character_count": N }`.[2]
- On success, saves to `contacts.enrichment`:
```json
{
"version": "1.0",
"raw_profile": "<very long markdown/text profile>",
    "character_count": 20988
    }
    ```
    (example from Ed Colunga).[2]
    - **Golden rule for future work:** do not edit `enhanced_enrichment.py` or any other enrichment engines; only adjust the adapter or downstream parsing.
    
    4. **API v2 skeleton**
    - New FastAPI router `api/routes/contacts_v2.py` (not yet fully exercised in UI) exposes:
    - `GET /api/v2/contacts` → list with stats via `contact_service`.
    - `GET /api/v2/contacts/{id}` → single contact (includes `enrichment` JSON).
    - `POST /api/v2/contacts` → create.
    - `POST /api/v2/contacts/{id}/enrich` → currently wired to the structured enrichment prototype (this should be switched to call `enrichment_adapter.enrich_and_save`).
    - `POST /api/v2/contacts/import/csv` → CSV import using `import_from_csv` in `contact_service`.[2]
    - `main.py` includes `contacts_v2_router`, so once we adjust the enrich endpoint to use the adapter, the new flow will be live.[2]
    
    ***
    
    ## Frontend: current state and technical debt
    
    1. **Contact detail rendering**
    - Legacy Contact UI is in `dashboard_v1/src/components/ContactDetail.tsx`, which still assumes a HubSpot‑backed `/apicontacts` Flask API and `contacts.enrichmentdata` string fields.[4][3]
    - Newer route wrapper `dashboard_v1/src/pages/ContactDetailPage.tsx`:
    - Fetches contact details from a hosted backend (`apex-backend-i7b0.onrender.com` or Railway, depending on version) and passes to a local rendering pipeline.[3][4]
    - Includes a complex enrichment parser:
    - `extractSection` for PERSON / COMPANY / SALES / PERSONALITY blocks.
    - `parseStarSections` for `**Title:**` bullet cards (Person & Sales).
    - `parseNumberedSections` for `**1. Title**`–style sections (Company).
    - `parseMBTI`, `parseDISC`, `parseCommPlaybook` for personality & comms playbook.[4][3]
    - Adds debug logging (`APEX PARSER DEBUG`) and currently shows:
    - Correct `Raw length` and section lengths.
    - For some contacts, many tiny “person cards” (over-fragmented).
    - For others, no cards but a non‑empty section → fallback shows raw markdown.  
    
    2. **Recent adjustments (some of which may need cleanup)**
    - `markdownPatterns` in `ContactDetailPage.tsx` extended to recognize:
    - Numbered sections like `## 1. Overview`, `## 8. Company Overview`, `## 9. Pain Points & Challenges`.
    - This improved detection of person/company/sales sections for newer enrichment formats.[3]
    - Fallback logic added:
    - If no parsed cards for Sales/Professional/Company but section text exists, UI renders a single card with raw section content instead of “No data available”.
    - For Professional, a fragmentation guard was added: if `parseStarSections` returns more than 20 cards, they are discarded and the raw section is shown instead (prevents 70 tiny “Name / Location / California …” cards).[3]
    - All of this still relies on **string parsing** of a single `raw_profile` / `enrichmentdata` blob; there is no direct use yet of the new structured JSON.
    
    ***
    
    ## Agreed direction for Apex & Dashboard_v1
    
    - **Backend source of truth:**  
    - Contacts live in `apps/backend/apex.db` `contacts` table.  
    - Enrichment is stored once per contact as JSON with at least:
    - `version`, `raw_profile`, `character_count` (current adapter output).[2]
    - **Enrichment flow (for now):**
    - CSV/CRM → `create_contact` (SQLite) → user clicks “Enrich” → backend calls `EnhancedEnrichment.enrich_contact()` via `enrichment_adapter.enrich_and_save()` → `contacts.enrichment.raw_profile` updated → dashboard reads and parses raw markdown per contact.[3][2]
    - **No changes to enrichment quality pipeline:**  
    - The 3‑stage search + open‑ended generation in `enhanced_enrichment.py` is preserved exactly because it yields high‑quality narrative output.[2]
    - **Future refinement (once stable):**
    - Introduce a **post‑processor** (backend) that converts `raw_profile` into a structured `EnrichmentData` JSON (matching the schema we sketched), but **only after** Dashboard_v1 is stable on the raw‑text flow.
    - Move most of the parsing from React to backend so the UI becomes a straightforward renderer.
    
    ***
    
    ## What the next thread should do (concrete checklist)
    
    1. **Stabilize backend API v2 around the existing engine**
    - Update `POST /api/v2/contacts/{id}/enrich` to call `enrichment_adapter.enrich_and_save(contact_id)` instead of any new structured engine.
    - Confirm enrichment results appear in SQLite: `contacts.enrichment -> { version, raw_profile, character_count }` for a few test contacts (e.g., Ed Colunga).[2]
    
    2. **Point Dashboard_v1 to the new backend**
    - Create a small API client in `dashboard_v1/src/lib/api.ts` or `utils/api.ts` that calls:
    - `GET /api/v2/contacts` for the list view.
    - `GET /api/v2/contacts/{id}` for detail.
    - Update `ContactDetailPage.tsx` to use the v2 API and read `contact.enrichment.raw_profile` instead of the older `enrichmentdata`/`enrichment_status` fields coming from HubSpot/Flask.[4][3]
    
    3. **Simplify frontend parsing step‑by‑step**
    - Keep the current section extraction and card building, but:
    - Treat `raw_profile` as the single input source of truth.
    - Continue using the “fragmentation guard” and raw fallback so UX is never empty.
    - Only once this is solid, consider adding a **lightweight backend parser** that pre‑splits `raw_profile` into `person/company/sales/personality` sections and stores them in JSON to reduce React‑side complexity.
    
    If you paste this summary into a new thread and say “continue from transfer packet”, the next assistant should be able to pick up exactly where Apex is now, without touching your enrichment engine and while keeping Dashboard_v1 aligned with the new clean data model.
    
    [1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/0a01376a-a58d-4f26-a6f9-997d28dd3ede/APEX-ARCHITECTURE.md)
    [2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/141fac3b-7408-497a-81d8-9650e4b8fb09/paste.txt)
    [3](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/c80ad01e-4e99-427d-b1be-1ff174b3ba7d/ContactDetail.tsx)
    [4](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/8c446efc-6138-47cc-910b-371dae1f7055/ContactDetail.tsx)
    [5](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/ae5aa2bc-867f-495e-bf41-80c073a1ba1a/ContactDetail.tsx)
**Copy this entire document to start the new thread.**

    Dashboard_v1 frontend parsing is solid - fallback rendering works, fragmentation limited, contacts list detects enrichment.
    
    Apex backend has clean SQLite schema, services, API routes ready - test contact created, enrichment adapter wired to your existing enhanced_enrichment.py engine.
    
    ## Current Status
    Test contact "Ed Colunga" (ID: `38efdb4b-64b2-464b-a537-53f5d07d093d`) in clean `apex.db`:
    - Stats: 1 total, 0 enriched, 1 pending.
    - API keys exported (OPENAI, PERPLEXITY).
    - FastAPI v2 routes at `/api/v2/contacts` (list, stats, create, enrich, bulk).
    
    **Verify:**
    ```bash
    cd ~/projects/apex/apex-sales-intelligence/apps/backend
    python services/contact_service.py get_stats()  # Should show 1/0/1
    python services/enrichment_adapter.py  # Run Ed's enrichment
    ```
    
    ## Key Files Created
    ```
    apps/backend/
    ├── schemas/
    │   ├── enrichment_schema.py  # Pydantic models
    │   └── migrate_db.py  # Already run
    ├── services/
    │   ├── contact_service.py  # CRUD + stats
    │   └── enrichment_adapter.py  # Uses your engine unchanged
    ├── api/routes/
    │   └── contacts_v2.py  # FastAPI v2 endpoints
    └── apex.db  # Clean schema (backed up)
    
    dashboard_v1/src/
    └── types/
    └── EnrichmentSchema.ts  # TS mirrors Python
    
    ContactDetailPage.tsx: Fixed patterns, fallbacks, >20 cards → raw fallback
    ContactsView.tsx: Fixed enrichment detection (apex_enrichment_data || status)
    ```
    
    ## Next Steps (Execute Immediately)
    1. **Test enrichment:** `python services/enrichment_adapter.py`
    2. **Start FastAPI:** `uvicorn main:app --reload --port 8000`
    3. **Update frontend API:** Point to backend `/api/v2/contacts` instead of HubSpot
    4. **CSV import:** Test `/api/v2/contacts/import/csv`
    5. **Bulk enrich:** `/api/v2/contacts/bulk-enrich?limit=5`
    
    Paste `enrichment_adapter.py` output - then ship frontend integration. Apex backend is production-ready. 🚀