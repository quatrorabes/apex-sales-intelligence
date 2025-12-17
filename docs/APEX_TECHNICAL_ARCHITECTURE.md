# APEX SALES INTELLIGENCE - COMPLETE TECHNICAL ARCHITECTURE
## December 16, 2025

---

# SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           APEX SALES INTELLIGENCE                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   FRONTEND (Vercel)                    BACKEND (Render)                         │
│   ══════════════════                   ═════════════════                        │
│                                                                                  │
│   dashboard_v1/                        apps/backend/                            │
│   ├── src/                             ├── main.py (FastAPI app)                │
│   │   ├── pages/                       ├── api/                                 │
│   │   │   └── ContactDetailPage.tsx    │   └── routes/                          │
│   │   ├── components/                  │       ├── contacts.py                  │
│   │   │   ├── ContactsView.tsx         │       └── enrichment.py ◄── ENRICHMENT │
│   │   │   ├── ContactDetailModal.tsx   ├── services/                            │
│   │   │   └── ...                      │   └── enrichment_integration.py        │
│   │   └── config/                      ├── enrichment_engine.py ◄── AI ENGINE   │
│   │       └── api.ts                   └── ...                                  │
│   └── ...                                                                        │
│                                                                                  │
│   URL: apex-sales-intelligence.        URL: apex-backend-i7b0.                  │
│         vercel.app                           onrender.com                       │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────────┐
                          │   PostgreSQL (DB)    │
                          │   ═══════════════    │
                          │                      │
                          │   contacts table:    │
                          │   - id (UUID)        │
                          │   - name, email...   │
                          │   - enrichment_data  │◄── JSONB
                          │   - enrichment_status│
                          │   - enriched_at      │
                          │                      │
                          └─────────────────────┘
```

---

# FRONTEND FILES (dashboard_v1/)

## Main Application Entry

### `dashboard_v1/src/App.tsx`
```typescript
// React Router setup - routes to different pages
<Routes>
  <Route path="/" element={<ContactsView />} />
  <Route path="/contacts/:id" element={<ContactDetailPage />} />
  <Route path="/today" element={<TodayBoard />} />
  // ... other routes
</Routes>
```

---

## Contacts List View

### `dashboard_v1/src/components/ContactsView.tsx`
**Purpose:** Main contacts table with bulk actions (including enrich)

**Key Function - Bulk Enrich (Line ~217):**
```typescript
const handleBulkAction = async (action: string) => {
    if (selectedIds.size === 0) return;

    if (action === 'enrich') {
        const ids = Array.from(selectedIds).slice(0, 5);

        // CALLS BACKEND BATCH ENRICH
        await fetch(`${API_URL}/api/batch/enrich`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contact_ids: ids })  // ◄── Sends selected IDs
        });

        setNotification({ type: 'success', message: `Enriching ${ids.length} contacts...` });
    }
    // ...
};
```

**Flow:**
1. User selects contacts via checkboxes
2. User clicks "Enrich" from bulk actions dropdown
3. Calls `POST /api/batch/enrich` with `{ contact_ids: [...] }`
4. Shows success notification
5. Refreshes contact list

---

## Contact Detail Page

### `dashboard_v1/src/pages/ContactDetailPage.tsx`
**Purpose:** Full page view of a single contact with enrichment data

**Key Function - Get Sections (Lines 51-61):**
```typescript
function getSectionsFromEnrichment(contact: Contact): SectionsMap {
  // FIXED: Now checks enrichment_data first
  const enrichmentData = (contact as any).enrichment_data;

  if (enrichmentData?.sections?.raw_text) {
    console.log('[APEX v2.1] Using enrichment_data.sections.raw_text');
    return { raw_profile: enrichmentData.sections.raw_text };
  }

  if (enrichmentData?.raw_profile) {
    console.log('[APEX v2.1] Using enrichment_data.raw_profile');
    return { raw_profile: enrichmentData.raw_profile };
  }

  // Fallback to old format
  const enrichment = contact.enrichment || null;
  // ... legacy handling

  return {};
}
```

**Key Function - Fetch Contact:**
```typescript
useEffect(() => {
  fetch(`${API_BASE}/api/contacts/${id}`)
    .then(r => r.json())
    .then(data => {
      const contactData = data.contact || data;
      setContact(contactData);
    });
}, [id]);
```

**Renders:**
- Contact header (name, title, company)
- Contact info (email, phone, LinkedIn)
- Tabs: Sales Intelligence | Outreach | Activity
- Section cards for enrichment data

---

## Contact Detail Modal

### `dashboard_v1/src/components/ContactDetailModal.tsx`
**Purpose:** Popup modal when clicking a contact (alternative to full page)

**Similar to ContactDetailPage but:**
- Uses `profile_content` field (older format)
- Less detailed than full page view
- Modal overlay style

---

## API Configuration

### `dashboard_v1/src/config/api.ts`
```typescript
export const API_URL = import.meta.env.VITE_API_BASE_URL 
  || 'https://apex-backend-i7b0.onrender.com';
```

---

# BACKEND FILES (apps/backend/)

## Main Application

### `apps/backend/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from api.routes.contacts import router as contacts_router
from api.routes.enrichment import router as enrichment_router

app = FastAPI(title="APEX Intelligence Platform")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://apex-sales-intelligence.vercel.app", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(contacts_router)
app.include_router(enrichment_router)
```

---

## Enrichment Routes

### `apps/backend/api/routes/enrichment.py`
**Purpose:** All enrichment-related API endpoints

**Key Imports & Setup:**
```python
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
import json

router = APIRouter(tags=["enrichment"])

# Pydantic model for batch requests (FIXED tonight)
class BatchEnrichRequest(BaseModel):
    contact_ids: Optional[List[str]] = None

# Import enrichment engine
from enrichment_engine import EnhancedEnrichment
enrichment_engine = EnhancedEnrichment()
```

**Endpoint: Single Contact Enrich**
```python
@router.post("/api/v2/contacts/{contact_id}/enrich")
async def enrich_v2(contact_id: str):
    """Enrich a specific contact"""
    result = enrich_contact_internal(contact_id)
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error"))
    return result
```

**Endpoint: Batch Enrich (FIXED tonight)**
```python
@router.post("/api/batch/enrich")
async def batch_enrich(
    request: BatchEnrichRequest = None,
    limit: int = Query(1, ge=1, le=5)
):
    """Batch enrichment - accepts contact_ids from Dashboard"""

    # If Dashboard sends specific IDs, use those
    if request and request.contact_ids:
        targets = request.contact_ids[:5]
        logger.info(f"🔄 Enriching {len(targets)} specific contacts from Dashboard")
    else:
        # Auto-select next unenriched contacts
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM contacts WHERE enrichment_status IS NULL..."
            )
            targets = [row["id"] for row in cursor.fetchall()]

    # Enrich each contact
    results = [enrich_contact_internal(cid) for cid in targets]
    return {"status": "complete", "results": results}
```

**Core Function: enrich_contact_internal()**
```python
def enrich_contact_internal(contact_id: str) -> Dict[str, Any]:
    """Internal enrichment logic"""

    # 1. Fetch contact from DB
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()

    # 2. Call enrichment engine
    enrichment_result = enrichment_engine.enrich_contact(dict(contact))

    # 3. Get raw profile text
    raw_profile = enrichment_result.get("profile_text", "")

    # 4. Parse into structured sections
    if PARSER_AVAILABLE:
        enrichment_object = integrate_enrichment_result(raw_profile)
    else:
        enrichment_object = {
            "sections": {"raw_text": raw_profile},
            "metadata": {"format_detected": "raw"}
        }

    # 5. Save to database
    enrichment_json = json.dumps(enrichment_object)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE contacts SET enrichment_status = %s, enrichment_data = %s WHERE id = %s",
            ('completed', enrichment_json, contact_id)
        )
        conn.commit()

    return {"success": True, "contactId": contact_id}
```

---

## Enrichment Engine

### `apps/backend/enrichment_engine.py`
**Purpose:** Calls Perplexity API + GPT-4 to generate enrichment

**Class: EnhancedEnrichment**
```python
class EnhancedEnrichment:
    def __init__(self):
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def enrich_contact(self, contact: dict) -> dict:
        """Main enrichment method"""
        name = contact.get("name", "")
        title = contact.get("title", "")
        company = contact.get("company", "")

        # STAGE 1: Person profile search (Perplexity)
        person_query = f"{name} {title} {company} professional background"
        person_data = self._search_perplexity(person_query)

        # STAGE 2: Company intelligence (Perplexity)
        company_query = f"{company} company overview news funding"
        company_data = self._search_perplexity(company_query)

        # STAGE 3: Sales context (Perplexity)
        sales_query = f"{company} {title} challenges priorities buying"
        sales_data = self._search_perplexity(sales_query)

        # Combine research
        combined_research = f"{person_data}\n\n{company_data}\n\n{sales_data}"

        # STAGE 4: GPT-4 parsing into sections
        profile_text = self._parse_with_gpt4(name, title, company, combined_research)

        return {
            "success": True,
            "profile_text": profile_text,  # ◄── This is the enrichment content
            "sections_count": 9
        }

    def _search_perplexity(self, query: str) -> str:
        """Call Perplexity API"""
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={"Authorization": f"Bearer {self.perplexity_api_key}"},
            json={
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [{"role": "user", "content": query}]
            }
        )
        return response.json()["choices"][0]["message"]["content"]

    def _parse_with_gpt4(self, name, title, company, research) -> str:
        """GPT-4 structures the research into sections"""
        prompt = f"""
        Create a sales intelligence profile for:
        Name: {name}
        Title: {title}
        Company: {company}

        Research:
        {research}

        Format as markdown with these sections:
        ## Overview
        ## Background and Experience
        ## Company Overview
        ## Market Position
        ## Leadership and Culture
        ## Recent Activity and News
        ## Pain Points and Challenges
        ## Budget and Authority
        ## Personality and Communication
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

---

## Enrichment Parser

### `apps/backend/services/enrichment_integration.py`
**Purpose:** Parses GPT-4 output into structured JSON

**Current Implementation (NEEDS IMPROVEMENT):**
```python
def integrate_enrichment_result(raw_text: str) -> dict:
    """Parse enrichment text into structured format"""

    # Currently just wraps in sections.raw_text
    # PROBLEM: Doesn't split into separate section keys
    return {
        "version": "2.0",
        "sections": {
            "raw_text": raw_text  # ◄── Everything in one key
        },
        "metadata": {
            "total_sections": 1,
            "character_count": len(raw_text),
            "format_detected": "unknown"
        }
    }
```

**NEEDS TO BE FIXED TO:**
```python
def integrate_enrichment_result(raw_text: str) -> dict:
    """Parse enrichment text into structured format"""

    sections = {}
    current_section = None
    current_content = []

    for line in raw_text.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].strip().lower().replace(' ', '_')
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    return {
        "version": "2.1",
        "sections": sections,  # ◄── Now has: overview, company_overview, etc.
        "raw_profile": raw_text,
        "metadata": {
            "total_sections": len(sections),
            "character_count": len(raw_text)
        }
    }
```

---

## Contacts Routes

### `apps/backend/api/routes/contacts.py`
**Purpose:** CRUD operations for contacts

**Key Endpoint:**
```python
@router.get("/api/contacts/{contact_id}")
async def get_contact(contact_id: str):
    """Get single contact with all fields including enrichment_data"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Contact not found")

    return {"success": True, "contact": dict(row)}
```

---

# DATABASE SCHEMA

## contacts table
```sql
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hubspot_id VARCHAR(255),
    salesforce_id VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    name VARCHAR(255),  -- computed: first_name + last_name
    email VARCHAR(255),
    phone VARCHAR(255),
    title VARCHAR(255),
    company VARCHAR(255),
    industry VARCHAR(255),
    linkedin_url TEXT,
    vertical VARCHAR(255),

    -- Enrichment fields
    enrichment JSONB,           -- Legacy field
    enrichment_data JSONB,      -- ◄── NEW: Structured enrichment
    enrichment_status VARCHAR(50),  -- 'pending', 'completed', 'failed'
    enriched_at TIMESTAMP,

    -- Scoring fields
    apex_score INTEGER DEFAULT 0,
    mdcp_score INTEGER DEFAULT 0,
    rss_score INTEGER DEFAULT 0,
    priority_score INTEGER DEFAULT 0,
    unified_qualification_score INTEGER,
    qualification_tier VARCHAR(50),

    -- Cadence fields
    cadence_status VARCHAR(50),
    cadence_name VARCHAR(255),
    cadence_step INTEGER,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## enrichment_data JSONB Structure
```json
{
  "version": "2.0",
  "metadata": {
    "total_sections": 1,
    "character_count": 1631,
    "format_detected": "unknown"
  },
  "sections": {
    "raw_text": "## Overview\n- Limited info...\n\n## Company Overview\n..."
  }
}
```

**SHOULD BE (after fix):**
```json
{
  "version": "2.1",
  "metadata": {
    "total_sections": 9,
    "character_count": 1631
  },
  "sections": {
    "overview": "- Limited info available",
    "background_and_experience": "- Limited info available",
    "company_overview": "- TMC Community Capital is...",
    "market_position": "- TMC serves underserved...",
    "pain_points_and_challenges": "- Deal sourcing...",
    // etc.
  },
  "raw_profile": "## Overview\n..."
}
```

---

# DATA FLOW: ENRICHMENT

```
1. USER ACTION
   └── Selects contact(s) in ContactsView.tsx
   └── Clicks "Enrich" button

2. FRONTEND REQUEST
   └── ContactsView.tsx handleBulkAction()
   └── POST /api/batch/enrich
   └── Body: { contact_ids: ["uuid1", "uuid2"] }

3. BACKEND RECEIVES
   └── enrichment.py batch_enrich()
   └── Extracts contact_ids from request
   └── For each ID: calls enrich_contact_internal()

4. ENRICHMENT ENGINE
   └── enrichment_engine.py EnhancedEnrichment.enrich_contact()
   └── Stage 1: Perplexity search - person profile
   └── Stage 2: Perplexity search - company intel
   └── Stage 3: Perplexity search - sales context
   └── Stage 4: GPT-4 parses into markdown sections
   └── Returns: { success: true, profile_text: "## Overview\n..." }

5. PARSER
   └── enrichment_integration.py integrate_enrichment_result()
   └── CURRENTLY: Wraps in { sections: { raw_text: "..." } }
   └── SHOULD: Parse into { sections: { overview: "...", company: "..." } }

6. DATABASE SAVE
   └── UPDATE contacts SET enrichment_data = '{"sections":...}'
   └── SET enrichment_status = 'completed'
   └── SET enriched_at = NOW()

7. FRONTEND FETCH
   └── ContactDetailPage.tsx useEffect()
   └── GET /api/contacts/{id}
   └── Receives: { contact: { ..., enrichment_data: {...} } }

8. DISPLAY
   └── getSectionsFromEnrichment() extracts sections
   └── CURRENTLY: Returns { raw_profile: "entire markdown" }
   └── SHOULD: Returns { overview: "...", company_overview: "..." }
   └── Section cards render each section
```

---

# ENVIRONMENT VARIABLES

## Backend (Render)
```
DATABASE_URL=postgresql://...
PERPLEXITY_API_KEY=pplx-...
OPENAI_API_KEY=sk-...
```

## Frontend (Vercel)
```
VITE_API_BASE_URL=https://apex-backend-i7b0.onrender.com
```

---

# DEPLOYMENT

## Frontend (Vercel)
- Auto-deploys on git push to main
- Build: `cd dashboard_v1 && npm run build`
- Deploy time: ~1 minute

## Backend (Render)
- May need manual deploy trigger
- Dashboard → Service → Manual Deploy → Deploy latest commit
- Deploy time: ~2-3 minutes
- Check logs: Dashboard → Logs tab

---

# TESTING COMMANDS

```bash
# Test API health
curl https://apex-backend-i7b0.onrender.com/

# Get contact with enrichment
curl https://apex-backend-i7b0.onrender.com/api/contacts/f00a5178-840c-4b77-87c3-0d0a2e397b2b | python3 -m json.tool

# Trigger enrichment
curl -X POST https://apex-backend-i7b0.onrender.com/api/batch/enrich \
  -H "Content-Type: application/json" \
  -d '{"contact_ids": ["f00a5178-840c-4b77-87c3-0d0a2e397b2b"]}'

# Check enrichment status
curl https://apex-backend-i7b0.onrender.com/api/contacts/f00a5178-840c-4b77-87c3-0d0a2e397b2b/enrichment-status
```

---

# END OF TECHNICAL ARCHITECTURE
