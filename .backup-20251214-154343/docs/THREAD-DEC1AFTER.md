Apex is now production-stable with a clean architecture: Apex Intelligence API (Flask + PostgreSQL on Railway) orchestrates enrichment, scoring, HubSpot sync, and Today’s Board, while Dashboard_v1 (React/Vite) consumes these APIs to give reps a prioritized action surface and intelligence-rich contact views.[1]

***

## 1. Key Programs & Components

### Apex Intelligence API (Backend)

- **Name:** Apex API Server  
- **Description:** REST backend for enrichment, scoring, Today’s Board, and CRM sync; supports local SQLite and Railway PostgreSQL.[1]
- **Location:** `~/projects/apex/api.py` → GitHub `main` → Railway service `apex-intelligence`.[1]
- **Replaces:** Ad‑hoc scripts, spreadsheets, manual CRM exports, and scattered research notes.[1]
- **Current priorities:**
  - Add health monitoring and alerting (Datadog/New Relic).[1]
  - Implement retry logic and request logging for API latency and reliability.[1]

### Dashboard_v1 (React Frontend)

- **Name:** Apex Sales Dashboard  
- **Description:** React/Vite single-page app showing Today’s Board, All Contacts, Cadence, Intelligence Lab, Raw Data, and “Why Me?”; supports enrichment triggers and viewing AI content.[1]
- **Location:** `~/projects/apex/dashboard_v1/` → deployed as static site from `main`.[1]
- **Replaces:** Excel lead lists, manual HubSpot views, and fragmented note-taking.[1]
- **Current priorities:**
  - Add EnrichmentWarning (require LinkedIn URL or at least warn).[1]
  - Test contact detail modal and enrich flows on 50+ fresh contacts.[1]
  - Add “Mark Contacted” quick action and search/filter UX.[1]

### Enhanced Enrichment Engine (Profile Builder)

- **Name:** 3‑Stage AI Enrichment Pipeline  
- **Description:** For a contact, Stage 1 uses Perplexity (sonar-pro) for web research, Stage 2 uses GPT‑4 to organize into a 12‑section dossier (pain points, product fit, personality, talking points), Stage 3 persists profile and feeds scoring.[1]
- **Location & trigger:** Inline in `api.py` (~lines 85–360) behind `POST /api/contacts/<id>/enrich`.[1]
- **Replaces:** 30–45 minutes of manual LinkedIn/web research per contact and inconsistent notes.[1]
- **Current priorities:**
  - Test on 10+ new HubSpot contacts and tune prompts.[1]
  - Enforce/validate `linkedin_url` for better quality.[1]
  - Add retries and quality guards (min length, sparse-data handling, caching).[1]

### ApexScoringEngine

- **Name:** MDCP Scoring Engine  
- **Description:** Computes MDCP (Market Decision‑maker Contact Priority), priority scores, tiers (hot, warm, qualified, nurture, etc.) and later RSS (Relationship Strength Score).[1]
- **Location:** Initialized in `api.py` (~374–380); core logic under `apps/backend/intelligence/engines/scoring/`.[1]
- **Replaces:** Manual lead scoring sheets and intuition-driven prioritization.[1]
- **Current priorities:**
  - Validate thresholds on 50+ enriched contacts.[1]
  - Implement RSS based on activity data.[1]
  - Expose scoring weights and add a feedback loop in UI.[1]

***

## 2. Major API Endpoints

### `/api/hubspot/import`

- **Purpose:** Paginated import from HubSpot; applies business filters (exclude unqualified, DNC, personal email, missing company/name/email) and upserts to DB with phone/mobile/LinkedIn, using `hubspot_id` as unique key.[1]
- **Location:** `api.py` around lines 1005–1065.[1]
- **Replaces:** Manual CSV exports from HubSpot and separate upload/cleanup steps.[1]
- **Current action items:**
  - Nightly auto re‑sync job.[1]
  - Extend pattern to Salesforce/Pipedrive connectors.[1]

### `/api/contacts/<id>/enrich`

- **Purpose:** Run 3‑stage enrichment for a single contact and persist profile + scores.[1]
- **Location:** `api.py` enrichment section (~85–360).[1]
- **Replaces:** Human research across LinkedIn, company websites, and unstructured note‑taking.[1]
- **Current action items:** LinkedIn validation, retry/sparse‑data handling, and profile quality flags.[1]

### `/api/todays-board`

- **Purpose:** Returns Today’s prioritization board: Hot New Prospects and Relationship buckets, each with scores, urgency tier, and metadata.[1]
- **Location:** `api.py` around lines 875–1000.[1]
- **Replaces:** Manual “who do I call” lists and spreadsheet‑based prioritization.[1]
- **Current action items:**
  - Backfill `last_contact_date` from HubSpot activity to fully populate relationships.[1]
  - Add date filters and “Mark Contacted” endpoint.[1]

### Backfill & Scoring Endpoints (new)

- **`/api/hubspot/backfill-activity` (POST):** Backfills `last_contact_date` from HubSpot activity and contact properties. (Recently added to `api.py` under “HUBSPOT BACKFILL LAST CONTACT DATE”.)  
- **`/api/contacts/score-all` (POST):** Batch-scores contacts using titles, company presence, LinkedIn presence, enrichment status, and recency; updates `mdcp_score`, `priority_score`, `mdcp_tier`, `last_scored`. (Added under “BULK SCORING ENDPOINT” in `api.py`.)  
- **Purpose:** Operationalize scoring and recency signals across the entire database, not just per‑enrichment.[1]
- **Current action items:** Run periodically (or cron) and eventually orchestrate via scheduler.

***

## 3. Enhanced Enrichment Engine Details

### Roles of Each Component

- **Perplexity (Stage 1):** Generates raw research text on contact and company using sonar-pro, with citations and broad coverage.[1]
- **GPT‑4 (Stage 2):** Transforms research into a structured 12‑section profile (bio, pain points, objectives, risks, buying triggers, personality), ready for sales use.[1]
- **Database & Scoring (Stage 3):** Saves enriched profile to `contacts` table, triggers MDCP scoring, and makes intelligence queryable by Dashboard and Today’s Board.[1]

### What It Replaced & Value

- Replaced manual, one‑off pre‑call research and inconsistent note templates.[1]
- Delivers consistent, AI‑generated dossiers per contact, cutting pre‑call prep from ~30–45 minutes to ~1 minute.[1]

### Current Priorities

- Improve robustness (retry logic, sparse-output handling, minimum length checks).[1]
- Make LinkedIn URL a first‑class, validated input.[1]
- Add source tracking and caching to reuse company‑level research across contacts.[1]

***

## 4. Frontend Dashboard_v1 Functions

### Tech Stack & Location

- **Stack:** React, TypeScript, Vite, hitting REST API via `API_URL = import.meta.env.VITE_API_URL`.[1]
- **Location:** `~/projects/apex/dashboard_v1/` in repo; deployed as static app on Railway.[1]

### Core Features & User Value

- **Today’s Board:** Surfaces Hot Prospects and Relationship tiers, with counts and priority, answering “who should I talk to today.”[1]
- **All Contacts View:** Displays contact list with phone, mobile, LinkedIn and status, pulling live from PostgreSQL.[1]
- **Intelligence Views:** Tabs for AI content (Pain Points, Product Fit, Key Insights, scripts and templates).[1]
- **Enrichment Triggers:** Buttons to run enrichment and generate content for a selected contact.[1]

### Key Changes from the Thread

- Centralized `VITE_API_URL` and removed a dozen hard‑coded URLs so all traffic routes correctly to Railway (or local, via env).[1]
- Updated contact header to show phone, mobile, and LinkedIn; wired up Today’s Board to the fixed API and scores.[1]

### Current Priorities

- Enrichment pre‑checks (warn if LinkedIn URL missing).[1]
- Error boundaries around contact fetch failures and offline fallbacks.[1]
- UX features like search/filter, “Mark Contacted”, and signal feeds.[1]

***

## 5. API Server Details

### Environment & Database

- **Environments:** Local dev with SQLite; production on Railway with PostgreSQL.[1]
- **Env detection:** `IS_PRODUCTION` flag toggling connection, SQL syntax (e.g., `?` vs `%s`), and transaction behavior.[1]
- **Deployment:** Railway service `apex-intelligence` at `https://apex-intelligence-production.up.railway.app`.[1]

### Endpoints & Orchestration

- Contact CRUD, enrichment (`/api/contacts/<id>/enrich`), scoring (`/api/contacts/score-all`), Today’s Board (`/api/todays-board`), HubSpot import/backfill (`/api/hubspot/*`), and health (`/api/health`).[1]
- Orchestrates external APIs: HubSpot CRM, Perplexity sonar-pro, OpenAI GPT‑4.[1]

### Major Improvements From the Thread

- Fixed PostgreSQL transaction handling with per‑record commit/rollback to avoid batch aborts.[1]
- Added unique index on `hubspot_id` and aligned schema (phone_mobile, data_source, sync_date, names, lifecycle, lead_status).[1]
- Resolved Today’s Board date logic and casting issues so it works with TEXT `last_contact_date`.[1]
- Connected GitHub → Railway source correctly and stabilized deploy flow.[1]

***

## 6. Action Items & Current Priorities (By Component)

### Apex Intelligence API

- Add monitoring and alerting in production.[1]
- Implement retry and better logging around enrichment, scoring, and HubSpot calls.[1]

### HubSpot Integration

- Run full import regularly; set up nightly re‑sync.[1]
- Finalize backfill of `last_contact_date` from HubSpot engagements.[1]

### Enhanced Enrichment & Scoring

- Validate enrichment quality and MDCP distributions on a larger sample.[1]
- Add RSS and feedback loop for reps; expose scoring logic.[1]

### Today’s Board

- Populate relationships via backfill and new activity tracking.[1]
- Add date-scoped boards (Today vs Week) and “Mark Contacted” action.[1]

### Dashboard_v1

- Ensure all fetch calls use `VITE_API_URL` (no lingering hard-coded localhost).[1]
- Ship EnrichmentWarning, search/filter UX, and quick actions to close the loop from board to activity.[1]

This guide is the baseline context for any new Apex thread: assume these programs, endpoints, and priorities are in place, and build from here.

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/facf915c-8018-4b8b-8368-0fa7a6d0e085/THREAD-DEC1AM.md)