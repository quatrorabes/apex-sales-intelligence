Yes. Here is a clean Apex architecture you can copy into a new thread so nothing gets lost.[1]

## System overview

- **Backend (Python / FastAPI / SQLite)**  
  Lives in `apps/backend`. Owns contacts, enrichment storage, API routes, and calls your existing enrichment engine (no changes to that code).  
- **Engines (Apex Intelligence)**  
  Live under `apps/backend/intelligence/engines`. `enhanced_enrichment.py` is the canon enrichment engine; everything else here is supporting logic or legacy.  
- **Frontend (Dashboard_v1 React)**  
  Lives in `dashboard_v1/src`. Renders contacts, dossier, intelligence, and outreach views. Reads from API and applies light parsing/formatting.

```text
apex-sales-intelligence/
├── apps/
│   └── backend/                   # Apex backend (canonical)
│       ├── main.py                # FastAPI app entrypoint
│       ├── apex.db                # Clean contacts + enrichment DB
│       ├── api/
│       │   └── routes/
│       │       └── contacts_v2.py # v2 REST API for contacts/enrichment
│       ├── schemas/
│       │   └── enrichment_schema.py   # Pydantic models (reference only)
│       ├── services/
│       │   ├── contact_service.py     # CRUD + stats on contacts table
│       │   └── enrichment_adapter.py  # Calls EnhancedEnrichment, saves result
│       └── intelligence/
│           └── engines/
│               └── enrichment/
│                   └── enhanced_enrichment.py  # PRIMARY enrichment engine (do not change)
└── dashboard_v1/
    └── src/
        ├── App.tsx                    # Frontend shell & routing
        ├── components/
        │   ├── ContactsView.tsx       # Main contacts list & filters
        │   ├── AllContactsView.tsx    # (If used) aggregate contacts view
        │   ├── ContactDetail.tsx      # Legacy detail component
        │   └── ContactEnrichmentView.tsx / EnrichmentDisplay.tsx  # Enrichment UI pieces
        ├── pages/
        │   ├── ContactsPage.tsx       # Contacts screen wrapper
        │   └── ContactDetailPage.tsx  # New Apex contact detail + dossier/intel tabs
        ├── utils/
        │   └── enrichmentParser.ts    # Frontend parsing of raw_profile text
        └── types/
            └── EnrichmentSchema.ts    # TS mirror of enrichment JSON shape
```

## Backend modules (what “works” now)

- **`main.py`**  
  - Hosts `FastAPI` app and CORS.  
  - Includes the new router: `app.include_router(contacts_v2_router)`.

- **`api/routes/contacts_v2.py`**  
  - `GET /api/v2/contacts` – list contacts + stats.  
  - `GET /api/v2/contacts/stats` – aggregate counts.  
  - `POST /api/v2/contacts` – create contact (from CSV, CRM, or manual).  
  - `POST /api/v2/contacts/{id}/enrich` – will eventually call the adapter.  
  - `POST /api/v2/contacts/import/csv` – CSV import (ready for wiring to UI).  

- **`services/contact_service.py`**  
  - Owns the **canonical `contacts` table** in `apex.db` (id, name, company, email, enrichment JSON, timestamps).  
  - Methods: `create_contact`, `get_contact`, `get_all_contacts`, `save_enrichment`, `get_stats`, etc.

- **`services/enrichment_adapter.py`**  
  - **Critical glue.** Takes a contact from `contacts` table, builds the dict your **existing `EnhancedEnrichment`** expects, calls `engine.enrich_contact()`, and saves:  
    ```python
    enrichment_data = {
        "version": "1.0",
        "raw_profile": result["profile_text"],
        "character_count": result["character_count"],
    }
    ```
  - This means the DB stores **raw enrichment text**; parsing stays on the frontend.

- **`intelligence/engines/enrichment/enhanced_enrichment.py`**  
  - Your 3‑stage multi-search enrichment engine.  
  - **Golden rule for future threads:** do not change this script’s logic or prompts; only call it via the adapter.

## Frontend modules (what to rely on)

- **`App.tsx` + routing**  
  - Entry point; ensures `/contacts` and `/contacts/:id` hit the right components.

- **Contacts list & stats**  
  - `components/ContactsView.tsx` and/or `pages/ContactsPage.tsx` should become the consumers of `/api/v2/contacts` and `/api/v2/contacts/stats` instead of talking to HubSpot directly.  
  - Enrichment indicator now should be driven by:  
    - `contact.enrichment` existing in API response, or  
    - `enriched_at` not null.

- **Contact detail & dossier**  
  - `pages/ContactDetailPage.tsx` is the **canonical Apex detail view**.  
  - It currently:  
    - Pulls raw enrichment data (right now from HubSpot; soon from `/api/v2/contacts/:id`).  
    - Uses `extractSection` + markdown patterns to split into person/company/sales/personality.  
    - Uses **fallbacks**: if card parsing fails or over-fragments, it shows cleaned raw text instead.

- **Parsing utilities**  
  - `utils/enrichmentParser.ts` (and inline helpers in `ContactDetailPage.tsx`) should be the **only place** that knows about markdown headers, numbered sections, etc.  
  - Long term, once the DB starts storing structured JSON instead of just `raw_profile`, this module becomes a mapping layer rather than regex hell.

## Legacy / ignore for now

- Multiple old engines under `intelligence/engines/enrichment/` (e.g., `perplexity_enrichment.py`, older `intelligence_compiler` versions).  
- Older outreach/scoring flows under `intelligence/engines/outreach` and `intelligence/engines/scoring` that aren’t currently called via `main.py`.  
- HubSpot‑specific enrichment parsing in the frontend that reads directly from CRM instead of `/api/v2/contacts`.  
  - Treat CRM sync as **integration**, not source of truth: Apex DB is primary, CRM is optional mirror.

## How to brief the next thread

When you open a new thread, paste this short context upfront:

1. **Source of truth:**  
   - Contacts and enrichment now live in `apps/backend/apex.db` (`contacts` table).  
   - Each contact has `enrichment: { version, raw_profile, character_count }` from `EnhancedEnrichment`.

2. **Enrichment contract:**  
   - Do **not** modify `enhanced_enrichment.py`.  
   - Only call it via `services/enrichment_adapter.enrich_and_save(contact_id)`.

3. **API surface for Dashboard_v1:**  
   - Use `/api/v2/contacts`, `/api/v2/contacts/{id}`, `/api/v2/contacts/stats`, `/api/v2/contacts/import/csv`, `/api/v2/contacts/{id}/enrich`.

4. **Frontend contract:**  
   - `ContactDetailPage.tsx` should read `contact.enrichment.raw_profile` and parse it.  
   - `ContactsView.tsx` should treat `enriched_at` or `enrichment` presence as “enriched”.

If you paste that into the new conversation, Apex stays on-rails and we keep compounding on this architecture instead of thrashing it.

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/e79db3ba-bf77-4489-8839-3258f27adbd4/CleanShot-2025-12-10-at-14.58.51-2x.jpg)