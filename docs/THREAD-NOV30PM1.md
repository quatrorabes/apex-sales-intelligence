## 📋 APEX SALES INTELLIGENCE - System Inventory

**Creating comprehensive relay document for handoff...**

***

## APEX SALES INTELLIGENCE - PROGRAMS & ENDPOINTS

***

### **1. Apex Intelligence API Server (`api.py`)**
- **What It Is:** Python Flask backend serving REST API for enrichment, scoring, and contact management.
- **Why Used:** Core engine for Profile Builder, MDCP scoring, and contact lifecycle management.
- **Where Located:** GitHub (projects/apex), Railway deployment.
- **Replaced:** Legacy manual enrichment and static contact lists.
- **Next Steps:** 
- Integrate new scoring modules
- Add monitoring/logging
- Document API endpoints

***

### **2. Dashboard v1 (React Frontend)**
- **What It Is:** React dashboard for Today's Board, Contact Enrichment, Intelligence tabs.
- **Why Used:** Visualize and interact with enriched/scored contacts, drive user actions.
- **Where Located:** GitHub (dashboard_v1), Railway static deployment.
- **Replaced:** Spreadsheet-based tracking and siloed analytics.
- **Next Steps:**
- Add real-time data streaming
- Build integration wizard
- Document UI/UX workflow

***

### **3. Profile Builder (EnhancedEnrichment Class)**
- **What It Is:** Python enrichment engine combining Perplexity and GPT-4 for profile research.
- **Why Used:** Automate contact enrichment and generate structured dossiers.
- **Where Located:** apps/backend/intelligence/engines/enrichment/
- **Replaced:** Manual web research and LinkedIn scraping.
- **Next Steps:**
- Add source attribution
- Build validation pipeline
- Integrate with new data sources

***

### **4. MDCP Scoring Engine (ApexScoringEngine)**
- **What It Is:** Python engine calculating contact scores (MDCP, Priority, RSS).
- **Why Used:** Auto-prioritize contacts and recommend next actions.
- **Where Located:** apps/backend/intelligence/engines/scoring/
- **Replaced:** Manual scoring and static segmentation.
- **Next Steps:**
- Add user feedback loop
- Integrate with outreach performance
- Document scoring logic

***

### **5. Today's Board (Flask Endpoint)**
- **What It Is:** REST endpoint returning prioritized contact lists.
- **Why Used:** Daily action planning for sales teams.
- **Where Located:** api.py (`/api/todays-board`)
- **Replaced:** Static Excel reports.
- **Next Steps:**
- Add user preferences
- Build historical analytics
- Integrate with calendar

***

### **6. Enrichment/Scoring CLI Tools**
- **What It Is:** Python scripts for bulk contact processing.
- **Why Used:** Automate large-scale enrichment and scoring.
- **Where Located:** scripts/ directory.
- **Replaced:** Manual batch processing.
- **Next Steps:**
- Add progress tracking
- Integrate with monitoring
- Document usage patterns

***

### **Summary Table**

| Program/Endpoint           | Type          | Purpose                                   | Location      | Replaced               | Next Steps                     |
|----------------------------|---------------|-------------------------------------------|--------------|------------------------|-------------------------------|
| Apex Intelligence API      | Flask API     | Enrichment, scoring, contact management    | GitHub/Railway | Manual processes       | Integration, docs, monitoring |
| Dashboard v1               | React Frontend| Contact board, enrichment UI              | GitHub/Railway | Spreadsheets           | Real-time, UX docs            |
| Profile Builder            | Python Engine | Automated profile research                 | apps/backend | Manual research        | Validation, attribution       |
| MDCP Scoring Engine       | Python Engine | Contact scoring/prioritization              | apps/backend | Static segmentation    | Feedback loop, docs           |
| Today's Board Endpoint    | Flask API     | Daily prioritized contact list             | api.py       | Static reports         | Analytics, preferences        |
| CLI Tools                  | Python Scripts| Bulk enrichment/scoring                   | scripts/     | Manual batch           | Progress, monitoring          |

***

**Commander, use this as a living document to track progress and planning.** 📝


## **1. APEX API SERVER**

| Attribute | Details |
|-----------|---------|
| **Name** | APEX API (`api.py`) |
| **Type** | Python Flask REST API |
| **Description** | Core backend serving enrichment, scoring, and Today's Board intelligence |
| **Purpose** | Orchestrate contact enrichment (3-stage), MDCP scoring, cadence routing |
| **Location** | `~/projects/apex/api.py` + GitHub: `apex` repo main branch |
| **Endpoints** | `/api/contacts`, `/api/contacts/{id}/enrich`, `/api/todays-board`, `/api/health` |
| **Database** | SQLite (local) / PostgreSQL (Railway production) |
| **Replaced** | Legacy monolithic enrichment script |
| **Status** | ✅ LIVE - Scoring engine initialized tonight |
| **Next Steps** | Deploy fixed version to Railway, test full workflow end-to-end |

***

## **2. ENHANCED ENRICHMENT ENGINE**

| Attribute | Details |
|-----------|---------|
| **Name** | EnhancedEnrichment (inline class in api.py) |
| **Type** | Python class - 3-stage intelligence pipeline |
| **Description** | Profile Builder: Perplexity → GPT-4 → Database save |
| **Purpose** | Generate comprehensive contact profiles with structured intelligence |
| **Location** | Lines 80-360 in `api.py` |
| **Stages** | 1) Perplexity sonar-pro research 2) GPT-4 structuring 3) DB persistence |
| **Output Format** | 12-section markdown profile (Overview, Background, Pain Points, etc.) |
| **Replaced** | Manual research + unstructured enrichment |
| **Status** | ✅ WORKING - Tested on contact #306 (Chris Moritz, Newmark) |
| **Next Steps** | Auto-trigger from UI "Enrich" button, measure API latency |

***

## **3. APEX SCORING ENGINE**

| Attribute | Details |
|-----------|---------|
| **Name** | ApexScoringEngine |
| **Type** | Python class from `apps/backend/intelligence/engines/scoring/` |
| **Description** | MDCP (title + enrichment quality) + Priority scoring |
| **Purpose** | Auto-calculate lead urgency scores post-enrichment |
| **Location** | `apps/backend/intelligence/engines/scoring/apex_scoring_engine.py` |
| **Scores** | MDCP (0-100), Priority (weighted), RSS (placeholder 50.0) |
| **Initialization** | Added to api.py lines 371-379 tonight |
| **Replaced** | Manual scoring system |
| **Status** | ✅ INITIALIZED - Available on health check |
| **Next Steps** | Verify scores populate on enrichment, adjust weighting if needed |

***

## **4. TODAY'S BOARD ENDPOINT**

| Attribute | Details |
|-----------|---------|
| **Name** | `/api/todays-board` |
| **Type** | REST GET endpoint |
| **Description** | Daily prioritized action list - relationships + hot prospects |
| **Purpose** | Display urgent contacts needing action, qualified new prospects |
| **Location** | api.py lines 730-820 |
| **Data Structure** | `{ relationships: { urgent, warm }, new_prospects: { hot, qualified } }` |
| **Filters** | Priority score ≥60, days since contact, enrichment status |
| **Replaced** | Manual Salesforce board review |
| **Status** | ✅ WORKING - Showing 4 hot prospects (Sam Petros 97, others 94) |
| **Next Steps** | Add RSS score integration, implement relationship tiers (nurture, stable) |

***

## **5. DASHBOARD_V1 (React Frontend)**

| Attribute | Details |
|-----------|---------|
| **Name** | Dashboard_v1 |
| **Type** | React + Vite SPA |
| **Description** | Sales intelligence UI - contacts, enrichment, scoring, outreach |
| **Purpose** | User-facing interface for APEX system |
| **Location** | `~/projects/apex/dashboard_v1/` (GitHub) |
| **Tabs** | Today's Board, Contacts, Intelligence, Cadence, Content |
| **API Integration** | All URLs now use `VITE_API_URL` env var (localhost:8000 or Railway) |
| **Replaced** | Legacy Salesforce-only view |
| **Status** | ✅ WORKING - Today's Board displays, Intelligence tab parsing fixed |
| **Updates Tonight** | Fixed NaN warnings, cleaned markdown display, removed duplicate files |
| **Next Steps** | Test enrichment workflow end-to-end, deploy to production |

***

## **6. CONTACT DETAIL MODAL**

| Attribute | Details |
|-----------|---------|
| **Name** | ContactDetailModal.tsx |
| **Type** | React component |
| **Description** | Full contact view with Dossier + Intelligence tabs |
| **Purpose** | Display enriched profile, scoring, outreach content |
| **Location** | `dashboard_v1/src/components/ContactDetailModal.tsx` |
| **Features** | Profile sections (Overview, Background, etc.), Intelligence subtabs (Pain Points, Product Fit, Insights), email/call/LinkedIn templates |
| **Status** | ✅ WORKING - Markdown cleanup applied, section extraction fixed |
| **Replaced** | Static contact cards |
| **Next Steps** | Wire up "Generate Content" button to backend, test copy/paste functionality |

***

## **7. CADENCE DASHBOARD**

| Attribute | Details |
|-----------|---------|
| **Name** | CadenceDashboard.tsx |
| **Type** | React component |
| **Description** | Sequence/cadence management for outreach campaigns |
| **Purpose** | Track multi-touch sequences (emails, calls, LinkedIn) |
| **Location** | `dashboard_v1/src/components/CadenceDashboard.tsx` |
| **Status** | ⚠️ PARTIALLY TESTED - API fixed, needs full integration test |
| **Replaced** | Manual spreadsheet tracking |
| **Next Steps** | Test cadence creation, verify touch recording, check auto-advance logic |

***

## **8. DATABASE SCHEMA**

| Attribute | Details |
|-----------|---------|
| **Location** | `apex.db` (SQLite local) / Railway PostgreSQL (prod) |
| **Tables** | `contacts`, `contact_activities`, `opportunity_signals` |
| **Key Columns** | `id`, `name`, `email`, `company`, `title`, `profile_content`, `priority_score`, `mdcp_score`, `rss_score`, `enrichment_status`, `last_contact_date` |
| **Status** | ✅ Schema verified, 310 contacts with scores |
| **Replaced** | CRM-only data storage |
| **Next Steps** | Add `rss_score` calculation (activity-based), track signal history |

***

## **9. DEPLOYMENT INFRASTRUCTURE**

| Attribute | Details |
|-----------|---------|
| **Production** | Railway (apex-intelligence-production.up.railway.app) |
| **Database** | PostgreSQL on Railway |
| **Local Dev** | SQLite, localhost:8000 (API), localhost:5173 (Dashboard) |
| **Git Workflow** | Push to `origin/main` → Railway auto-deploys |
| **Status** | 🔴 STAGING - Waiting for corrected api.py to deploy |
| **Replaced** | Manual Railway config |
| **Next Steps** | Force new commit to trigger Railway redeploy, verify health check passes |

***

## **🎯 WHAT NEEDS DOING BEFORE YOU LEAVE**

1. ✅ **Force push corrected api.py** - Get Railway deploying working version
2. ⏳ **Wait 60 sec for Railway redeploy** - Check logs for "Scoring: Available"
3. 📊 **Verify production health** - `curl api/health` from Railway
4. 🚀 **Document for home work** - This relay script is your guide

***

## **📝 SAVED FOR TOMORROW**

- **Intelligence Tab Subtabs** - Pain Points, Product Fit showing correctly now ✅
- **Score Displays** - All null-safe with `?? 0` ✅  
- **API Integration** - All using env variables ✅
- **Markdown Cleanup** - Section headers removed from display ✅

***

**Commander, force the new commit now and you're set for home! 🏠** 🚀