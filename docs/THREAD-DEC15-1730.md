Below is a **THREAD TRANSFER** you can paste into a new thread to continue cleanly under *Apex Sales Intelligence* with the correct `Apex` + `Dashboard_v1` naming and the current Render/Vercel/Postgres deployment model.[1]

## Thread Transfer: Apex Sales Intelligence (Dec 15, 2025)

### Current objective
Stabilize **Dashboard_v1** UI routing and page ownership after several layout experiments, while keeping **ContactDetail** functional and preserving the “Good afternoon, Chris” landing experience.[1]

### Deployment topology (now)
- **Backend:** Render web service (`appsbackend`, FastAPI via `uvicorn main:app`) with `DATABASE_URL` coming from a Render Postgres instance (`apex-db`).[1]
- **Frontend:** Vercel hosting the Dashboard SPA (Vite build → `dist`) with API base URL configured via env var (`VITE_API_URL` / `VITEAPEXAPIURL` depending on which client helper is used).[1]
- **Database:** Postgres on Render (`apex-db`).[1]

### What broke / what got fixed
- Root route (`/`) was incorrectly changed to **redirect** to `/todays-board`, which replaced the welcome landing experience.[1]
- Fix: `dashboard_v1/src/App.tsx` was updated so `/` renders `LandingPage` again (no redirect).[1]
- `ContactDetail` was changed visually (user not thrilled) but is currently tolerated and should not be further churned until landing/dashboard stability is achieved.[1]

## Dashboard_v1 pages (routes → components)
These are the “known-good” pages and where they live right now.[1]

- `/` → `dashboard_v1/src/components/LandingPage.tsx`  
  - This is the **welcome** page: “Good morning/afternoon/evening, Chris” + quick action tiles (Contacts / Analytics / Cold Call / etc).[1]
- `/todays-board` → `dashboard_v1/src/components/TodaysBoard.tsx`  
  - There are multiple versions floating around; the preferred “original” version was captured as a backup file: `TodaysBoard.tsx.backup-20251215_161810`.[1]
- `/contacts` → `dashboard_v1/src/components/ContactsView.tsx`[1]
- `/contacts/:id` → `dashboard_v1/src/pages/ContactDetail.tsx`[1]

(There are also backend endpoints for analytics/smart-lists/cold-call queue; UI routes may exist depending on which App.tsx is active.)[1]

## Backend API endpoints Dashboard_v1 relies on (primary)
From `api.py` (and/or the `appsbackend` app), these endpoints exist and should be treated as canonical for Dashboard_v1 wiring.[1]

- `GET /api/contacts` (contacts list)[1]
- `GET /api/contacts/{id}` (single contact)[1]
- `POST /api/contacts/{id}/enrich` (enrichment)[1]
- `GET /api/todays-board` (aggregated stats/segments for board)[1]
- `GET /api/analytics` (counts, rates, match tiers, personas, etc.)[1]
- `GET /api/smart-lists` (precomputed list counts)[1]
- `GET /api/cold-callqueue` (queue feed)[1]
- `GET /api/userprofile?userid=default` (profile/preferences; used by Dashboard_v1 helpers)[1]

Also present: `/api/v2/contacts/*` routes for newer v2 patterns in `appsbackend/api/routes/contactsv2.py` + enrichment routes in related modules; some Dashboard_v1 helpers reference these.[1]

## Frontend API config (important)
There are multiple env var names in use across Dashboard_v1:
- `dashboard_v1/src/config/api.ts` prefers `VITE_APEX_API_URL` (or similar) with fallback to `VITE_API_URL`, and defaults to the Render backend URL if unset.[1]
- Some older components hardcode `https://apex-backend-i7b0.onrender.com` directly.[1]
Action in next thread: consolidate on **one** env var and one fetch helper to reduce breakage.[1]

## High-risk repo state warning
Local working tree showed **many staged deletions/untracked scripts** during the incident; do not commit unrelated deletions.[1]
Recommended guardrail in next thread: before any deploy, run:
- `git status` (must be clean except intended files)[1]
- commit only the minimal frontend files required (usually `dashboard_v1/src/App.tsx` + 1 component).[1]

## “Known good” landing behavior (definition)
Landing page must be:
- Route: `/` (no redirect)[1]
- Component: `LandingPage.tsx` (welcome greeting + 6 quick actions)[1]

## Next thread first actions (surgical, ROI)
- Confirm current `dashboard_v1/src/App.tsx` routes in main branch match:
  - `/` → `LandingPage`
  - `/todays-board` → `TodaysBoard`
  - `/contacts` → `ContactsView`
  - `/contacts/:id` → `ContactDetail`[1]
- Freeze `ContactDetail` for now (no cosmetic churn).[1]
- Add a simple “version marker” comment at top of LandingPage + TodaysBoard to prevent confusion during future edits (timestamp + purpose).[1]

If you want, paste the **current** `dashboard_v1/src/App.tsx` and `dashboard_v1/src/components/LandingPage.tsx` into the new thread and I’ll lock them down with a minimal, testable deploy script that only touches those files.

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_747aeb83-8e6a-4566-b2b1-733b8db8bda4/9c031784-5364-447d-8305-ec160d110728/paste.txt)