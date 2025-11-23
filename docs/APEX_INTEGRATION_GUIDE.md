# APEX INTELLIGENCE INTEGRATION GUIDE
## Complete Setup for Scoring + Persona + HubSpot Sync

### 📁 Directory Structure

```
~/projects/apex/apps/backend/
├── intelligence/
│   ├── __init__.py
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── enrichment/
│   │   │   ├── __init__.py
│   │   │   ├── apex_intelligence_engine.py
│   │   │   └── persona_classifier_cre_sba.py
│   │   └── scoring/
│   │       └── __init__.py
│   └── sync/
│       ├── __init__.py
│       └── hubspot_sync.py
└── main.py (updated)
```

### 🎯 Integration Flow

```
IMPORT FLOW:
CSV/HubSpot Import → Score (Initial) → Classify Persona → Save

ENRICHMENT FLOW:  
Enrich Contact → Re-Score → Update Persona → Sync to HubSpot

SCRIPT GENERATION FLOW:
Get Contact → Use Persona + Scores → Generate Targeted Scripts
```

### 🔧 Setup Commands

```bash
# 1. Create directory structure
cd ~/projects/apex/apps/backend
mkdir -p intelligence/engines/enrichment intelligence/engines/scoring intelligence/sync

# 2. Create __init__.py files
touch intelligence/__init__.py
touch intelligence/engines/__init__.py
touch intelligence/engines/enrichment/__init__.py
touch intelligence/engines/scoring/__init__.py  
touch intelligence/sync/__init__.py

# 3. Copy intelligence files
cp apex_intelligence_engine.py intelligence/engines/enrichment/
cp persona_classifier_cre_sba.py intelligence/engines/enrichment/

# 4. Install dependencies
pip install hubspot-api-client requests

# 5. Setup HubSpot API key
export HUBSPOT_API_KEY="your-api-key-here"
# Or add to .env file
echo "HUBSPOT_API_KEY=your-api-key" >> .env
```

### 🆕 New API Endpoints

```python
# Import from HubSpot
POST /api/import/hubspot
Response: {imported_count, scored_count, classified_count}

# Bulk score contacts
POST /api/contacts/score-all
Response: {scored_count, average_mdcp, average_rss}

# Get persona distribution
GET /api/analytics/personas
Response: {tier1_count, tier2_count, breakdown_by_type}

# Sync contact to HubSpot
POST /api/contacts/{id}/sync-hubspot
Response: {success, synced_properties}

# Setup HubSpot custom properties (one-time)
POST /api/hubspot/setup-properties
Response: {created_count, property_names}
```

### 📊 Database Schema Updates

```sql
-- Add new columns to contacts table
ALTER TABLE contacts ADD COLUMN persona_tier TEXT;
ALTER TABLE contacts ADD COLUMN persona_type TEXT;
ALTER TABLE contacts ADD COLUMN persona_confidence REAL;
ALTER TABLE contacts ADD COLUMN mdcp_score REAL;
ALTER TABLE contacts ADD COLUMN mdcp_tier TEXT;
ALTER TABLE contacts ADD COLUMN rss_score REAL;
ALTER TABLE contacts ADD COLUMN rss_tier TEXT;
ALTER TABLE contacts ADD COLUMN priority_score REAL;
ALTER TABLE contacts ADD COLUMN urgency_level TEXT;
ALTER TABLE contacts ADD COLUMN last_scored_at TEXT;
ALTER TABLE contacts ADD COLUMN lifecycle_stage TEXT;
```

### 🔄 Updated Workflow

**1. Import Contact (CSV or HubSpot)**
```python
# Import → Score → Classify → Save
contact = import_contact(data)
scores = score_contact(contact.id)
persona = classify_persona(contact)
save_with_scores_and_persona(contact, scores, persona)
```

**2. Enrich Contact**
```python
# Enrich → Re-score → Update Persona → Sync
enrich_contact(contact.id)
new_scores = re_score_contact(contact.id)  # Scores may change!
new_persona = reclassify_persona(contact)  
sync_to_hubspot(contact.id, new_scores, new_persona)
```

**3. Generate Scripts**
```python
# Use persona for targeted messaging
contact = get_contact_with_persona(contact.id)
persona_type = contact.persona_type
tier = contact.persona_tier

if tier == "Tier 1":
    # Referral partner messaging
    scripts = generate_referral_scripts(contact, persona_type)
elif tier == "Tier 2":
    # Direct borrower messaging
    scripts = generate_borrower_scripts(contact, persona_type)
```

### 🎨 Frontend Updates Needed

**Add to Contact List Table:**
- Persona Tier badge (Tier 1/Tier 2)
- Persona Type (e.g., "Peer/Referral Partner")
- MDCP Score bar
- RSS Score bar
- Priority badge (IMMEDIATE/HIGH/MEDIUM/LOW)

**Add to Intelligence Report:**
- Persona section showing:
  - Tier (Tier 1 or Tier 2)
  - Type (specific persona)
  - Confidence score
  - Matched criteria
  - Priority multiplier

**Add new Persona Dashboard:**
- Pie chart: Tier 1 vs Tier 2 distribution
- Bar chart: Persona types breakdown
- Table: Top scoring contacts by persona
- Filter by persona type

### 🚀 Testing Checklist

- [ ] Import contacts from CSV → Auto-scored → Persona assigned
- [ ] Import from HubSpot → Contacts synced → Scored → Classified
- [ ] Enrich contact → Re-scored → Persona updated
- [ ] Generate scripts → Uses persona-specific messaging
- [ ] Sync to HubSpot → Custom properties populated
- [ ] View persona dashboard → Distribution shown
- [ ] Filter by persona tier → Works correctly
- [ ] Sort by priority score → Order correct

### 💡 Key Benefits

1. **Automatic Scoring on Import** - Every contact immediately scored
2. **Dynamic Re-scoring** - Scores update after enrichment
3. **Persona-Based Targeting** - Scripts tailored to persona type
4. **HubSpot Integration** - All data syncs back to HubSpot
5. **Priority Intelligence** - Know exactly who to contact first
6. **Tier-Based Strategy** - Different approach for referral vs borrower

### 📈 Expected Results

| Metric | Before | After |
|--------|--------|-------|
| Scoring Time | Manual | Automatic |
| Persona Classification | None | 8 detailed personas |
| HubSpot Integration | None | Bi-directional |
| Script Targeting | Generic | Persona-specific |
| Priority Clarity | Low | High (MDCP + RSS) |
| Re-engagement Strategy | None | Lifecycle-based |

### 🔑 Environment Variables

```bash
# Required
HUBSPOT_API_KEY=pat-na1-xxx...

# Optional
DATABASE_PATH=./apex.db
PERPLEXITY_API_KEY=pplx-xxx...
```

### 📝 Notes

- **Tier 1 contacts** get 1.25-1.35x priority multiplier (referral partners)
- **Tier 2 contacts** get 1.15-1.25x priority multiplier (direct borrowers)
- **Re-scoring after enrichment** catches changes in equity, deal status, etc.
- **Persona confidence** helps identify edge cases needing manual review
- **HubSpot custom properties** allow native HubSpot workflows based on APEX data

