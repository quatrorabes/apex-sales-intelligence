# 🧵 APEX SALES INTELLIGENCE - THREAD HANDOFF

## Project Overview

**Apex** is an AI-powered sales intelligence platform that enriches contact data with comprehensive research, personality analysis (MBTI/DISC), and sales opportunity insights.

**Architecture:**
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Dashboard_v1   │────▶│    api.py       │────▶│   Perplexity    │
│  (React/Vite)   │     │  (Flask:8000)   │     │   + GPT-4o      │
│  localhost:3000 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    apex.db      │
                        │    (SQLite)     │
                        └─────────────────┘
```

***

## File Locations

| Component | Path |
|-----------|------|
| **API Server** | `~/projects/apex/api.py` |
| **Database** | `~/projects/apex/apex.db` |
| **Dashboard** | `~/projects/apex/dashboard_v1/` |
| **Contact Detail Page** | `~/projects/apex/dashboard_v1/src/pages/ContactDetailPage.tsx` |
| **Environment Variables** | `~/projects/apex/.env` |
| **Saved Profiles** | `~/projects/apex/enrichment_profiles/` |

***

## Current Enrichment Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                    ENRICHMENT PIPELINE v3.0                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  STAGE 1A: Perplexity - PERSON RESEARCH        (~5-6K chars)    │
│  ├─ Career history, education, achievements                      │
│  ├─ LinkedIn activity, speaking engagements                      │
│  └─ Professional philosophy, board positions                     │
│                                                                  │
│  STAGE 1B: Perplexity - COMPANY RESEARCH       (~5-6K chars)    │
│  ├─ Business model, products, services                           │
│  ├─ Market position, competitors                                 │
│  └─ Recent news, leadership, culture                             │
│                                                                  │
│  STAGE 1C: Perplexity - SALES INTELLIGENCE     (~5-6K chars)    │
│  ├─ Industry trends, pain points                                 │
│  ├─ Buying triggers, budget cycles                               │
│  └─ Competitive pressures, opportunities                         │
│                                                                  │
│  ═══════════════════════════════════════════════════════════    │
│  TOTAL RAW RESEARCH: ~17,000 characters (PRESERVED)              │
│  ═══════════════════════════════════════════════════════════    │
│                                                                  │
│  STAGE 2: GPT-4o - PERSONALITY ONLY (APPENDED) (~1-2K chars)    │
│  ├─ MBTI Assessment with evidence table                          │
│  ├─ DISC Profile with percentages                                │
│  └─ Communication Playbook (Do's/Don'ts)                         │
│                                                                  │
│  ═══════════════════════════════════════════════════════════    │
│  FINAL OUTPUT: ~19,000 characters                                │
│  ═══════════════════════════════════════════════════════════    │
└──────────────────────────────────────────────────────────────────┘
```

**Key Decision:** GPT was compressing 17K → 5K chars (70% data loss). We now use GPT ONLY for personality inference, appending ~1-2K to the raw research.

***

## Data Format

The enrichment output uses `=== SECTION ===` markers:

```
=== PERSON RESEARCH: {name} ===

# {name}: {title} at {company}

## Current Role and Responsibilities
...

## Career History
...

## Education & Credentials
...

=== COMPANY RESEARCH: {company} ===

## Company Overview
...

## Products & Services
...

=== SALES INTELLIGENCE ===

## Industry Trends
...

## Pain Points
...

=== PERSONALITY ANALYSIS ===

## Myers-Briggs (MBTI) Assessment
**Inferred Type:** ENTJ
**Confidence:** Medium

| Dimension | Preference | Evidence |
|-----------|------------|----------|
| Energy | E | Leadership roles... |
...

## DISC Profile Assessment
...

## Communication Playbook
### ✅ DO:
### ❌ DON'T:
```

***

## Dashboard UI Design

**Design System:** Huly-inspired dark theme

| Token | Value | Usage |
|-------|-------|-------|
| `bg.app` | `#0f1114` | Page background |
| `bg.surface` | `#1a1d21` | Cards |
| `bg.subsection` | `rgba(255,255,255,0.02)` | Subsection cards |
| `text.primary` | `#f5f5f5` | Headings |
| `text.secondary` | `#9ca3af` | Body text |
| `accent.blue` | `#3b82f6` | Links, Professional tab |
| `accent.green` | `#22c55e` | Success, Enriched badge |
| `accent.orange` | `#f97316` | Sales tab, warnings |

**UI Pattern:** Subsection cards with:
- Subtle background shading
- Section header with icon + gradient line
- Data rows (label/value pairs) like Huly contact cards

***

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/contacts` | GET | List contacts (paginated) |
| `/api/contacts/<id>` | GET | Get single contact |
| `/api/contacts/<id>/enrich` | POST | Trigger enrichment |
| `/api/contacts/<id>/enrichment-status` | GET | Poll enrichment status |
| `/api/contacts/<id>/reset-enrichment` | POST | Reset to re-enrich |
| `/api/todays-board` | GET | Dashboard summary |

***

## Environment Variables (.env)

```bash
PERPLEXITY_API_KEY=pplx-xxxxx
OPENAI_API_KEY=sk-xxxxx
HUBSPOT_ACCESS_TOKEN=pat-xxxxx  # Optional
```

***

## Recent Fixes Applied

| Issue | Fix |
|-------|-----|
| `gpt-4-turbo` 8000 max_tokens error | Changed to `gpt-4o` with `max_tokens=4096` |
| `llama-3.1-sonar-large-128k-online` 400 error | Changed to `sonar` model |
| GPT destroying 70% of data | GPT now APPENDS personality only |
| Single Perplexity query = weak results | Now 3 queries: Person, Company, Sales |
| Parser truncating at section boundaries | Updated parser for `=== SECTION ===` format |
| 2-space vs 4-space indentation errors | Standardized to 4-space |

***

## Known Issues / Next Steps

### 🔴 To Fix
1. **Outreach tab** - Currently placeholder, needs AI sequence generation
2. **MDCP Score** - Shows 0, needs scoring logic connected
3. **LinkedIn URL** - Should be clickable link in UI

### 🟡 To Improve
1. **Personality confidence** - Could improve evidence gathering
2. **Error handling** - Add retry logic for API failures
3. **Caching** - Consider caching Perplexity results

### 🟢 Future Features
1. **Bulk enrichment** - Enrich multiple contacts at once
2. **Export** - PDF/CSV export of profiles
3. **HubSpot sync** - Push enrichment back to HubSpot
4. **Email generation** - AI-written outreach based on profile

***

## Commands to Run

```bash
# Start API server
cd ~/projects/apex && python api.py

# Start Dashboard
cd ~/projects/apex/dashboard_v1 && npm run dev

# View saved profiles
ls -la ~/projects/apex/enrichment_profiles/

# Check latest profile
cat ~/projects/apex/enrichment_profiles/$(ls -t ~/projects/apex/enrichment_profiles/ | head -1)
```

***

## Key Code References

### Perplexity Model (api.py)
```python
"model": "sonar",  # NOT llama-3.1-sonar-large-128k-online
```

### GPT Model (api.py)
```python
model="gpt-4o",
max_tokens=2000,  # Small call for personality only
```

### Content Parser (ContactDetailPage.tsx)
```typescript
const personMatch = content.match(/=== PERSON RESEARCH:[^=]*===([\s\S]*?)(?====|$)/);
const companyMatch = content.match(/=== COMPANY RESEARCH:[^=]*===([\s\S]*?)(?====|$)/);
const salesMatch = content.match(/=== SALES INTELLIGENCE ===([\s\S]*?)(?====|$)/);
const personalityMatch = content.match(/=== PERSONALITY ANALYSIS ===([\s\S]*?)(?====|$)/);
```

***

## Sample Enriched Contact

**Greg Richter** - CEO at Medalist Partners
- Person research: Career from Prudential → Credit Suisse → Candlewood → Medalist
- Company research: $2B AUM alternative credit manager
- Sales intel: Industry trends, regulatory pressures, tech modernization needs
- Personality: ENTJ, D/C DISC profile
- **Total profile: ~19,000 characters**

***

## Thread Summary

This session focused on:
1. Fixing API errors (model names, token limits)
2. Optimizing the enrichment pipeline (3 queries, preserve all data)
3. Building Huly-style UI with subsection cards
4. Creating proper content parser for new data format

**The system is now shipping production-quality 19K character profiles.**

***

*Handoff created: December 4, 2025, 1:35 PM PST*