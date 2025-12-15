# Apex Sales Intelligence - Thread Summary (Dec 7, 2025)

## System Overview

**Apex** is a production AI sales intelligence system with:
- **Backend**: Python Flask API hosted on Railway (`apex-backend-production-production.up.railway.app`)
- **Frontend**: React/TypeScript dashboard hosted on Vercel (`dashboard_v1`)
- **Database**: PostgreSQL on Railway (1,338+ contacts)

***

## Architecture

### Backend (api.py)
- **Location**: `~/projects/apex/apex-sales-intelligence/api.py`
- **Hosting**: Railway with auto-deploy from GitHub
- **Key Environment Variables** (in Railway):
  - `DATABASE_URL` / `DATABASE_PUBLIC_URL`
  - `PERPLEXITY_API_KEY`
  - `OPENAI_API_KEY`
  - `HUBSPOT_ACCESS_TOKEN`

### Frontend (Dashboard_v1)
- **Location**: `~/projects/apex/apex-sales-intelligence/dashboard_v1/`
- **Hosting**: Vercel with auto-deploy from GitHub
- **API URL**: Hardcoded to `https://apex-backend-production-production.up.railway.app`

***

## Key Issues Fixed This Session

### 1. API 500 Errors on Contacts Endpoint
**Problem**: `SELECT *` on 140-column table caused timeouts
**Fix**: Created `CONTACT_COLUMNS` constant with explicit column list (lines ~15-30 in api.py)

### 2. Missing `/api/todays-board` Endpoint
**Problem**: 404 error
**Fix**: Added endpoint returning stats, segments, and top priority contacts

### 3. Contact Detail Page Blank
**Problem**: Field name mismatch - API returns `firstname`/`lastname`, frontend expected `first_name`/`last_name`
**Fix**: Updated `ContactDetail.tsx` in `/components/` (not `/pages/`):
```bash
sed -i '' 's/first_name/firstname/g' ContactDetail.tsx
sed -i '' 's/last_name/lastname/g' ContactDetail.tsx
```

### 4. "Why We Fit" Tab Not Working
**Problem**: API returns `{ data: { ... } }` wrapper, frontend didn't extract it
**Fix**: Changed `setIcpData(data)` to `setIcpData(data.data)` in ContactDetail.tsx line ~544

### 5. Enrichment Data Not Parsing
**Problem**: Parser expected `=== SECTION ===` format but old data used `## Markdown` headers
**Fix**: Updated `extractSection` function (line 100 in ContactDetail.tsx) to handle BOTH formats

### 6. Sales Intelligence Section Missing
**Problem**: Enrichment only made 2 Perplexity calls (person + company)
**Fix**: Added 3rd call for sales intelligence and 4th for personality analysis in api.py:
```python
person_result = call_perplexity(f"Research {name}, {title} at {company}...")
company_result = call_perplexity(f"Research {company}...")
sales_result = call_perplexity(f"Sales intelligence for {name}...")
personality_result = call_perplexity(f"Analyze personality profile of {name}...")

profile_text = f"""=== PERSON RESEARCH: {name} ===
{person_result}

=== COMPANY RESEARCH: {company} ===
{company_result}

=== SALES INTELLIGENCE ===
{sales_result}

### PERSONALITY ANALYSIS
{personality_result}
"""
```

### 7. Playbook URL Mismatch
**Problem**: Frontend called `/api/settings/playbook`, backend had `/api/playbook`
**Fix**: Updated Settings.tsx to use correct URL

### 8. Enrichment Status Check
**Problem**: Frontend checked `enrichment_status === 'enriched'` but API returns `'completed'`
**Fix**: 
```bash
sed -i '' "s/=== 'enriched'/=== 'completed'/g" ContactDetail.tsx
```

### 9. Onboarding Modal Always Showing
**Problem**: Checked `profile.full_name` which didn't exist
**Fix**: Changed to `if (false)` to disable (TodaysBoard.tsx line ~69)

### 10. Pagination Added
**Problem**: Contacts page loaded all 1,338 contacts
**Fix**: Added to ContactsView.tsx:
- State: `page`, `totalContacts`, `pageSize = 50`
- Fetch: `?limit=${pageSize}&offset=${(page-1)*pageSize}`
- UI: Pagination controls at bottom

### 11. HubSpot Integration Added
**Problem**: No HubSpot endpoints existed
**Fix**: Added to api.py:
- `GET /api/hubspot/contacts` - Fetch contacts from HubSpot
- `POST /api/hubspot/sync` - Import HubSpot contacts to database
- Wired up Settings.tsx HubSpot button to call sync

***

## Key Files & Their Purposes

### Backend (api.py)
| Line Range | Function |
|------------|----------|
| ~15-30 | `CONTACT_COLUMNS` - explicit column list |
| ~240-270 | `GET /api/contacts` - paginated contacts list |
| ~498-560 | `POST /api/contacts/{id}/enrich` - 4-call enrichment |
| ~1370-1460 | HubSpot integration endpoints |

### Frontend Components
| File | Purpose |
|------|---------|
| `App.tsx` | Routes, keyboard shortcuts, ImportWizard mount |
| `TodaysBoard.tsx` | Main dashboard with stats |
| `ContactsView.tsx` | Contacts list with table/cards/kanban views, pagination |
| `ContactDetail.tsx` | Contact profile with tabs (Professional, Company, Sales, Personality) |
| `Settings.tsx` | Playbook config, Import, HubSpot sync, API keys |
| `ImportWizard.tsx` | CSV/paste import modal |

### Key Functions in ContactDetail.tsx
| Function | Line | Purpose |
|----------|------|---------|
| `extractSection()` | ~100 | Parses enrichment data by section headers |
| `parseAllSections()` | (varies) | Parses bullet points from sections |
| `parseMBTI()` | (varies) | Extracts Myers-Briggs type |
| `parseDISC()` | (varies) | Extracts DISC profile |
| `parseCommPlaybook()` | (varies) | Extracts DO's/DON'Ts |

***

## Current Playbook Data (Restored)
```json
{
  "companyName": "Harvest Small Business Finance",
  "tagline": "We help small business secure financing...",
  "website": "www.harvestsbf.com",
  "products": [
    {"name": "SBA 504 & 7(a)", "priceRange": "$500k - $5000k"},
    {"name": "Conventional", "priceRange": "$500k - $5000k"}
  ],
  "valueProps": [
    {"headline": "Surety of Execution"},
    {"headline": "Fast close"},
    {"headline": "Flexible Underwriting"}
  ],
  "painPoints": [
    {"problem": "Declined loan"},
    {"problem": "need to close fast"},
    {"problem": "Business cashflow"}
  ],
  "proofPoints": [
    {"title": "Case Study 1"},
    {"title": "90% approval"},
    {"title": "Chris Rabenold has closed many loans"}
  ],
  "competitors": [{"name": "New Day Finance"}]
}
```

***

## Deployment Commands

### Backend (Railway)
```bash
cd ~/projects/apex/apex-sales-intelligence
git add api.py
git commit -m "description"
git push origin main
# Auto-deploys to Railway in ~60-90 seconds
```

### Frontend (Vercel)
```bash
cd ~/projects/apex/apex-sales-intelligence/dashboard_v1
git add -A
git commit -m "description"
git push origin main
# Auto-deploys to Vercel in ~60-90 seconds
```

***

## Testing Commands

```bash
# Health check
curl https://apex-backend-production-production.up.railway.app/api/health

# Contacts list
curl "https://apex-backend-production-production.up.railway.app/api/contacts?limit=5"

# Single contact
curl "https://apex-backend-production-production.up.railway.app/api/contacts/103"

# Enrich contact
curl -X POST "https://apex-backend-production-production.up.railway.app/api/contacts/103/enrich"

# ICP match
curl "https://apex-backend-production-production.up.railway.app/api/contacts/103/icp-match"

# Playbook
curl "https://apex-backend-production-production.up.railway.app/api/playbook"

# HubSpot contacts
curl "https://apex-backend-production-production.up.railway.app/api/hubspot/contacts"

# HubSpot sync
curl -X POST "https://apex-backend-production-production.up.railway.app/api/hubspot/sync"
```

***

## Still Pending / Known Issues

1. **Settings button** - Added to TodaysBoard header (link to /settings)
2. **Import Wizard** - Needs to be wired up in Settings.tsx Import tab
3. **Salesforce integration** - Not implemented (shows "Coming Soon")
4. **Enrichment from ContactsView** - May have 404 (need to verify endpoint URL)

***

## File Locations Summary

```
~/projects/apex/apex-sales-intelligence/
├── api.py                          # Backend API (deployed to Railway)
├── dashboard_v1/
│   └── src/
│       ├── App.tsx                 # Main app, routes, ImportWizard
│       └── components/
│           ├── TodaysBoard.tsx     # Dashboard
│           ├── ContactsView.tsx    # Contacts list + pagination
│           ├── ContactDetail.tsx   # Contact profile (THE MAIN ONE)
│           ├── Settings.tsx        # Playbook, Import, HubSpot
│           └── ImportWizard.tsx    # Import modal
```