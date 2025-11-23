The system is a two-layer sales platform: the newer Apex Sales Intelligence backend + React dashboard sit on top of an earlier “Sales Angel” engine that provides enrichment, scoring, pipeline, cadences, and dashboards.[1][2][3][4]

Below is a handoff-ready, file-by-file and architecture-level summary focused on the Apex stack you are actively using, plus how it relates to the legacy Sales Angel pieces.

***

### High-level architecture

- The **Apex Sales Intelligence Platform** is a FastAPI backend (`main.py`) with a React frontend (`App.tsx`), backed by a local SQLite database (`apex.db`) and a JSON file (`dashboard_data.json`) used as a simple “bridge” store for enriched contact intelligence and generated scripts.[2][5][6][7]
- Enrichment runs through a **Perplexity-based pipeline** (`intelligence/enrichment/perplexity_enrichment.py`) which enriches a given contact ID using Perplexity’s API, then writes normalized output into `dashboard_data.json` via `DashboardBridge`.[6][2]
- Outreach content is produced through an **orchestration layer** (`apex_script_orchestrator.py`) plus simple generators (`email_generator.py`, `call_script_generator_unified.py`) that call OpenAI to create emails and call scripts from the enriched profile.[8][2]
- An older but still available **Sales Angel** system provides a broader CRM layer: contacts, generated_content, outreach cadences, pipeline stages, and analytics, all centered around `sales_angel.db` and Streamlit dashboards (`dashboard.py`, `app.py`, `sales_angel_dashboard.py`) and a Flask API (`api_server.py`).[9][10][3][11][4][1]

***

### Apex backend: `main.py` (FastAPI API)

- `main.py` is the **entrypoint** for the Apex backend API, implemented in FastAPI and exposed on port 3000 with docs at `/docs` and `/redoc`.[7]
- It initializes the SQLite database `apex.db`, creating a **rich `contacts` table** with HubSpot IDs, names, company, multiple scoring fields, enrichment status/JSON, and tracking fields like last_contacted, lifecycle_stage, and lead scores.[7]
- It also creates **`outreach_history`** and **`analytics`** tables for logging sent outreach and generic metrics associated with contacts.[7]
- On startup (`lifespan` context), it calls `init_db()`, checks environment variables such as `PERPLEXITY_API_KEY`, and prints URLs for API documentation.[7]
- The file imports and wires in three major subsystems: the enrichment module (`intelligence.enrichment.enrich_contact`), the dashboard bridge (`hook_after_enrichment` from `dashboard_bridge.py`), and the script orchestration/config manager (`ScriptOrchestrator`, `DashboardConfigManager`).[7]
- It defines REST endpoints such as:  
  - `POST /api/process-enrichment/{contact_id}` – run the full enrichment→dashboard update pipeline.[7]
  - `GET /api/dashboard/{contact_id}` – fetch dashboard-ready intelligence for a contact.[7]
  - `POST /api/refresh-scripts/{contact_id}` – regenerate scripts from existing dashboard data and persist back.[7]
  - `GET /api/business-config` and `PUT /api/business-config` – read/write business-level configuration used during generation.[7]
  - `POST /api/generate-scripts/{contact_id}` – “direct” script generation from enriched data, routed through `ScriptOrchestrator`.[7]

***

### Apex scoring engine: `apex_intelligence_engine.py`

- `apex_intelligence_engine.py` implements the **ApexScoringEngine**, which computes multi-dimensional scores (MDCP and RSS) and an overall priority score/urgency for a contact.[12]
- MDCP scoring breaks into **Money, Decision, Credibility, Pain**, with weightings that vary by lead type (`BANKER`, `CDC`, `BROKER`, `PRIVATE_LENDER`, `BORROWER`) defined in `LeadTypeProfile.PROFILES`.[12]
- RSS scoring measures **Relationship/Signal Strength** using familiarity, engagement, and productivity, and classifies leads into PLATINUM/GOLD/SILVER/BRONZE tiers.[12]
- `score_contact(contact_id, save_to_db=True)` fetches the contact, determines lifecycle stage (`NEW`, `WARMING`, `ACTIVE`, `ESTABLISHED`), runs MDCP + RSS, derives a **priority score and urgency (IMMEDIATE/HIGH/MEDIUM/LOW)**, and optionally writes the result into the `contacts` table’s `opportunity_score`, `lead_tier`, `enrichment_data`, and timestamps.[12]
- The scoring engine uses helper functions like `safe_divide`, `normalize_score`, `calculate_days_between`, plus classification helpers such as `classify_mdcp_tier` and `classify_rss_tier`.[12]

***

### Enrichment & dashboard bridge

#### Perplexity enrichment (referenced module)

- `intelligence/enrichment/perplexity_enrichment.py` (path from docs) connects to Perplexity’s API, running **multi-query person/company searches** and returning structured enrichment data including background, education, company intel, pain points, talking points, personality, and recent activity.[2]
- The enrichment step is triggered when a user hits **“Deep Enrich”** for a contact via the API or UI, which calls the enrichment function on that `contact_id`.[2]

#### `dashboard_bridge.py`

- `dashboard_bridge.py` defines the **DashboardBridge**, which is the glue between raw enrichment output and the front-end–friendly `dashboard_data.json` store.[6]
- `transfer_to_dashboard(contact_id, enrichment_result)` normalizes the enrichment structure for UI display and writes it into `dashboard_data.json` under a key equal to the contact ID as a string.[6]
- `_structure_for_dashboard(enrichment)` flattens and renames fields into a nested object with sections: `contact_info`, `intelligence`, `engagement`, `scoring`, `company_intel`, and `metadata` (including `last_enriched`, a simple `data_quality` rating, and a `completeness` percentage).[6]
- `update_contact(contact_id, dashboard_data)` is used later to save enriched data plus generated scripts back into `dashboard_data.json` once content generation completes.[6]
- `get_dashboard_data(contact_id)` reads `dashboard_data.json` and returns the structured object for a specific contact, which is what the React dashboard consumes.[6]
- `hook_after_enrichment(contact_id, enrichment_result)` is a convenience function the backend calls immediately after enrichment to perform the transfer.[6]

***

### Script orchestration & generators

#### `apex_script_orchestrator.py`

- `apex_script_orchestrator.py` is the **high-level orchestrator** that turns enriched intelligence into industry-specific communication requests, then routes those to OpenAI-backed generators.[8]
- In `__init__`, it loads a **business configuration** (`MY_COMPANY`, `MY_VALUE_PROPOSITION`, `MY_SERVICES`, `MY_TARGET_PERSONAS`, `MY_WRITING_STYLE`) from `my_business_config`, and a `VerticalAgnosticIntelligence` helper from `vertical_intelligence`.[8]
- It initializes an OpenAI client (`OpenAI(api_key=OPENAI_API_KEY)`) and builds internal **“jargon layers”** for verticals like `CRE_BROKER`, `CRE_LENDER`, and `SBA_LENDER`, mapping generic terms to industry language and defining specific terminology and pain-language translations.[8]
- `route_for_generation(enriched_data, target_vertical)` performs:  
  - `_extract_intelligence`: pull name, title, company, recent deals, pain points, trigger events, personality, and a vertical score from the enriched blob.[8]
  - `_match_vertical_to_contact`: infer the best vertical from job title/company (e.g., broker vs bank vs SBA/CDC) with a confidence score.[8]
  - `_apply_jargon_layer`: rewrite pain points and context using vertical-specific terms and jargon.[8]
  - `_get_relevant_config`: select relevant business config and value props for that vertical/persona.[8]
  - `_route_to_generators`: call internal `_generate_email`, `_generate_call_script`, and `_generate_linkedin` to produce vertical-specific messaging.[8]
- `_generate_email` builds a vertical-aware email prompt describing contact, pain points, terminology, and your unique approach, then asks OpenAI GPT‑4 to produce a 60–80‑word email; `_generate_subject_line` returns a vertical-tuned subject line template.[8]
- `_generate_call_script` builds call scripts that incorporate the same vertical context, generating structured call content for use in the UI or over the phone.[8]

#### `email_generator.py` (Apex outreach)

- `email_generator.py` (in `intelligence/outreach`) is a **lightweight generator** focused just on creating three short, professional outreach emails from a contact profile and enrichment summary.[2][8]
- It takes `contact_data` (name, company, title, email) and `enrichment_data` (pain_points, talking_points, etc.), builds a constrained prompt, and uses GPT‑4 with different temperatures to produce three variants labeled professional/balanced/casual.[2][8]
- Output is a list of dicts with `variant`, `subject`, `body`, and `tone`, which the backend stores inside the `generated_scripts` section of the dashboard data.[2]

#### `call_script_generator_unified.py` (Apex outreach)

- `call_script_generator_unified.py` generates a **single structured call script** for a contact, including opener, permission, hook, 3 discovery questions, objection handlers, and a close, tailored by personality (MBTI) and pain points.[2]
- It parses the model’s output into sections, applies fallbacks if parsing fails, and returns an object containing both the full script and the structured `sections` map, plus metadata (`duration_estimate`, `difficulty`, `personality_adapted`).[2]
- As with emails, the result is stored under `generated_scripts.call_scripts` for the given contact in `dashboard_data.json`.[6][2]

***

### Enrichment → dashboard → generation pipeline

- The **end-to-end flow** for a contact is: user triggers “Deep Enrich” → FastAPI calls `enrich_contact(contact_id)` → Perplexity fetches intelligence → `DashboardBridge.transfer_to_dashboard` writes normalized data into `dashboard_data.json` → OpenAI generators create emails and call scripts → `DashboardBridge.update_contact` writes updated `generated_scripts` back → frontend reads and displays everything in the Intelligence Report.[2][6][7]
- Environment variables control keys and behavior, notably `PERPLEXITY_API_KEY` and `OPENAI_API_KEY`, and a flag `AUTO_GENERATE_CONTENT` to choose between auto and manual script generation.[2][7]

***

### React frontend: `App.tsx`

- `App.tsx` is the main React UI entry that renders the **Apex Sales Intelligence dashboard**, including contact list, action buttons, and Intelligence Report view.[5]
- The contact list table includes multi-select checkboxes, sortable headers for name, company, title, opportunity score, status, and actions to trigger enrichment or view intelligence per contact.[5]
- The Intelligence Report section (as designed in docs and handoff) is expected to load a single contact’s record from `/api/dashboard/{id}`, showing `contact_info`, `intelligence`, `engagement`, and `generated_scripts` (emails and call scripts) pulled from `dashboard_data.json`.[5][6][2]

***

### Handoff doc: `THREAD_HANDOFF_NOV20.md`

- `THREAD_HANDOFF_NOV20.md` is the **canonical description of the current Apex system** as of Nov 20, 2025, and should be the first document a new thread reads.[2]
- It summarizes project status (enrichment and dashboard transfer working, script generation ready, LinkedIn enhancement done, content generation configurable) and lists all Apex files with paths under `apex/apps/backend`.[2]
- It documents the **key endpoints**, env vars, step-by-step “How it works”, and a clear next-steps roadmap (fix dashboard display, improve enrichment prompts, scale script generation, and add LinkedIn automation).[2]

***

### Legacy Sales Angel stack (context for new thread)

These files are mostly part of the prior “Sales Angel” platform; they give context and reusable components (pipeline, cadences, dashboards) but are separate from the new Apex+React stack.

#### Pipeline & cadences: `PIPELINE-SYSTEM-README.md`

- Describes a **pipeline/cadence/activity tracking system** with four new tables: `pipeline_stages`, `cadences`, `cadence_steps`, and `contact_cadence_assignments`, plus an enhanced `outreach_activities` table for scoring and next actions.[1]
- Documents five Python modules: `upgrade_db_pipeline.py`, `pipeline_manager.py`, `cadence_engine.py`, `activity_tracker_v2.py`, and `test_complete_system.py`, with examples for moving contacts through stages, assigning cadences by MDCP score, logging activities, forecasting revenue, and listing scheduled touchpoints.[1]

#### Dashboards & crisis fix: `QUICK-START.md`, `DASHBOARD-FIX-GUIDE.md`, `SYSTEM-DELIVERY.md`, `DASHBOARD-FIX-IMMEDIATE.md`

- `QUICK-START.md` is a **5‑minute setup guide** for a Streamlit dashboard (`dashboard.py`) that integrates `loan_email_generator.py`, `loan_call_generator.py`, `sales_angel_db.py`, and `sales_angel_ml.py`, including instructions for `.env`, dependencies, run instructions, and a description of all tabs (Dashboard, Contacts, Generate Content, Review Content, ML Analytics, Settings).[9]
- `DASHBOARD-FIX-GUIDE.md` and `DASHBOARD-FIX-IMMEDIATE.md` explain why `premium_dashboard.py` was broken and prescribe a new simplified dashboard architecture (`dashboard.py`) plus concrete CSS and layout fixes for readability, component layout, and database connectivity.[10][13]
- `SYSTEM-DELIVERY.md` is an **executive-level summary** stating that the Sales Angel system (dashboard.py + generators + DB + ML) is production-ready, with a description of end-to-end behavior (add contacts, generate content, review/feedback, analytics) and an ASCII architecture diagram.[11]

#### API & system overview: `FINAL_HANDOFF_WITH_API.md`

- `FINAL_HANDOFF_WITH_API.md` details a separate **Flask-based REST API** that exposes /api/enrich, /api/content, /api/pipeline, /api/cadence, /api/activity, and /api/analytics endpoints, backed by `sales_angel.db` and a Swagger UI blueprint.[3]
- It includes a complete file list (`api_server.py`, `sales_angel_dashboard.py`, `sales_angel.py`, `download_contacts.py`, `score_leads.py`, `complete_pipeline.py`, `view_enriched.py`) and example curl commands to use the API.[3]

#### Original Sales Angel handoff: `PROJECT_HANDOFF.md`

- `PROJECT_HANDOFF.md` is the **original project handoff** for Sales Angel, summarizing its architecture: HubSpot/CSV/manual inputs, SQLite DB (`contacts`, `generated_content`, `outreach_cadence`, `deals`, `activity_log`), AI processing, Streamlit dashboards, and output integrations.[4]
- It documents core components such as `orchestrate.py` (master workflow), `hubspot_sync.py`, `sales_angel_complete.py` (batch content generation), `app.py` (5‑page Streamlit dashboard), `data_tool.py` (CLI inspector), and `config.py` (company configuration and generation settings).[4]
- It also provides the **SQL schemas** for the main tables (`contacts`, `generated_content`, `outreach_cadence`, `deals`) and a history of problems solved (lost contacts, schema mismatches, content generation filters).[4]

***

### How to brief a new thread

For a new engineer or AI thread, the recommended reading order is:

1. **`THREAD_HANDOFF_NOV20.md`** – current Apex system, file layout, behavior, and priorities.[2]
2. **`main.py`, `dashboard_bridge.py`, `apex_intelligence_engine.py`, `apex_script_orchestrator.py`** – understand how enrichment, scoring, dashboard data, and content generation are wired.[12][6][7][8]
3. **`App.tsx`** – see how the React UI consumes `/api/dashboard/{id}` and is supposed to show intelligence and generated scripts.[5][6][2]
4. **`PIPELINE-SYSTEM-README.md` + `PROJECT_HANDOFF.md`** – background on the broader Sales Angel ecosystem: pipeline, cadences, dashboards, and prior API.[1][4]
5. **`SYSTEM-DELIVERY.md`, `QUICK-START.md`, `DASHBOARD-FIX-GUIDE.md`** – reference if you want to borrow or port proven patterns (Streamlit dashboard, ML feedback loop, generator wiring).[10][11][9]

If you want, the next step can be a short, copy‑pasteable “New Thread Intro” that distills just the Apex subset into a one-page orientation for whoever picks this up next.

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8b36f26b-aa88-498d-829f-3a6b22b9cf5a/366c4127-46d2-4970-8e22-38ebdd2292c5/PIPELINE-SYSTEM-README.md)
[2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/b91ee26c-8aec-4731-9a98-f16a74d246e7/THREAD_HANDOFF_NOV20.md)
[3](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8b36f26b-aa88-498d-829f-3a6b22b9cf5a/c9db32f4-daa3-4953-829d-40cdb9f33400/FINAL_HANDOFF_WITH_API.md)
[4](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8b36f26b-aa88-498d-829f-3a6b22b9cf5a/03bc25f7-7545-42e1-bccf-ea113e72b1f0/PROJECT_HANDOFF.md)
[5](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/027fe467-fa03-499e-a784-c97f44508b4a/App.tsx)
[6](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/fd606d5c-2948-4e38-9a34-37a674b46c4d/dashboard_bridge.py)
[7](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/869c12ef-1790-4898-918a-009b172ac563/main.py)
[8](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/56ceda42-9cf6-44ce-90ad-26d3ee88a7e8/apex_script_orchestrator.py)
[9](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8b36f26b-aa88-498d-829f-3a6b22b9cf5a/9e595878-4299-42e0-8224-1c0370f9175c/QUICK-START.md)
[10](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8b36f26b-aa88-498d-829f-3a6b22b9cf5a/0cb14e4d-f98a-4c3b-9fe7-8858f5504e70/DASHBOARD-FIX-GUIDE.md)
[11](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8b36f26b-aa88-498d-829f-3a6b22b9cf5a/0572e409-a65f-4914-9fc3-2381f2c486cc/SYSTEM-DELIVERY.md)
[12](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/d0e8d145-33a9-42f7-932c-8cb48234aac8/apex_intelligence_engine.py)
[13](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_8b36f26b-aa88-498d-829f-3a6b22b9cf5a/471acb2d-4dfd-440b-9ad9-bf70c0e78556/DASHBOARD-FIX-IMMEDIATE.md)