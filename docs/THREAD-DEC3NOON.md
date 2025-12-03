## 1. SCRIPT/PROGRAM DETAILS

Apex Sales Intelligence is a production-ready AI sales system with HubSpot sync, enrichment (OpenAI/GPT-4), scoring, cadence generation, and React dashboard. Modular architecture: Backend (Python/Flask/SQLite), Frontend (React/Vite/TypeScript).

### Backend Scripts (~/projects/apex/)
| Name | Purpose | Integration | Implementation Steps |
|------|---------|-------------|----------------------|
| **hubspot_sync.py** | Syncs qualified HubSpot contacts (1,436) with filters (unqualified excluded, name/email/company required). Maps `hs_linkedin_url` → `linkedin_url`, `lifecyclestage` → `lifecycle_stage`. | Calls HubSpot API, upserts to SQLite `contacts`. Triggers enrichment/scoring. CLI: `python hubspot_sync.py` | 1. `pip install requests python-dotenv`. 2. `.env`: `HUBSPOT_ACCESS_TOKEN=your_key`. 3. `chmod +x hubspot_sync.py`. 4. Run: `python hubspot_sync.py` (batches 100, full sync). 5. Logs stats (298 LinkedIn ready). |
| **apex_master_integration.py** | Core Flask API (localhost:8000). Endpoints: `/api/contacts`, `/api/contacts/<id>/enrich`. Handles 2-stage enrichment (data gather + GPT-4 synthesis), upsert to DB. | HubSpot → enrichment → scoring → dashboard. SQLite `./apex.db`. OpenAI GPT-4. | 1. Schema init in code. 2. `python apex_master_integration.py &`. 3. Endpoints: GET/POST `/api/contacts`, enrich triggers pipeline. 4. Logs: "APEX INTELLIGENCE SYSTEM - READY". |
| **api.py** | Alternate API (PostgreSQL/Railway). Enrichment/scoring engine. | Fallback for prod (Railway PG). Similar to master, but PG URL. | 1. `DATABASE_URL=postgresql://...` in .env. 2. `python api.py &` (port 8000). 3. Avoid local (SQLite preferred). |
| **enhanced_enrichment.py** | Stage 1 enrichment (raw data: LinkedIn, company, social). | Called by API enrich. Outputs to `profile_content`. | Integrated in master. Run standalone: `python enhanced_enrichment.py tact_id>`. |
| **apex_8persona_classifier.py** | 8-persona scoring (banker, borrower, etc.). Outputs `persona`, `persona_confidence`. | Post-enrichment, updates DB `persona`. | Integrated. Standalone: `python apex_8persona_classifier.py`. |
| **apex_scoring_engine.py** | Composite scores (MDCP, RSS, priority). | API enrichment → scores → `mdcp_score`, `rss_score`. | Integrated. |
| **call_script_generator.py** | Generates 3 email/call scripts + LinkedIn messages. | Enrichment → `email_1_subject/body`, `call_script_1`. | Integrated. |
| **linkedin_generator.py** | LinkedIn connect/InMail/warmup messages. | Enrichment → `linkedin_connect`, `linkedin_inmail`. | Integrated. |
| **value_matcher.py** | Product-fit scoring (`fit_score`, `match_reasoning`). | Scoring pipeline. |
| **data_flow_pipeline.py** | Orchestrates sync → enrich → score → cadence. | Master cron-like. |
| **auto_sequence_engine.py** | Cadence automation (email/call/LinkedIn sequence). | Dashboard cadence start. |
| **hubspot_service.py** | HubSpot CRUD (sync helper). | Sync uses. |

### Frontend (React/Vite - dashboard/ or apps/dashboard/)
| Name | Purpose | Integration | Implementation Steps |
|------|---------|-------------|----------------------|
| **App.tsx / App_DEC2.tsx** | Main dashboard shell. Tabs: Contacts, Cadence, Intelligence. | Calls API `/api/contacts`, realtime enrichment status. | 1. `cd dashboard`. 2. `npm install`. 3. `npm run dev` (localhost:3000). |
| **CadenceDashboard.tsx** | Cadence visualization/launch. Shows sequences, progress. | API `/api/cadence`. |
| **ApexIntelligence.tsx** | Persona/scores view. Charts, explainers. | API enrichment data. |
| **ContactDetailModal.tsx** | Contact profile: Scores, content (profile_content), scripts. | API `/api/contacts/<id>`. |
| **ContactEnrichmentView.tsx** | Enrichment progress, batch button. | Triggers `/api/contacts/<id>/enrich`. |
| **ActivityTimeline.tsx** | Contact history (touches, cadence). | API activity logs. |
| **ContentGenerator.tsx** | Scripts/InMail generator UI. | Calls generators. |
| **TodaysBoard.tsx** | Daily pipeline: Top prospects by score. | API sorted contacts. |

### Other
| Name | Purpose | Integration | Steps |
|------|---------|-------------|-------|
| **batch_enrich.py** | Batch enrichment pipeline. | CLI batch API calls. | `python batch_enrich.py`. |
| **monitor_enrichment.sh** | Realtime progress monitor. | Loops API status. | `./monitor_enrichment.sh`. |

**Implementation Overview:** Backend Python (Flask/SQLite/OpenAI/HubSpot). Frontend React (Vite/TSX). Start: sync → API → dashboard.

***

## 2. DATABASE FIELD SPECIFICATIONS

**Primary: SQLite `./apex.db`** (local dev/prod fallback). **Railway PostgreSQL** (prod scale).

### SQLite `contacts` Table (1436 rows post-sync)
| Field | Datatype | Constraints/Indexes | Relations/Purpose |
|-------|----------|---------------------|-------------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique DB ID. API uses. |
| name | TEXT | NOT NULL (pre-fix) | Full name ("Michael Allison"). From firstname+lastname. Sync required. |
| email | TEXT | UNIQUE index | Primary key for upsert. HubSpot email. |
| phone | TEXT | - | Primary phone. |
| company | TEXT | - | Company name. Sync required. |
| job_title | TEXT | - | Title. Maps HubSpot `jobtitle`. |
| linkedin_url | TEXT | INDEX idx_linkedin_url | `hs_linkedin_url`. Enrichment key (298 have). |
| ai_prospect_score | REAL | - | AI prospect score. Post-enrichment. |
| ai_confidence | TEXT | - | Confidence level. |
| prospect_score | REAL | - | Overall prospect. |
| lead_score | REAL | - | Lead score. |
| composite_score | REAL | - | Combined score. |
| vip_intelligence_score | REAL | - | VIP intel. |
| borrower_persona_type | TEXT | - | Persona subtype. |
| relationship_persona_type | TEXT | - | Relationship type. |
| persona | TEXT | - | Main persona ("banker"). 8-classifier. |
| primary_persona_tier | TEXT | - | Tier (A/B/C). |
| persona_confidence_score | REAL | - | Confidence (0-100). |
| sales_stage | TEXT | - | Pipeline stage. |
| lead_status | TEXT | INDEX | "NEW", from HubSpot `hs_lead_status`. Filter unqualified. |
| lifecycle_stage | TEXT | INDEX | "lead", from HubSpot `lifecyclestage`. |
| scoring_tier | TEXT | - | A/B/C tier. |
| lead_priority | TEXT | - | Priority. |
| last_contact | DATE | - | Last touch date. |
| last_activity_type | TEXT | - | Email/call. |
| total_touchpoints | INTEGER | - | Touch count. |
| days_since_contact | INTEGER | - | Days cold. |
| days_in_pipeline | INTEGER | - | Pipeline time. |
| enrichment_status | TEXT | INDEX idx_enrichment_status | "pending/completed/failed". Monitors pipeline. |
| enrichment_level | TEXT | - | Basic/full. |
| last_enriched | DATE | - | Timestamp. |
| last_scored | DATE | - | Score time. |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record create. |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Last update. |

**Added Sync Fields:**
| Field | Datatype | Purpose |
|-------|----------|---------|
| hubspot_id | TEXT | HubSpot "156352". |
| firstname | TEXT | First name. |
| lastname | TEXT | Last. |
| phone_mobile | TEXT | Mobile. |
| title | TEXT | Synonym `job_title`. |
| import_source | TEXT | "hubspot". |
| last_crm_sync | TEXT | Sync timestamp. |
| enrichment_ready | INTEGER | 1 if LinkedIn. |

**Enrichment Fields (GPT-4 Output):**
| Field | Datatype | Purpose |
|-------|----------|---------|
| profile_content | TEXT | Full GPT profile (overview + company). |
| overview | TEXT | Contact summary. |
| background | TEXT | Bio. |
| recent_mentions | TEXT | News/social. |
| social_profiles | TEXT | Links. |
| personality_detail | TEXT | Myers-Briggs inferred. |
| mb_summary | TEXT | MBTI. |
| company_overview | TEXT | Company intel. |
| company_products_services | TEXT | Products. |
| company_leadership | TEXT | Leaders. |
| company_market_competitors | TEXT | Competitors. |
| company_recent_news | TEXT | News. |
| company_fun_facts | TEXT | Facts. |
| sales_talking_points | TEXT | Script inputs. |
| deals_history | TEXT | CRM notes. |
| fun_facts | TEXT | Icebreakers. |
| pain_points | TEXT | Objections. |
| talking_points | TEXT | Pitch. |
| rss_score | REAL | Relationship Strength Score. |
| rss_tier | TEXT | PLATINUM/BRONZE. |
| mdcp_score | REAL | Market/Decision/Contact/Pain. |
| mdcp_tier | TEXT | HOT/COLD. |
| priority_score | REAL | Composite. |
| urgency_level | TEXT | HIGH/MEDIUM. |
| persona_multiplier | REAL | 1.00 (persona boost). |
| enrichment_data | TEXT | Raw JSON. |

**Indexes:** `idx_hubspot_id`, `idx_linkedin_url`, `idx_enrichment_status`, `idx_name`.

**Railway PostgreSQL (`contacts` table):** Mirror SQLite + scaling. `DATABASE_URL` in .env. Same fields/constraints. Foreign keys: none (denormalized for speed).

***

## 3. INTEGRATION & CONNECTIVITY

**Flow:** HubSpot API → sync.py → SQLite → API endpoints → Enrichment (OpenAI) → Scoring → Dashboard realtime → Cadence execution.

### Connections
- **HubSpot ↔ sync.py**: Bearer token (.env `HUBSPOT_ACCESS_TOKEN`). POST `/crm/v3/objects/contacts/search` → upsert SQLite.
- **SQLite ↔ API**: Flask ORM (apex_master_integration.py). Upsert uses email primary.
- **API ↔ OpenAI**: GPT-4 (`/chat/completions`). Stage1: scrape LinkedIn/company. Stage2: synthesize → parse → DB.
- **API ↔ Dashboard**: CORS-enabled. GET `/api/contacts?limit=50&sort=priority_score`, POST `/enrich`. WebSockets for realtime.
- **Dashboard ↔ Generators**: Button clicks → API → `call_script_generator.py`, `linkedin_generator.py` → content fields.
- **Cron/Sequences**: `auto_sequence_engine.py` polls DB `enrichment_status='completed'` → cadence start.
- **Scoring Pipeline**: Enrichment → `apex_scoring_engine.py`/`apex_8persona_classifier.py` → scores/persona → `composite_score`.
- **Railway PG**: Prod swap: .env `DATABASE_URL`. Same code.

**Step-by-Step System Flow:**
1. **Sync**: `python hubspot_sync.py` → DB populated (1436).
2. **Enrich**: API `/enrich` → Stage1 (data) → Stage2 (GPT) → Stage3 (parse/save).
3. **Score**: Post-enrich → persona/scores populated.
4. **Dashboard**: `npm run dev` → realtime contacts/scores/cadence.
5. **Cadence**: Click → `auto_sequence_engine.py` → email/LinkedIn auto.

**Dependencies:** `.env` (tokens), `pip install flask requests openai psycopg2-binary python-dotenv httpx`. NPM for dashboard.

**Apex_v1 production!** Full docs → handoff ready. 🚀