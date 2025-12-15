cd ~/projects/apex

# Check what's changed
git status

# Add all changes
git add .

# Commit with a descriptive message
git commit -m "feat: Add content generators and fix enrichment flow

- Add value_matcher.py for product-to-contact matching
- Update linkedin_automation.py with proper indentation
- Update linkedin_sales_nav.py with DB_PATH config
- Update enhanced_enrichment.py with Stage 2 user customization
- Fix ContactDetailModal.tsx handleEnrich to call API directly
- Add user_preferences table with products/services fields
- Update content generation endpoints in api.py"

# Push to GitHub
git push origin main
Or if you're on a different branch:

bash
git push origin your-branch-name
📋 Quick Status Check First
bash
git status
This will show you all modified files. Review them before pushing!

Expected files changed:

✅ api.py

✅ ContactDetailModal.tsx

✅ ContactEnrichmentView.tsx

✅ linkedin_automation.py

✅ linkedin_sales_nav.py

✅ enhanced_enrichment.py

✅ value_matcher.py (new file)

✅ config.py (new file)

Let me know once it's pushed! 🚀

looks good

Excellent! 🎉 Great progress today!

✅ What We Accomplished
Content Generators Module

✅ linkedin_automation.py - fixed indentation & DB path

✅ linkedin_sales_nav.py - fixed indentation & DB path

✅ call_script_generator.py - updated for apex.db

✅ email_generator.py - ready for use

✅ value_matcher.py - NEW product-to-contact matching

Enhanced Enrichment

✅ Stage 1: Perplexity (open-ended research)

✅ Stage 2: GPT-4 polish with user's products/services

User Preferences

✅ Database table with 5 products, 5 services, 5 values, etc.

✅ Ready for onboarding modal integration

Dashboard Fixes

✅ Fixed ContactDetailModal.tsx - Enrich button now calls API

🎯 Next Session To-Do
Wire Content Generation buttons - Email, Call, LinkedIn in Content tab

Update OnboardingModal - Add products/services step

Chat Things tab - Display parsed strategic intelligence (Pain Points, Product Fit, Key Insights)

Test full enrichment flow - Perplexity → GPT-4 → Dashboard

🧪 Quick Test Before You Stop
Try enriching a contact:

Open dashboard

Click on a contact

Click "Enrich" button

Watch backend logs for Stage 1 & Stage 2

You should see the full enrichment with YOUR products in Section 10!

Great session! 🚀

## 📋 APEX Thread Handoff Summary - November 26-27, 2025

***

### 🎯 Project: APEX AI-Powered Contact Enrichment & Scoring Platform

***

## ✅ Completed Work

### 1. Content Generator Modules (Backend)

**Location:** `apps/backend/intelligence/engines/outreach/generators/`

| File | Status | Description |
|------|--------|-------------|
| `linkedin_automation.py` | ✅ Fixed | Fixed indentation, added DB_PATH from config, added `_add_default_templates()` method |
| `linkedin_sales_nav.py` | ✅ Fixed | Fixed indentation, added DB_PATH from config |
| `call_script_generator.py` | ✅ Ready | Updated to use apex.db |
| `email_generator.py` | ✅ Ready | Generates 3-email sequences |
| `value_matcher.py` | ✅ NEW | Matches user's products/services to contact's needs via OpenAI |
| `config.py` | ✅ NEW | Centralized DB_PATH configuration |

***

### 2. Enhanced Enrichment (Two-Stage Pipeline)

**Location:** `apps/backend/intelligence/engines/enrichment/enhanced_enrichment.py`

**Flow:**
```
Stage 1: Perplexity (sonar-pro)
├─ Open-ended research query
├─ NO product mentions (stays generic)
└─ Returns raw profile

Stage 2: GPT-4 Polish
├─ Gets user preferences from DB
├─ Customizes Section 10 (Product Fit) with USER's products
├─ Customizes Section 11 (Key Insights) for product relevance
└─ Returns polished, personalized profile
```

**Key Feature:** User's products/services from onboarding are injected in Stage 2 only, keeping Perplexity research unbiased.

***

### 3. User Preferences System

**Database Table:** `user_preferences`

```sql
CREATE TABLE user_preferences (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id TEXT UNIQUE NOT NULL,
products TEXT,                    -- JSON array (up to 5)
services TEXT,                    -- JSON array (up to 5)
value_propositions TEXT,          -- JSON array (up to 5)
target_customers TEXT,            -- JSON array (up to 5)
personal_differentiators TEXT,    -- JSON array (up to 5)
company_differentiators TEXT,     -- JSON array (up to 5)
industry TEXT,
target_verticals TEXT,
ideal_titles TEXT,
avoid_titles TEXT,
min_company_size INTEGER,
max_company_size INTEGER,
seniority_levels TEXT,
exclude_c_suite INTEGER DEFAULT 0,
created_at TEXT,
updated_at TEXT
);
```

**New Columns in `contacts` table:**
- `product_match TEXT`
- `match_reasoning TEXT`
- `user_can_override INTEGER DEFAULT 1`

***

### 4. API Endpoints Added

**Location:** `api.py` (root)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/user/preferences` | GET | Retrieve user preferences |
| `/api/user/preferences` | POST | Save user preferences |
| `/api/contacts/<id>/enrich` | POST | Trigger two-stage enrichment |
| `/api/contacts/<id>/generate-content` | POST | Generate emails/calls/LinkedIn |
| `/api/contacts/<id>/match-product` | POST | Match products to contact needs |

***

### 5. Frontend Updates

**Files Modified:**

| File | Changes |
|------|---------|
| `ContactDetailModal.tsx` | Fixed `handleEnrich` to call API directly instead of relying on `onEnrich` prop |
| `App.tsx` | Added "Why Me?" tab with full user preferences editor |

**"Why Me?" Tab Features:**
- Products editor (up to 5)
- Services editor (up to 5)
- Value Propositions editor (up to 5)
- Target Customers editor (up to 5)
- Save/Reload buttons
- Instructions panel
- All changes persist to database

***

### 6. Bug Fixes

| Issue | Resolution |
|-------|------------|
| Enrich button not calling API | Changed `handleEnrich` to call API directly |
| `setIsEnriching` undefined | Changed to `setEnriching` (matching state variable) |
| Emoji syntax errors in JSX | Replace emojis with Lucide React icons |
| Special characters (`—`, `×`) | Replace with `-`, `X`, or HTML entities |
| Duplicate imports | Consolidated all Lucide imports into single statement |
| `enrichment_data` parsing | Changed to use `profile_content` directly (string, not JSON) |

***

## 🔧 Architecture Overview

```
User Onboarding → user_preferences table
↓
Contact Selected → Enrich Button
↓
Stage 1: Perplexity (generic research)
↓
Stage 2: GPT-4 + user_preferences
(personalizes Sections 10 & 11)
↓
profile_content saved to contacts table
↓
Content Generation (emails, calls, LinkedIn)
uses matched products from user_preferences
```

***

## 📁 Key File Locations

```
~/projects/apex/
├── api.py                           # Main API (includes new endpoints)
├── apex.db                          # SQLite database
├── dashboard_v1/src/
│   ├── App.tsx                      # Main app with "Why Me?" tab
│   └── components/
│       ├── ContactDetailModal.tsx   # Contact detail view (fixed enrichment)
│       └── OnboardingModal.tsx      # User onboarding
└── apps/backend/intelligence/engines/
├── enrichment/
│   └── enhanced_enrichment.py   # Two-stage enrichment
└── outreach/
└── generators/
├── config.py            # DB_PATH config
├── email_generator.py
├── call_script_generator.py
├── linkedin_automation.py
├── linkedin_sales_nav.py
└── value_matcher.py     # Product matching
```

***

## 🚧 Next Steps / TODO

1. **Wire Content Generation Buttons** - Email, Call, LinkedIn buttons in Content tab
2. **Chat Things Tab** - Display parsed strategic intelligence (Pain Points, Product Fit, Key Insights)
3. **Test Full Enrichment Flow** - End-to-end with user preferences
4. **Add Personal/Company Differentiators** - Add remaining 2 sections to "Why Me?" tab
5. **Manual Product Override** - Allow user to change AI-matched product per contact

***

## 🧪 Testing Commands

```bash
# Start backend
cd ~/projects/apex
python3 api.py

# Start frontend
cd ~/projects/apex/dashboard_v1
npm run dev

# Test user preferences API
curl http://localhost:8000/api/user/preferences

# Test enrichment
curl -X POST http://localhost:8000/api/contacts/1/enrich

# Check database
sqlite3 apex.db "SELECT * FROM user_preferences;"
```

***

## ⚠️ Known Issues

1. **Emoji characters in JSX** - Must use Lucide icons instead of emoji characters
2. **Special characters** - Replace `—` with `-` and `×` with `X` or icon
3. **Import statement** - Don't import `React` separately when using Vite (just use named imports from 'react')

***

**Last Updated:** November 27, 2025, 1:51 PM PST
**Git Status:** Committed to GitHub