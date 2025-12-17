## **APEX SALES INTELLIGENCE - HANDOFF DOCUMENT**
### **December 15, 2025 - 10:40 PM PST**

***

## **ARCHITECTURE OVERVIEW**

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Vercel)                        │
│              dashboard_v1/ - React + TypeScript + Vite          │
│                    apex-sales-intelligence.vercel.app           │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACKEND (Render)                         │
│              apps/backend/main.py - FastAPI                     │
│              apex-backend-i7b0.onrender.com                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATABASE (Supabase)                      │
│                    PostgreSQL + UUID primary keys               │
└─────────────────────────────────────────────────────────────────┘
```

***

## **WHAT WAS FIXED TONIGHT**

| Issue | Fix | File |
|-------|-----|------|
| GET contact returned int parsing error | Changed `contact_id: int` → `contact_id: str` | `apps/backend/main.py` |
| ContactDetail not reading enrichment | Changed import to `ContactDetailPage.tsx` which reads `contact.enrichment.sections` | `dashboard_v1/src/App.tsx` |
| Section key mismatch | Added fallback mappings (e.g., `sections['1._overview']` → Overview tab) | `ContactDetailPage.tsx` |
| Missing routes (Analytics, ColdCall, SmartLists, Board) | Added routes to App.tsx | `dashboard_v1/src/App.tsx` |
| Analytics crash (`undefined.HIGH`) | Added null safety + API response normalization | `Analytics.tsx` |
| Why We Fit showing "Poor" when ICP=0 | Changed condition to `icpMatch && icpMatch.score > 0`, fallback shows APEX/RSS/MDCP scores | `ContactDetailPage.tsx` |
| Sales Intel empty | Mapped to `6._strategic_context` and `skills_expertise` | `ContactDetailPage.tsx` |
| Raw Data empty | Changed to `JSON.stringify(contact.enrichment, null, 2)` | `ContactDetailPage.tsx` |

***

## **CURRENT ENDPOINT STATUS**

### **Working Endpoints (200 OK)**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/contacts` | GET | List contacts with pagination |
| `/api/contacts/{uuid}` | GET | Get single contact (UUID string) |
| `/api/contacts/{uuid}/enrich` | POST | Trigger enrichment |
| `/api/contacts/{uuid}/score` | POST | Trigger scoring |
| `/api/contacts/{uuid}/icp-match` | GET | Get ICP match data |
| `/api/contacts/{uuid}/generate-email` | POST | Generate email outreach |
| `/api/contacts/{uuid}/generate-linkedin` | POST | Generate LinkedIn message |
| `/api/todays-board` | GET | Dashboard data |
| `/api/analytics` | GET | Pipeline analytics |
| `/api/cold-call/queue` | GET | Cold call queue |
| `/api/smart-lists` | GET | Smart lists |
| `/health` | GET | Health check |

### **Missing/Broken Endpoints**

| Endpoint | Status | Notes |
|----------|--------|-------|
| `/api/contacts/{uuid}/generate-coldcall` | 404 | Frontend calls this but doesn't exist |

***

## **ENRICHMENT DATA STRUCTURE**

Contact enrichment is stored at `contact.enrichment.sections` (NOT `contact.enrichment_data` which is null):

```json
{
  "enrichment": {
    "engine": "apex_custom",
    "version": "2.1",
    "sections": {
      "1._overview": "Company overview...",
      "person_profile": "Person details...",
      "skills_expertise": "Skills...",
      "company_intelligence": "Company intel...",
      "4._market_position": "Market position...",
      "6._strategic_context": "Strategic context...",
      "social_profiles": "Social media...",
      "2._icebreaker_topics": "Icebreakers...",
      "fun_facts": "Fun facts...",
      // ... 25 total sections
    },
    "metadata": {
      "parsed_fields": { "twitter_url": "...", "facebook_url": "..." },
      "total_sections": 25
    }
  }
}
```

***

## **FRONTEND TAB → SECTION MAPPING**

| Tab | Sections Used |
|-----|---------------|
| **Overview** | `1._overview`, `person_profile`, `2._background_(work_history_and_achievements)`, `skills_expertise` |
| **Company** | `company_intelligence`, `4._market_position`, `3._leadership`, `recent_activity` |
| **Sales Intel** | `6._strategic_context`, `skills_expertise`, `2._professional_skills__leadership,_industry_expertise` |
| **Why We Fit** | ICP endpoint OR fallback to `contact.apex_score`, `unified_qualification_score`, `rss_score`, `mdcp_score` |
| **Outreach** | Calls generate endpoints |
| **Personality** | `social_profiles`, `2._icebreaker_topics` |
| **Raw Data** | Full `JSON.stringify(contact.enrichment)` |

***

## **KEY FILES**

### **Backend**
- `apps/backend/main.py` - All API endpoints (FastAPI)
- `apex_custom_enrichment.py` - Enrichment engine (uses GPT-4o)

### **Frontend**
- `dashboard_v1/src/App.tsx` - Router with all routes
- `dashboard_v1/src/pages/ContactDetailPage.tsx` - Contact detail with tabs
- `dashboard_v1/src/components/TodaysBoard.tsx` - Dashboard
- `dashboard_v1/src/components/Analytics.tsx` - Analytics page
- `dashboard_v1/src/components/ColdCallQueue.tsx` - Cold call queue
- `dashboard_v1/src/components/SmartLists.tsx` - Smart lists
- `dashboard_v1/src/components/OutreachGenerator.tsx` - Email/LinkedIn/ColdCall generation

***

## **REMAINING WORK**

### **HIGH PRIORITY**

1. **Add Cold Call Script endpoint** - Frontend calls `/api/contacts/{id}/generate-coldcall` but returns 404
   ```bash
   grep -n "generate-email" apps/backend/main.py  # Copy pattern, create generate-coldcall
   ```

2. **ICP Configuration** - ICP returns `score: 0` for all contacts. Need to configure ICP criteria in backend.

3. **Scoring Pipeline** - Contacts have scores but Analytics shows `tier_distribution: {HIGH: 0, MEDIUM: 0, ...}`. Need to populate `match_tier` field.

### **MEDIUM PRIORITY**

4. **Start Cadence button** - Untested, may need endpoint wiring

5. **Batch enrichment** - Test bulk enrich from contacts list

6. **GPT-4o migration** - Find and update any remaining `gpt-4` references to `gpt-4o`
   ```bash
   grep -rn "gpt-4" --include="*.py" . | grep -v "gpt-4o"
   ```

### **LOW PRIORITY**

7. **Cleanup backup files** - Many `.backup-*` files in repo

8. **UI polish** - Markdown rendering (remove `**` formatting artifacts)

***

## **TESTING CHECKLIST**

```bash
# Test all major endpoints
curl -s "https://apex-backend-i7b0.onrender.com/api/contacts?limit=3" | head -50
curl -s "https://apex-backend-i7b0.onrender.com/api/contacts/ef40c46e-1470-4138-beb6-d4be08f73c1f"
curl -s "https://apex-backend-i7b0.onrender.com/api/todays-board" | head -50
curl -s "https://apex-backend-i7b0.onrender.com/api/analytics"
curl -s "https://apex-backend-i7b0.onrender.com/api/cold-call/queue"
curl -s "https://apex-backend-i7b0.onrender.com/api/smart-lists"
```

***

## **GIT REPO**
```
https://github.com/quatrorabes/apex-sales-intelligence.git
Branch: main
```

***

## **DEPLOYMENT**

| Service | Platform | Auto-Deploy |
|---------|----------|-------------|
| Frontend | Vercel | Yes (on push to main) |
| Backend | Render | Yes (on push to main) |
| Database | Supabase | N/A |

**Rebuild times:** ~2-3 min for both Vercel and Render after push.

***

## **CONTACT FOR REFERENCE**

Test contact with full enrichment:
- **Name:** Nick Donnelly
- **UUID:** `ef40c46e-1470-4138-beb6-d4be08f73c1f`
- **Status:** Enriched with 25 sections
- **Scores:** APEX: 35, RSS: 50, MDCP: 20, Unified: 14

***

**END HANDOFF - Dec 15, 2025 @ 10:40 PM PST**