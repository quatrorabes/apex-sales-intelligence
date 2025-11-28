APEX Intelligence Platform - Project Status & Technical Documentation
Date: November 27, 2025
Status: Active Development - Frontend Debugging Phase

📁 Project Structure
text
/Users/chrisrabenold/projects/apex/
├── api.py                          # Main Flask API server (runs on port 8000)
├── apex.db                         # SQLite database (200 contacts)
├── config.py                       # Configuration (needs DB_PATH)
├── .env                            # Environment variables (API keys)
│
├── apps/backend/intelligence/engines/
│   ├── enrichment/
│   │   └── enhanced_enrichment.py  # Perplexity + OpenAI enrichment
│   │
│   ├── scoring/
│   │   ├── apex_intelligence_engine.py
│   │   ├── apex_scoring_engine.py
│   │   ├── scoring_wrapper.py
│   │   └── cadence_router.py
│   │
│   └── outreach/
│       ├── generators/
│       │   ├── __init__.py
│       │   ├── email_generator.py      # ✅ Working (max_tokens=400, line 169)
│       │   ├── call_script_generator.py # ✅ Working (needs whyme_helper)
│       │   ├── linkedin_generator.py    # ✅ Working
│       │   └── whyme_helper.py          # ✅ Created - provides user preferences
│       │
│       ├── auto_sequence_engine.py
│       └── value_matcher.py
│
├── dashboard_v1/src/
│   ├── App.tsx                     # ❌ BROKEN - has duplicate code/syntax errors
│   ├── App.tsx.backup              # Backup before edits
│   │
│   └── components/
│       ├── ContactDetailModal.tsx  # ✅ Working - enrichment + content generation
│       ├── ApexIntelligence.tsx
│       ├── CadenceDashboard.tsx
│       ├── ContactEnrichmentView.tsx
│       ├── RawDataViewer.tsx
│       └── WhyMeTab.tsx
🔧 Key Files & Their Purpose
Backend (Python/Flask)
File	Location	Purpose	Status
api.py	/apex/api.py	Main API server - all endpoints	✅ Working
config.py	/apex/config.py	Config vars	⚠️ Needs DB_PATH added
email_generator.py	.../generators/	Generates 3 email variants	✅ Working
call_script_generator.py	.../generators/	Generates 3 call scripts	✅ Working
linkedin_generator.py	.../generators/	LinkedIn messages + warmup	✅ Working
whyme_helper.py	.../generators/	User preferences for personalization	✅ Created
Frontend (React/TypeScript)
File	Location	Purpose	Status
App.tsx	/dashboard_v1/src/	Main app shell, contacts board	❌ BROKEN
ContactDetailModal.tsx	.../components/	Contact detail, enrich, generate	✅ Working
🗄️ Database Schema
Location: /Users/chrisrabenold/projects/apex/apex.db

Key Tables:

contacts - 200 records with enrichment data, scores, generated content

user_preferences - Why Me? settings for personalization

Key Columns in contacts:

sql
-- Enrichment
profile_content, enrichment_status, enriched_at

-- Scoring  
mdcp_score, mdcp_tier, rss_score, rss_tier, priority_score, urgency_level

-- Generated Content
email_1_subject, email_1_body, email_2_subject, email_2_body, email_3_subject, email_3_body
call_script_1, call_script_2, call_script_3
linkedin_connect, linkedin_followup, linkedin_inmail, linkedin_warmup
🔑 Environment Variables
File: /Users/chrisrabenold/projects/apex/.env

Required:

text
HUBSPOT_ACCESS_TOKEN=xxx
PERPLEXITY_API_KEY=xxx
OPENAI_API_KEY=xxx
Add to config.py:

python
DB_PATH = "/Users/chrisrabenold/projects/apex/apex.db"
🚀 How to Run
Backend
bash
cd /Users/chrisrabenold/projects/apex
source venv/bin/activate
python3 api.py
# Runs on http://localhost:8000
Frontend
bash
cd /Users/chrisrabenold/projects/apex/dashboard_v1
npm run dev
# Runs on http://localhost:5173
✅ What's Working
HubSpot Import - Pulls contacts from HubSpot API

Contact Enrichment - Uses Perplexity + OpenAI for research

Scoring Engine - MDCP, RSS, Priority scoring

Content Generation:

✅ Email (3 variants) - working, may need max_tokens increased to 800

✅ Call Scripts (3 variants) - working

✅ LinkedIn (connect, follow-up, InMail, warmup) - working

ContactDetailModal - Full modal with Intelligence, Dossier, Outreach tabs

Post-Enrich Flow - Modal stays open, shows success celebration

❌ What's Broken
App.tsx - Multiple Issues:
Duplicate Contact interface - Defined twice (lines ~20 and ~260)

Duplicate code blocks - Some sections pasted twice

Missing refreshTrigger state - Referenced but not declared

Intended Features Not Yet Working:
Status badges (○ ✨ 🎯 ✍️) next to contact names

Row highlighting for enriched contacts

Pagination (Load More button)

🔨 To Fix App.tsx
Option 1: Restore and manually add features

bash
cp /Users/chrisrabenold/projects/apex/dashboard_v1/src/App.tsx.backup /Users/chrisrabenold/projects/apex/dashboard_v1/src/App.tsx
Then add these features one at a time:

Add refreshTrigger state to App component

Add ContactStatusBadge component

Add badge to contact name cell

Pass refreshTrigger to ContactsBoard

Option 2: Get fresh working App.tsx
The original working file (before my edits) should be in git:

bash
cd /Users/chrisrabenold/projects/apex
git checkout dashboard_v1/src/App.tsx
📋 Remaining Tasks
Immediate (to fix current state):
 Fix App.tsx syntax errors

 Test full flow: Import → Enrich → Score → Generate Content

Short-term:
 Add status badges to contact rows

 Add pagination (Load More)

 Increase email max_tokens to 800 (line 169 of email_generator.py)

Medium-term:
 Cadence system - auto-sequencing

 Show selected contact on Apex Intelligence page

 Railway deployment

🧪 Testing Commands
bash
# Test generators
python3 -c "from apps.backend.intelligence.engines.outreach.generators.email_generator import generate_email_variants; print('✅ Email OK')"

python3 -c "from apps.backend.intelligence.engines.outreach.generators.call_script_generator import UnifiedCallScriptGenerator; print('✅ Call OK')"

python3 -c "from apps.backend.intelligence.engines.outreach.generators.linkedin_generator import generate_linkedin_content; print('✅ LinkedIn OK')"

# Test API
curl http://localhost:8000/api/health
curl http://localhost:8000/api/contacts?limit=5 | python3 -m json.tool

# Check database
sqlite3 apex.db "SELECT COUNT(*) FROM contacts;"
sqlite3 apex.db "SELECT id, name, enrichment_status FROM contacts LIMIT 5;"
📝 Key API Endpoints
Endpoint	Method	Purpose
/api/contacts	GET	List contacts (supports ?limit=&offset=)
/api/contacts/<id>	GET	Single contact
/api/contacts/<id>/enrich	POST	Enrich contact
/api/contacts/<id>/generate-content	POST	Generate email/call/LinkedIn
/api/hubspot/import	POST	Import from HubSpot
/api/contacts/<id>/score	POST	Score single contact
/api/contacts/score-batch	POST	Batch scoring
/api/user-preferences	GET/POST	Why Me? settings
🔗 External Services
Service	Purpose	Config Location
HubSpot	CRM data source	.env - HUBSPOT_ACCESS_TOKEN
Perplexity	Contact research	.env - PERPLEXITY_API_KEY
OpenAI	Content generation	.env - OPENAI_API_KEY
LinkMatch Pro	LinkedIn automation (subscribed)	Not yet integrated
💡 Notes for Next Session
Priority: Fix App.tsx - either restore from git or rebuild clean

The ContactDetailModal.tsx is solid - don't touch it

Backend is stable - all generators working

200 contacts in database - some already enriched with content

LinkMatch Pro subscription - could be integrated for LinkedIn automation

