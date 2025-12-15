You just completed a massive lift on Apex today. Here’s a clean handoff summary for the next thread and for future devs.

## Backend status: Apex API on Railway

- Environment:
  - Backend running on Railway, using Flask API from `api.py` deployed from `/Users/chrisrabenold/projects/apex`.[1]
  - Database is PostgreSQL on Railway; local `apex.db` is now legacy / reference only.[1]

- Schema:
  - `contacts` table was recreated in Postgres and extended to mirror the rich local `apex.db` schema: lead_status, lifecycle_stage, hubspot_id, hs_object_id, industry, location, scoring fields, enrichment fields, cadence fields, vertical verification, signal tracking, etc.[2][1]
  - Additional tables in Postgres:
    - `contact_activities` – activity logging (calls, emails, LinkedIn, meetings) with timestamps.[1]
    - `opportunity_signals` – simulated or future real buying signals with urgency boost, viewed flag.[1]
    - `userpreferences` (scoring “Why Me” / routing preferences, currently keyed by `userid`).[1]

- HubSpot import (fixed and upgraded):
  - New `/api/hubspot/import` implementation pulls a wide property set from HubSpot (name, email, phone, company, title/jobtitle, industry, LinkedIn, lifecycle stage, lead status, owner, created date, contact counts, etc.).[1]
  - Filters applied BEFORE insert:
    - Excludes lead_status in: `unqualified`, `do not contact`, `unsubscribe` (and likely empty).[1]
    - Excludes lifecycle_stage in: `unqualified`.[1]
    - Excludes personal contacts flagged as true/yes in HubSpot (so friends/family don’t enter Apex).[1]
    - Excludes records without required fields (name/email/phone/company).[1]
  - De-duplication:
    - Skips if an existing contact has same email OR same hubspot_id.[1]
  - Insert behavior:
    - On first import, creates full rows with core CRM data + hubspot metadata.
    - On subsequent imports, updates existing rows (name, title, company, lifecycle_stage, lead_status, etc.) instead of duplicating.[1]
  - Status:
    - Working end‑to‑end against Railway Postgres; contacts show correct lead_status, lifecycle_stage, location, job_title, hubspot_id in `/api/contacts`.[2]

- Enrichment engine:
  - You now have two “modes” in code:
    - Legacy engine: imports from `apps/backend/intelligence/engines/enrichment/enhanced_enrichment.py`. This path is fragile on Railway.[1]
    - Inline Perplexity enrichment: new `/api/contacts/<id>/enrich` that calls Perplexity `sonar-pro` and writes markdown profile into `contacts.profile_content`, sets `enrichment_status='completed'`, updates `enriched_at`. This is the one that just produced a 5,000+ character profile for contact 97.[2][1]
  - Tested:
    - POST `/api/contacts/97/enrich` returns `{ success: true, contact_id: 97, profile_length: 5031 }`.[2]
    - GET `/api/contacts/97` shows `enrichment_status: "completed"` and `profile_content` filled with a long markdown profile including “Professional Background”, “Company Overview”, “Industry Context”, “Potential Pain Points”, “Talking Points”, etc.[2]

- Scoring and Today’s Board:
  - There is a robust scoring pipeline in `api.py` with:
    - Fallback scoring if advanced engines fail (simple rule-based scoring).[1]
    - Proper Apex scoring integration (ApexScoringEngine, ScoringOrchestrator) wired to contacts table when backend modules are available.[1]
  - `/api/todays-board`:
    - Now points at Postgres and no longer uses SQLite-only `julianday`; date math has been adjusted for Postgres (days since last_contact_date).[1]
    - For now returns empty tiers until contacts have last_contact_date and scoring values; the endpoint itself is stable.[2]

## Frontend status: Dashboard_v1 (Vite/React)

- App structure:
  - Frontend lives at `/Users/chrisrabenold/projects/apex/dashboard_v1`, built with React + Vite and a dark AI sales UI.[3]
  - Main tabs (top nav):
    - Today’s Board
    - All Contacts
    - Cadence
    - Intelligence Lab
    - Raw Data
    - Why Me[3]

- All Contacts tab:
  - Now reading from Railway Postgres via `/api/contacts` and displays HubSpot-imported contacts (names, companies, titles, basic stage/priority columns).[2]
  - The API payload confirms everything needed for deeper UI use is present: lead_status, lifecycle_stage, industry, job_title, location, hubspot_id, etc.[2]

- ContactDetailModal component:
  - File: `dashboard_v1/src/components/ContactDetailModal.tsx`.[3]
  - Behavior:
    - When you click a contact, it fetches `/api/contacts/<id>` to get fresh data.[3]
    - Tracks `localContact` state and enrichment status flag:
      - `isEnriched = localContact.enrichment_status === 'completed' && localContact.profile_content && localContact.profile_content.length > 0`.[3]
    - View modes:
      - `viewMode` can be `'intelligence' | 'dossier' | 'outreach'`, default `'intelligence'`. Tabs at the top switch the mode. [3]
  - Dossier/intelligence parsing:
    - There is a `extractSection(sectionNumber, sectionName)` helper that tries to parse `localContact.profile_content` by looking for patterns like `1. Overview`, `2. Background`, etc., then uses `dossierData = { overview, background, education, ... }` to fill cards in the Dossier view.[3]
    - Problem: the new Perplexity enrichment writes headings like `## Professional Background`, `## Company Overview`, `## Industry Context`, etc. This format does NOT match the `1. Overview` pattern, so `extractSection` returns null for all sections. Result: modal renders as “not enriched” / empty despite `profile_content` being full.[3][2]
  - Current UX issue (the one you’re seeing):
    - API shows enriched profile and `enrichment_status='completed'`.[2]
    - Modal still appears blank or “not enriched” because section extraction can’t parse the markdown headings.
    - Re-enriching would just pay Perplexity twice and still hit the same UI parsing problem; the data is already there.

## What we accomplished today

- Stabilized the backend:
  - Moved critical endpoints from SQLite-style to PostgreSQL-safe SQL (placeholders, date math).[1]
  - Hand-migrated and extended schema on Railway to mirror `apex.db` so Apex logic has the fields it expects.[2][1]
  - Rebuilt `/api/hubspot/import` to:
    - Pull all relevant CRM properties.
    - Apply business filters (no unqualified / DNC / personal contacts).
    - Avoid duplicates.
    - Save richer context for scoring and outreach.[1]
  - Repaired enrichment so it:
    - Actually runs on Railway.
    - Uses your `sonar-pro` key.
    - Writes markdown profile into `profile_content` and marks status appropriately.[2][1]

- Verified key endpoints:
  - `/api/health` → healthy.[2]
  - `/api/contacts?limit=3` → returns HubSpot contacts with correct CRM fields.[2]
  - `/api/todays-board` → returns structured JSON with zero counts for now (no enriched + scored contacts with activity yet).[2]
  - `/api/user/preferences` → returns default user profile (`user_id: "default"`, scoring_profile: "DEFAULT").[2]
  - `/api/contacts/97/enrich` → success true, profile_length ~5000.[2]
  - `/api/contacts/97` → confirms `enrichment_status:

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/339726a9-98c0-4057-8c33-5e11e13be772/api.py)
[2](https://apex-intelligence-production.up.railway.app/api/contacts/97)
[3](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/76360545-5fe4-4562-98c6-b445e383216a/THREAD-NOV27-TODAYS-ACTIVITIES.md)
[4](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/5fbfb6dd-c886-4e46-9b04-41503763f109/api.py)