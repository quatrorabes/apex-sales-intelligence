# APEX Sales Intelligence Platform - Complete Project Summary

## 🎯 Project Overview
**APEX** is an AI-powered contact enrichment and scoring platform specifically designed for Commercial Real Estate (CRE) professionals. It integrates with HubSpot CRM, uses Perplexity AI for enrichment, and implements a sophisticated dual-scoring system (MDCP + RSS) optimized for CRE verticals.

## 🏗️ Current Architecture

### Tech Stack
- **Backend**: Python Flask API (port 8000)
- **Frontend**: React/TypeScript with Vite
- **Database**: SQLite (`~/projects/apex/apex.db`)
- **AI Services**: Perplexity API (enrichment), OpenAI (analysis)
- **Integrations**: HubSpot CRM

### Project Structure
```
~/projects/apex/
├── api.py                      # Main Flask API server
├── apex.db                    # SQLite database
├── .env                        # Environment variables (git-ignored)
├── requirements.txt            # Python dependencies
├── apps/
│   └── backend/
│       └── intelligence/
│           └── engines/
│               ├── enrichment/ # Contact enrichment logic
│               └── scoring/    # CRE-specific scoring engines
│                   ├── scoring_wrapper.py
│                   ├── user_scoring_engine.py
│                   ├── vertical_verifier.py
│                   └── apex_intelligence_engine.py
└── dashboard_v1/               # React frontend
    ├── src/
    │   ├── App.tsx
    │   └── components/
    │       ├── ApexIntelligence.tsx
    │       ├── ContactEnrichmentView.tsx
    │       └── OnboardingModal.tsx
    └── package.json
```

## 📊 Database Schema

### Main Tables
```sql
-- contacts table
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    hubspot_id TEXT,
    name TEXT,
    firstname TEXT,
    lastname TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    company TEXT,
    title TEXT,
    linkedin_url TEXT,
    
    -- Scoring fields
    mdcp_score REAL,           -- Data completeness (0-100)
    mdcp_tier TEXT,            -- HOT/WARM/QUALIFIED/COLD
    rss_score REAL,            -- Role/Seniority Score (0-100)
    rss_tier TEXT,
    priority_score REAL,       -- Combined score (0-100)
    urgency_level TEXT,        -- IMMEDIATE/HIGH/MEDIUM/LOW
    lifecycle_stage TEXT,      -- NEW/WARMING/ACTIVE/ESTABLISHED
    recommended_action TEXT,
    last_scored DATETIME,
    
    -- Enrichment fields
    enrichment_status TEXT,    -- pending/enriched/failed
    enrichment_data TEXT,      -- JSON blob
    perplexity_data TEXT,      -- JSON blob
    
    created_at DATETIME
);

-- user_preferences table (for ICP configuration)
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY,
    user_id TEXT UNIQUE,
    scoring_profile TEXT,      -- CRE_MORTGAGE/CRE_BROKERAGE
    custom_ideal_titles TEXT,  -- JSON array
    custom_avoid_titles TEXT,  -- JSON array
    ideal_company_size_min INTEGER,
    ideal_company_size_max INTEGER,
    target_seniority_levels TEXT,  -- JSON array
    exclude_c_suite INTEGER    -- boolean
);

-- scoring_history table (tracking score changes)
CREATE TABLE scoring_history (
    id INTEGER PRIMARY KEY,
    contact_id INTEGER,
    trigger TEXT,              -- manual/enrichment/batch
    old_score REAL,
    new_score REAL,
    timestamp DATETIME
);
```

## 🔧 Critical Configuration Files

### 1. Environment Variables (.env)
```bash
# HubSpot Configuration
HUBSPOT_TOKEN=your_hubspot_private_app_token

# AI APIs
PERPLEXITY_API_KEY=your_perplexity_key
OPENAI_API_KEY=your_openai_key

# Scoring Configuration
APEX_SCORING_PROFILE=CRE_MORTGAGE
CURRENT_USER_ID=default_user

# API Configuration
FLASK_ENV=development
FLASK_DEBUG=1
```

### 2. API Endpoints (api.py)
```python
# Key endpoints:
POST /api/hubspot/import         # Import contacts with CRE filtering
POST /api/contacts/:id/enrich    # AI enrichment via Perplexity
POST /api/contacts/:id/score     # Individual scoring
POST /api/contacts/score-batch   # Batch scoring (50 at a time)
GET  /api/contacts               # List all contacts
GET  /api/apex/scores           # Get scored contacts for dashboard
POST /api/user/onboarding       # Save ICP preferences
```

## 🎯 Scoring System Details

### Dual Scoring Architecture
The system uses two complementary scoring mechanisms:

#### 1. **RSS (Role/Seniority Score) - 70% weight**
Evaluates if the person is the right fit based on:
- **Vertical Match**: Are they in CRE? (broker, lender, developer)
- **Title Level**: VP, SVP, Director get high scores
- **Department Exclusions**: HR, Marketing, IT automatically scored low

#### 2. **MDCP (Multi-Dimensional Contact Profile) - 30% weight**
Measures data completeness:
- Company info: +15 points
- Email address: +15 points
- Phone number: +10 points
- LinkedIn URL: +10 points
- Enrichment data: +10 points

#### Priority Score Calculation
```python
priority_score = (rss_score * 0.7) + (mdcp_score * 0.3)
```

### CRE-Specific Scoring Engine (user_scoring_engine.py)
```python
class UserSpecificScoringEngine:
    def calculate_personalized_rss(self, contact: Dict) -> Dict:
        # STEP 1: Check excluded departments (HR, Marketing, etc.)
        # STEP 2: Check target verticals (CRE brokers, lenders)
        # STEP 3: Score based on title level within vertical
        # STEP 4: Apply bonuses for high-value companies
```

**Scoring Hierarchy**:
1. **EXCLUDED** (HR, Marketing, Legal) → 10 points ❌
2. **WRONG VERTICAL** (Not in CRE) → 25 points ❌
3. **RIGHT VERTICAL, Unknown Title** → 40-50 points ⚠️
4. **RIGHT VERTICAL + Manager** → 65 points ✅
5. **RIGHT VERTICAL + Director** → 75 points ✅
6. **RIGHT VERTICAL + VP** → 85 points ✅✅
7. **RIGHT VERTICAL + SVP** → 90 points ✅✅✅

## 🎨 Frontend Components

### 1. ApexIntelligence.tsx
Main dashboard showing:
- Scored contacts in priority order
- MDCP, RSS, and Priority scores
- Urgency levels (IMMEDIATE/HIGH/MEDIUM/LOW)
- Lifecycle stages
- Action recommendations

### 2. OnboardingModal.tsx
5-step wizard for configuring ICP:
- Step 1: Industry selection
- Step 2: Target verticals (CRE brokers, lenders, etc.)
- Step 3: Ideal titles configuration
- Step 4: Seniority level preferences
- Step 5: Company size preferences

### 3. ContactEnrichmentView.tsx
Shows enrichment status and allows:
- Manual enrichment triggering
- Viewing enrichment results
- Perplexity AI insights display

## ✅ What's Been Accomplished

1. **Built complete Flask API** with HubSpot integration
2. **Implemented CRE-specific scoring** with vertical verification
3. **Created intelligent import filtering** (excludes HR, Marketing, non-CRE)
4. **Developed React dashboard** with real-time scoring display
5. **Added ICP onboarding system** for user preferences
6. **Integrated Perplexity AI** for contact enrichment
7. **Set up Git repository** and pushed to GitHub
8. **Fixed scoring weights** (70% role, 30% data completeness)
9. **Added lifecycle stage tracking**
10. **Implemented batch scoring** for efficiency

## 🚀 What Needs Testing/Implementation

### Immediate Testing Needed:
1. **Auto-rescore after enrichment** - Verify scores update when new data arrives
2. **Scoring accuracy** - Test with various CRE vs non-CRE contacts
3. **Onboarding flow** - Complete setup and verify preferences save
4. **Import filtering** - Import from HubSpot and check filtering works

### Features to Implement:
1. **Score Explainer Component** - Visual breakdown of scoring
2. **Cold Outreach Score (COS)** - New scoring for minimal-info prospects
3. **Enhanced Contact Detail Page** - Better UI with colored action buttons
4. **Auto-rescore trigger** after enrichment
5. **Score evolution timeline** - Track score changes
6. **Smart cold calling queue** - Dedicated tab for outreach

## 📝 Testing Commands

### Start the System:
```bash
# Terminal 1: Start API
cd ~/projects/apex
source venv/bin/activate
python api.py

# Terminal 2: Start Frontend
cd ~/projects/apex/dashboard_v1
npm run dev
```

### Test Scoring:
```bash
# Score single contact
curl -X POST http://localhost:8000/api/contacts/1/score

# Batch score
curl -X POST http://localhost:8000/api/contacts/score-batch \
  -H "Content-Type: application/json" \
  -d '{"limit": 50}'

# Check scores
sqlite3 ~/projects/apex/apex.db "SELECT name, title, rss_score, priority_score FROM contacts ORDER BY priority_score DESC LIMIT 10;"
```

### Test Import:
```bash
# Import from HubSpot (should filter non-CRE)
curl -X POST http://localhost:8000/api/hubspot/import
```

### Test Onboarding:
1. Open dashboard: http://localhost:5173
2. Click "Configure ICP" button
3. Complete 5-step wizard
4. Verify preferences saved:
```bash
sqlite3 ~/projects/apex/apex.db "SELECT * FROM user_preferences;"
```

## 🐛 Known Issues/Fixes

1. **GitHub Access Issue**: Resolved - was router/LAN blocking port 443
2. **Scoring all 90s**: Fixed - was using fallback scoring
3. **MDCP/RSS not showing**: Fixed - field name mismatch in frontend
4. **Import not filtering**: Fixed - added CRE-specific filters

## 🔑 Key Files to Review

1. **scoring_wrapper.py** - Main scoring orchestration
2. **user_scoring_engine.py** - CRE-specific scoring logic
3. **api.py** - All API endpoints
4. **ApexIntelligence.tsx** - Main dashboard component
5. **OnboardingModal.tsx** - ICP configuration

## 📊 Sample SQL Queries

```sql
-- Check scoring distribution
SELECT 
    CASE 
        WHEN priority_score >= 80 THEN 'IMMEDIATE'
        WHEN priority_score >= 65 THEN 'HIGH'
        WHEN priority_score >= 50 THEN 'MEDIUM'
        ELSE 'LOW'
    END as urgency,
    COUNT(*) as count
FROM contacts
WHERE priority_score IS NOT NULL
GROUP BY urgency;

-- Find top CRE prospects
SELECT name, title, company, priority_score
FROM contacts
WHERE priority_score >= 75
ORDER BY priority_score DESC;

-- Check ICP preferences
SELECT * FROM user_preferences WHERE user_id='default_user';
```

## 🎯 Next Thread Focus

The new thread should focus on:
1. **Testing the complete scoring flow** with real contacts
2. **Implementing the auto-rescore** after enrichment
3. **Building the Score Explainer UI** component
4. **Adding the Cold Outreach Score** for minimal-info prospects
5. **Enhancing the contact detail page** with new design

This system is now a functional CRE-focused sales intelligence platform with sophisticated scoring, ready for testing and UI enhancements!