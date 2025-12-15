I see the issue clearly now. The **data structure is excellent** (numbered sections, tables, rich content), but the **frontend isn't rendering the markdown properly**. Looking at the Dovetail screenshots, here's what we need to match that world-class look:

***

## RECOMMENDATIONS

### 1. GPT Prompt Refinements

**Current output is good but needs polish:**

```python
# In api.py - Update the GPT prompt to:
# - Remove Section 6 (Outreach) entirely - you have separate scripts
# - Add visual hierarchy with better subheader consistency
# - Ensure tables have clean structure for rendering
```

**Updated prompt structure (5 sections only):**
- `# 1. OVERVIEW` - Executive summary, snapshot table, career highlights
- `# 2. PROFESSIONAL STYLE` - MBTI, DISC, Communication Playbook
- `# 3. COMPANY INTELLIGENCE` - Company overview, products, market position
- `# 4. PAIN POINTS` - Role-specific challenges, industry pressures
- `# 5. SALES INTEL` - Why now, opportunity assessment, strategic insights

### 2. Frontend Rendering Fix

The tables are coming through but **not rendering as styled tables**. The Tailwind prose classes need tweaking:

```tsx
// The markdown tables are rendering as text because 
// react-markdown isn't processing them correctly
// Need to ensure remarkGfm plugin is working
```

### 3. Visual Design Upgrades (Match Dovetail)

| Element | Current | Target (Dovetail-style) |
|---------|---------|------------------------|
| Tables | Plain text | Dark cards with borders |
| Headers | Basic | Azure accent with icons |
| Cards | Single block | Distinct sections with gaps |
| Typography | Uniform | Clear hierarchy |

***

## THREAD SUMMARY FOR HANDOFF

### Project: Apex Sales Intelligence System

**Goal:** Build a production-ready AI sales intelligence platform that enriches contacts with deep research, personality analysis, and sales playbooks.

***

### Architecture Established

```
┌─────────────────────────────────────────────────────────────────┐
│                        APEX PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│  STAGE 1: PERPLEXITY    →  STAGE 2: GPT-4-TURBO  →  STAGE 3: DB │
│  (Raw Research)            (Structure/Polish)        (Store)     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                     DASHBOARD_V1 (React)                         │
├─────────────────────────────────────────────────────────────────┤
│  ContactDetail.tsx parses numbered sections → renders to tabs    │
│  Tabs: Overview | Professional | Company | Pain Points | Sales   │
└─────────────────────────────────────────────────────────────────┘
```

***

### Key Files & Locations

| File | Path | Purpose |
|------|------|---------|
| `api.py` | `/Users/chrisrabenold/projects/apex/api.py` | Flask API + enrichment pipeline |
| `ContactDetail.tsx` | `/projects/apex/dashboard_v1/src/pages/ContactDetail.tsx` | Contact detail view with tabs |
| `apex.db` | `/projects/apex/apex.db` | SQLite database |
| `enrichment_profiles/` | `/projects/apex/enrichment_profiles/` | Saved profile .txt files |
| `.env` | `/projects/apex/.env` | API keys (PERPLEXITY, OPENAI, HUBSPOT) |

***

### Current State (As of Dec 4, 2025 12:15 AM)

**✅ WORKING:**
- HubSpot sync pulling contacts
- Perplexity research (Stage 1)
- GPT-4-Turbo structuring (Stage 2) - fixed token limit by switching from gpt-4
- Database storage (Stage 3)
- Dashboard loads contacts, shows enrichment status
- Tab navigation works
- Profile content is stored with numbered sections

**⚠️ NEEDS WORK:**
- Markdown tables not rendering as styled tables (prose classes issue)
- Section 6 (Outreach) should be blank - separate scripts handle this
- Visual polish to match Dovetail-quality UI
- Tables need dark card styling with proper borders

***

### Data Flow

```
Contact in HubSpot
       ↓
Sync to apex.db (contacts table)
       ↓
User clicks "Enrich Now"
       ↓
API calls Perplexity: "Research {name}, {title} at {company}..."
       ↓
Raw research → GPT-4-Turbo with structured prompt
       ↓
Output: Markdown with # 1., # 2., etc. sections
       ↓
Stored in contacts.profile_content
       ↓
Frontend splits on "# 1.", "# 2.", etc.
       ↓
Each section → Tab content
       ↓
ReactMarkdown + remarkGfm renders tables/lists
```

***

### Profile Output Structure (Current)

```markdown
# 1. OVERVIEW
## 1.1 Executive Summary
## 1.2 Contact Snapshot (TABLE)
## 1.3 Career Highlights
## 1.4 Education & Credentials (TABLE)

# 2. PROFESSIONAL STYLE
## 2.1 Myers-Briggs Assessment (TABLE)
## 2.2 DISC Profile (TABLE)
## 2.3 Communication Playbook (DO/DON'T lists)

# 3. COMPANY INTELLIGENCE
## 3.1 Company Overview (TABLE)
## 3.2 Products & Services (TABLE)
## 3.3 Market Position
## 3.4 Recent Developments (TABLE)

# 4. PAIN POINTS
## 4.1 Role-Specific Challenges (5 challenges)
## 4.2 Industry Pressures

# 5. SALES INTEL
## 5.1 Why NOW?
## 5.2 Opportunity Assessment (TABLE with 🟢/🟡/🔴)
## 5.3 Strategic Insights

# 6. OUTREACH ← REMOVE THIS (handled separately)
```

***

### Frontend Parser (ContactDetail.tsx)

```typescript
// Splits on "# 1.", "# 2.", etc.
const parts = content.split(/(?=^# \d+\. )/m);

// Maps to tabs:
// "1" → overview
// "2" → professional
// "3" → company
// "4" → pain
// "5" → sales
// "6" → outreach (leave blank)
```

***

### Next Steps for New Thread

1. **Fix table rendering** - Ensure `remarkGfm` is working and tables get proper dark styling
2. **Update GPT prompt** - Remove Section 6 (Outreach), refine table structures
3. **Add visual cards** - Each subsection (1.1, 1.2, etc.) should be its own card like Dovetail
4. **Polish typography** - Match the Dovetail design language (clean headers, subtle borders)
5. **Test enrichment** - Run several contacts through to verify consistency

***

### API Keys Required

```env
HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxx
PERPLEXITY_API_KEY=pplx-xxxxx
OPENAI_API_KEY=sk-xxxxx
```

***

### Commands to Run

```bash
# Start API
cd ~/projects/apex && python api.py

# Start Dashboard
cd ~/projects/apex/dashboard_v1 && npm run dev

# Check latest profile
sqlite3 ~/projects/apex/apex.db "SELECT substr(profile_content, 1, 500) FROM contacts WHERE enrichment_status='completed' ORDER BY enriched_at DESC LIMIT 1;"
```

***

**Bottom line:** The data pipeline is solid. The GPT output structure is correct. The issue is **frontend rendering** - tables showing as text instead of styled components. Next thread should focus on making ContactDetail.tsx render the markdown beautifully with proper table styling, card layouts, and visual hierarchy matching the Dovetail screenshots.

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/f74a629c-2834-4cec-9fd7-d56a900a6aa4/Screenshot-2025-12-01-at-12.33.35-AM.jpg?AWSAccessKeyId=ASIA2F3EMEYEV7NL7KLK&Signature=53btOX5dfELlEFfZ15A5fSrZHys%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHgaCXVzLWVhc3QtMSJHMEUCIBXvl3t7ZNGZ%2B6NCD7EOdEWwEx7HfWwnRs6O5Sc%2FHg9MAiEAnkcu9F9vYD9%2BsprFjSGkJEuiTQt61lpkIki8tS3VyoMq8wQIQRABGgw2OTk3NTMzMDk3MDUiDJoiksW92arnfNqduirQBOhBLIY5WvalnptFONUl5Av9fhr9E4gwxqHNXfhOwhogPatgwELCA817EFO9Y9VmR6HMYSUZWCEpw%2FkFmjiPIgICPOt5sM8pzC5Q3bfSpG%2Fv7xxTCHbivkE%2Boxmx%2B13IXaRIYjPlFWKrSxO7Qvk79%2FY28XdV4d4ETvxynhcVjS62vqU7qg%2B2r1cTMXLmv6YIae%2B4mMKDGYVZkI9oBCeMsqQxl4LOiRx63nFxPE6IW8dD3VkrQen8MUTgHObJ0sbTSK%2F9Pq1FGs12q24MnxKcArCvTHhuR5ELLWbZPc%2BrW5ijVWGhGL41K2Jxh5UlyRVfut0BIYCmremYLoObaamisthVKNLDYQWca%2B9TiBwZko8NZFPdm9KsiT2miYzX6CGT%2F2BOyWmkjWYiojMEKhODRNYw7SUSLZCNyiwhEMe6qQsxKBa6H40vGJeaf3ENn2ObFo06gAn53KwRzmR5MJnhA%2B2T%2BCdfrtDrIfC170eoNeCqmeWhm9MDTtwCjwXjKXJd4ayoVz30gPzZ7LQ9loeh%2FQzjb6B7P5u2p9YlesEeB3zutoihnuTFSwCZywPTZ5bNZWOZrQYA47XSHIsZSbuNdCGQ%2BtZKU5LHSenSQzazq1DE3Eldju31dAevAgM49TlNlcR1gk94mZdLQ%2BMjP%2FD0w6ejIaXMklLsk1PMKkIAwW%2FcFRlW61KKdvn5aBSRheGZg2v9kH%2FahS7iTSpZaq04jGqyZMc2yW0keWgWueKkR27%2F4JhV6l%2BoDxKuwD5t0gexl0xjp05%2BXdVLJ807Oa0MBDswsvbEyQY6mAGzUwRIn4Fh8Bvni73G4MuWyKkaPs4PhbKH2LDYKbNzti6drLC8ZvVlelfXFLCopJFw%2BTCxalrrfKv6UeBrL7JD0KWogi%2FdqB27VPdSTeJ7S8L1i7j4afnU5T6twDRobpDZS85SCYo9Ic%2B4xygN9wToJ%2BWMX%2FyvcbWqYHoVJ1Oc6U6UqmlEsbtXKwiS%2BLDmS1plcfBzwsF0FA%3D%3D&Expires=1764836812)
[2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/69d1cf27-c22e-4cc5-aa8e-d7f524b96558/CleanShot-2025-12-03-at-23.59.24-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYEV7NL7KLK&Signature=JMNlKSgg1yXsVxK3aspp%2B3L9Si8%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHgaCXVzLWVhc3QtMSJHMEUCIBXvl3t7ZNGZ%2B6NCD7EOdEWwEx7HfWwnRs6O5Sc%2FHg9MAiEAnkcu9F9vYD9%2BsprFjSGkJEuiTQt61lpkIki8tS3VyoMq8wQIQRABGgw2OTk3NTMzMDk3MDUiDJoiksW92arnfNqduirQBOhBLIY5WvalnptFONUl5Av9fhr9E4gwxqHNXfhOwhogPatgwELCA817EFO9Y9VmR6HMYSUZWCEpw%2FkFmjiPIgICPOt5sM8pzC5Q3bfSpG%2Fv7xxTCHbivkE%2Boxmx%2B13IXaRIYjPlFWKrSxO7Qvk79%2FY28XdV4d4ETvxynhcVjS62vqU7qg%2B2r1cTMXLmv6YIae%2B4mMKDGYVZkI9oBCeMsqQxl4LOiRx63nFxPE6IW8dD3VkrQen8MUTgHObJ0sbTSK%2F9Pq1FGs12q24MnxKcArCvTHhuR5ELLWbZPc%2BrW5ijVWGhGL41K2Jxh5UlyRVfut0BIYCmremYLoObaamisthVKNLDYQWca%2B9TiBwZko8NZFPdm9KsiT2miYzX6CGT%2F2BOyWmkjWYiojMEKhODRNYw7SUSLZCNyiwhEMe6qQsxKBa6H40vGJeaf3ENn2ObFo06gAn53KwRzmR5MJnhA%2B2T%2BCdfrtDrIfC170eoNeCqmeWhm9MDTtwCjwXjKXJd4ayoVz30gPzZ7LQ9loeh%2FQzjb6B7P5u2p9YlesEeB3zutoihnuTFSwCZywPTZ5bNZWOZrQYA47XSHIsZSbuNdCGQ%2BtZKU5LHSenSQzazq1DE3Eldju31dAevAgM49TlNlcR1gk94mZdLQ%2BMjP%2FD0w6ejIaXMklLsk1PMKkIAwW%2FcFRlW61KKdvn5aBSRheGZg2v9kH%2FahS7iTSpZaq04jGqyZMc2yW0keWgWueKkR27%2F4JhV6l%2BoDxKuwD5t0gexl0xjp05%2BXdVLJ807Oa0MBDswsvbEyQY6mAGzUwRIn4Fh8Bvni73G4MuWyKkaPs4PhbKH2LDYKbNzti6drLC8ZvVlelfXFLCopJFw%2BTCxalrrfKv6UeBrL7JD0KWogi%2FdqB27VPdSTeJ7S8L1i7j4afnU5T6twDRobpDZS85SCYo9Ic%2B4xygN9wToJ%2BWMX%2FyvcbWqYHoVJ1Oc6U6UqmlEsbtXKwiS%2BLDmS1plcfBzwsF0FA%3D%3D&Expires=1764836812)
[3](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/fe2a1413-f6ca-4a80-af2d-ffde67aa748c/CleanShot-2025-12-04-at-00.02.18-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYEV7NL7KLK&Signature=P1dbsb5wcyaU%2FUazpDSJree6ckQ%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHgaCXVzLWVhc3QtMSJHMEUCIBXvl3t7ZNGZ%2B6NCD7EOdEWwEx7HfWwnRs6O5Sc%2FHg9MAiEAnkcu9F9vYD9%2BsprFjSGkJEuiTQt61lpkIki8tS3VyoMq8wQIQRABGgw2OTk3NTMzMDk3MDUiDJoiksW92arnfNqduirQBOhBLIY5WvalnptFONUl5Av9fhr9E4gwxqHNXfhOwhogPatgwELCA817EFO9Y9VmR6HMYSUZWCEpw%2FkFmjiPIgICPOt5sM8pzC5Q3bfSpG%2Fv7xxTCHbivkE%2Boxmx%2B13IXaRIYjPlFWKrSxO7Qvk79%2FY28XdV4d4ETvxynhcVjS62vqU7qg%2B2r1cTMXLmv6YIae%2B4mMKDGYVZkI9oBCeMsqQxl4LOiRx63nFxPE6IW8dD3VkrQen8MUTgHObJ0sbTSK%2F9Pq1FGs12q24MnxKcArCvTHhuR5ELLWbZPc%2BrW5ijVWGhGL41K2Jxh5UlyRVfut0BIYCmremYLoObaamisthVKNLDYQWca%2B9TiBwZko8NZFPdm9KsiT2miYzX6CGT%2F2BOyWmkjWYiojMEKhODRNYw7SUSLZCNyiwhEMe6qQsxKBa6H40vGJeaf3ENn2ObFo06gAn53KwRzmR5MJnhA%2B2T%2BCdfrtDrIfC170eoNeCqmeWhm9MDTtwCjwXjKXJd4ayoVz30gPzZ7LQ9loeh%2FQzjb6B7P5u2p9YlesEeB3zutoihnuTFSwCZywPTZ5bNZWOZrQYA47XSHIsZSbuNdCGQ%2BtZKU5LHSenSQzazq1DE3Eldju31dAevAgM49TlNlcR1gk94mZdLQ%2BMjP%2FD0w6ejIaXMklLsk1PMKkIAwW%2FcFRlW61KKdvn5aBSRheGZg2v9kH%2FahS7iTSpZaq04jGqyZMc2yW0keWgWueKkR27%2F4JhV6l%2BoDxKuwD5t0gexl0xjp05%2BXdVLJ807Oa0MBDswsvbEyQY6mAGzUwRIn4Fh8Bvni73G4MuWyKkaPs4PhbKH2LDYKbNzti6drLC8ZvVlelfXFLCopJFw%2BTCxalrrfKv6UeBrL7JD0KWogi%2FdqB27VPdSTeJ7S8L1i7j4afnU5T6twDRobpDZS85SCYo9Ic%2B4xygN9wToJ%2BWMX%2FyvcbWqYHoVJ1Oc6U6UqmlEsbtXKwiS%2BLDmS1plcfBzwsF0FA%3D%3D&Expires=1764836812)
[4](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/3766213c-9fa9-40e7-b502-a4b1862afa83/CleanShot-2025-12-04-at-00.03.17-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYEV7NL7KLK&Signature=iADwvzBA7QFFN%2BuinmgjevOIFDE%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHgaCXVzLWVhc3QtMSJHMEUCIBXvl3t7ZNGZ%2B6NCD7EOdEWwEx7HfWwnRs6O5Sc%2FHg9MAiEAnkcu9F9vYD9%2BsprFjSGkJEuiTQt61lpkIki8tS3VyoMq8wQIQRABGgw2OTk3NTMzMDk3MDUiDJoiksW92arnfNqduirQBOhBLIY5WvalnptFONUl5Av9fhr9E4gwxqHNXfhOwhogPatgwELCA817EFO9Y9VmR6HMYSUZWCEpw%2FkFmjiPIgICPOt5sM8pzC5Q3bfSpG%2Fv7xxTCHbivkE%2Boxmx%2B13IXaRIYjPlFWKrSxO7Qvk79%2FY28XdV4d4ETvxynhcVjS62vqU7qg%2B2r1cTMXLmv6YIae%2B4mMKDGYVZkI9oBCeMsqQxl4LOiRx63nFxPE6IW8dD3VkrQen8MUTgHObJ0sbTSK%2F9Pq1FGs12q24MnxKcArCvTHhuR5ELLWbZPc%2BrW5ijVWGhGL41K2Jxh5UlyRVfut0BIYCmremYLoObaamisthVKNLDYQWca%2B9TiBwZko8NZFPdm9KsiT2miYzX6CGT%2F2BOyWmkjWYiojMEKhODRNYw7SUSLZCNyiwhEMe6qQsxKBa6H40vGJeaf3ENn2ObFo06gAn53KwRzmR5MJnhA%2B2T%2BCdfrtDrIfC170eoNeCqmeWhm9MDTtwCjwXjKXJd4ayoVz30gPzZ7LQ9loeh%2FQzjb6B7P5u2p9YlesEeB3zutoihnuTFSwCZywPTZ5bNZWOZrQYA47XSHIsZSbuNdCGQ%2BtZKU5LHSenSQzazq1DE3Eldju31dAevAgM49TlNlcR1gk94mZdLQ%2BMjP%2FD0w6ejIaXMklLsk1PMKkIAwW%2FcFRlW61KKdvn5aBSRheGZg2v9kH%2FahS7iTSpZaq04jGqyZMc2yW0keWgWueKkR27%2F4JhV6l%2BoDxKuwD5t0gexl0xjp05%2BXdVLJ807Oa0MBDswsvbEyQY6mAGzUwRIn4Fh8Bvni73G4MuWyKkaPs4PhbKH2LDYKbNzti6drLC8ZvVlelfXFLCopJFw%2BTCxalrrfKv6UeBrL7JD0KWogi%2FdqB27VPdSTeJ7S8L1i7j4afnU5T6twDRobpDZS85SCYo9Ic%2B4xygN9wToJ%2BWMX%2FyvcbWqYHoVJ1Oc6U6UqmlEsbtXKwiS%2BLDmS1plcfBzwsF0FA%3D%3D&Expires=1764836812)
[5](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/2bdd0e16-8725-4f16-a01d-d23199835573/CleanShot-2025-12-03-at-23.54.02-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYEV7NL7KLK&Signature=YgphMZd%2F%2F5XOzQo%2BkZjHOKzX1cw%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHgaCXVzLWVhc3QtMSJHMEUCIBXvl3t7ZNGZ%2B6NCD7EOdEWwEx7HfWwnRs6O5Sc%2FHg9MAiEAnkcu9F9vYD9%2BsprFjSGkJEuiTQt61lpkIki8tS3VyoMq8wQIQRABGgw2OTk3NTMzMDk3MDUiDJoiksW92arnfNqduirQBOhBLIY5WvalnptFONUl5Av9fhr9E4gwxqHNXfhOwhogPatgwELCA817EFO9Y9VmR6HMYSUZWCEpw%2FkFmjiPIgICPOt5sM8pzC5Q3bfSpG%2Fv7xxTCHbivkE%2Boxmx%2B13IXaRIYjPlFWKrSxO7Qvk79%2FY28XdV4d4ETvxynhcVjS62vqU7qg%2B2r1cTMXLmv6YIae%2B4mMKDGYVZkI9oBCeMsqQxl4LOiRx63nFxPE6IW8dD3VkrQen8MUTgHObJ0sbTSK%2F9Pq1FGs12q24MnxKcArCvTHhuR5ELLWbZPc%2BrW5ijVWGhGL41K2Jxh5UlyRVfut0BIYCmremYLoObaamisthVKNLDYQWca%2B9TiBwZko8NZFPdm9KsiT2miYzX6CGT%2F2BOyWmkjWYiojMEKhODRNYw7SUSLZCNyiwhEMe6qQsxKBa6H40vGJeaf3ENn2ObFo06gAn53KwRzmR5MJnhA%2B2T%2BCdfrtDrIfC170eoNeCqmeWhm9MDTtwCjwXjKXJd4ayoVz30gPzZ7LQ9loeh%2FQzjb6B7P5u2p9YlesEeB3zutoihnuTFSwCZywPTZ5bNZWOZrQYA47XSHIsZSbuNdCGQ%2BtZKU5LHSenSQzazq1DE3Eldju31dAevAgM49TlNlcR1gk94mZdLQ%2BMjP%2FD0w6ejIaXMklLsk1PMKkIAwW%2FcFRlW61KKdvn5aBSRheGZg2v9kH%2FahS7iTSpZaq04jGqyZMc2yW0keWgWueKkR27%2F4JhV6l%2BoDxKuwD5t0gexl0xjp05%2BXdVLJ807Oa0MBDswsvbEyQY6mAGzUwRIn4Fh8Bvni73G4MuWyKkaPs4PhbKH2LDYKbNzti6drLC8ZvVlelfXFLCopJFw%2BTCxalrrfKv6UeBrL7JD0KWogi%2FdqB27VPdSTeJ7S8L1i7j4afnU5T6twDRobpDZS85SCYo9Ic%2B4xygN9wToJ%2BWMX%2FyvcbWqYHoVJ1Oc6U6UqmlEsbtXKwiS%2BLDmS1plcfBzwsF0FA%3D%3D&Expires=1764836812)
[6](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/4f93a095-f083-42c0-a12b-923ee7d60a9b/CleanShot-2025-12-04-at-00.01.27-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYEV7NL7KLK&Signature=o%2FAFSRNTIuFXvSJkTyCZYha%2F5GE%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHgaCXVzLWVhc3QtMSJHMEUCIBXvl3t7ZNGZ%2B6NCD7EOdEWwEx7HfWwnRs6O5Sc%2FHg9MAiEAnkcu9F9vYD9%2BsprFjSGkJEuiTQt61lpkIki8tS3VyoMq8wQIQRABGgw2OTk3NTMzMDk3MDUiDJoiksW92arnfNqduirQBOhBLIY5WvalnptFONUl5Av9fhr9E4gwxqHNXfhOwhogPatgwELCA817EFO9Y9VmR6HMYSUZWCEpw%2FkFmjiPIgICPOt5sM8pzC5Q3bfSpG%2Fv7xxTCHbivkE%2Boxmx%2B13IXaRIYjPlFWKrSxO7Qvk79%2FY28XdV4d4ETvxynhcVjS62vqU7qg%2B2r1cTMXLmv6YIae%2B4mMKDGYVZkI9oBCeMsqQxl4LOiRx63nFxPE6IW8dD3VkrQen8MUTgHObJ0sbTSK%2F9Pq1FGs12q24MnxKcArCvTHhuR5ELLWbZPc%2BrW5ijVWGhGL41K2Jxh5UlyRVfut0BIYCmremYLoObaamisthVKNLDYQWca%2B9TiBwZko8NZFPdm9KsiT2miYzX6CGT%2F2BOyWmkjWYiojMEKhODRNYw7SUSLZCNyiwhEMe6qQsxKBa6H40vGJeaf3ENn2ObFo06gAn53KwRzmR5MJnhA%2B2T%2BCdfrtDrIfC170eoNeCqmeWhm9MDTtwCjwXjKXJd4ayoVz30gPzZ7LQ9loeh%2FQzjb6B7P5u2p9YlesEeB3zutoihnuTFSwCZywPTZ5bNZWOZrQYA47XSHIsZSbuNdCGQ%2BtZKU5LHSenSQzazq1DE3Eldju31dAevAgM49TlNlcR1gk94mZdLQ%2BMjP%2FD0w6ejIaXMklLsk1PMKkIAwW%2FcFRlW61KKdvn5aBSRheGZg2v9kH%2FahS7iTSpZaq04jGqyZMc2yW0keWgWueKkR27%2F4JhV6l%2BoDxKuwD5t0gexl0xjp05%2BXdVLJ807Oa0MBDswsvbEyQY6mAGzUwRIn4Fh8Bvni73G4MuWyKkaPs4PhbKH2LDYKbNzti6drLC8ZvVlelfXFLCopJFw%2BTCxalrrfKv6UeBrL7JD0KWogi%2FdqB27VPdSTeJ7S8L1i7j4afnU5T6twDRobpDZS85SCYo9Ic%2B4xygN9wToJ%2BWMX%2FyvcbWqYHoVJ1Oc6U6UqmlEsbtXKwiS%2BLDmS1plcfBzwsF0FA%3D%3D&Expires=1764836812)
[7](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/c0b95fd8-2a90-457d-befe-778844112b86/CleanShot-2025-12-04-at-00.03.07-2x.jpg?AWSAccessKeyId=ASIA2F3EMEYEV7NL7KLK&Signature=4E2joK%2BffE2%2Fci5E6zxmy8OSWi8%3D&x-amz-security-token=IQoJb3JpZ2luX2VjEHgaCXVzLWVhc3QtMSJHMEUCIBXvl3t7ZNGZ%2B6NCD7EOdEWwEx7HfWwnRs6O5Sc%2FHg9MAiEAnkcu9F9vYD9%2BsprFjSGkJEuiTQt61lpkIki8tS3VyoMq8wQIQRABGgw2OTk3NTMzMDk3MDUiDJoiksW92arnfNqduirQBOhBLIY5WvalnptFONUl5Av9fhr9E4gwxqHNXfhOwhogPatgwELCA817EFO9Y9VmR6HMYSUZWCEpw%2FkFmjiPIgICPOt5sM8pzC5Q3bfSpG%2Fv7xxTCHbivkE%2Boxmx%2B13IXaRIYjPlFWKrSxO7Qvk79%2FY28XdV4d4ETvxynhcVjS62vqU7qg%2B2r1cTMXLmv6YIae%2B4mMKDGYVZkI9oBCeMsqQxl4LOiRx63nFxPE6IW8dD3VkrQen8MUTgHObJ0sbTSK%2F9Pq1FGs12q24MnxKcArCvTHhuR5ELLWbZPc%2BrW5ijVWGhGL41K2Jxh5UlyRVfut0BIYCmremYLoObaamisthVKNLDYQWca%2B9TiBwZko8NZFPdm9KsiT2miYzX6CGT%2F2BOyWmkjWYiojMEKhODRNYw7SUSLZCNyiwhEMe6qQsxKBa6H40vGJeaf3ENn2ObFo06gAn53KwRzmR5MJnhA%2B2T%2BCdfrtDrIfC170eoNeCqmeWhm9MDTtwCjwXjKXJd4ayoVz30gPzZ7LQ9loeh%2FQzjb6B7P5u2p9YlesEeB3zutoihnuTFSwCZywPTZ5bNZWOZrQYA47XSHIsZSbuNdCGQ%2BtZKU5LHSenSQzazq1DE3Eldju31dAevAgM49TlNlcR1gk94mZdLQ%2BMjP%2FD0w6ejIaXMklLsk1PMKkIAwW%2FcFRlW61KKdvn5aBSRheGZg2v9kH%2FahS7iTSpZaq04jGqyZMc2yW0keWgWueKkR27%2F4JhV6l%2BoDxKuwD5t0gexl0xjp05%2BXdVLJ807Oa0MBDswsvbEyQY6mAGzUwRIn4Fh8Bvni73G4MuWyKkaPs4PhbKH2LDYKbNzti6drLC8ZvVlelfXFLCopJFw%2BTCxalrrfKv6UeBrL7JD0KWogi%2FdqB27VPdSTeJ7S8L1i7j4afnU5T6twDRobpDZS85SCYo9Ic%2B4xygN9wToJ%2BWMX%2FyvcbWqYHoVJ1Oc6U6UqmlEsbtXKwiS%2BLDmS1plcfBzwsF0FA%3D%3D&Expires=1764836812)
[8](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/dfc5e936-28fe-4fcd-856f-932221ee95ad/profile_4504_20251203_235132.txt)