# APEX INTELLIGENCE - INSTALLATION & INTEGRATION GUIDE

## 📦 Quick Start

### Step 1: Copy Files to Your Project

```bash
# Copy the main scoring engine
cp apex_intelligence_engine.py apps/backend/intelligence/apex_scoring_engine.py
cp lead_types.py apps/backend/intelligence/lead_types.py
cp utils.py apps/backend/intelligence/utils.py
cp __init__.py apps/backend/intelligence/__init__.py

# Copy the migration script
cp add_apex_intelligence_migration.py migrations/add_apex_intelligence.py
```

### Step 2: Run Database Migration

```bash
# Activate your venv
source venv/bin/activate

# Run the migration
python migrations/add_apex_intelligence.py

# Output should show:
# ✅ [APEX INTELLIGENCE] Migration completed successfully!
#    • Tables created: 6
#    • Columns added: 24
```

### Step 3: Set Up Lead Types

Update your contacts with lead types:

```sql
-- UPDATE contacts by lead type
UPDATE contacts SET lead_type = 'BROKER' WHERE company LIKE '%Broker%';
UPDATE contacts SET lead_type = 'BANKER' WHERE company LIKE '%Bank%';
UPDATE contacts SET lead_type = 'CDC' WHERE title LIKE '%SBA%';
UPDATE contacts SET lead_type = 'BORROWER' WHERE lead_type IS NULL;
```

### Step 4: Run Your First Scoring

```bash
python -m apps.backend.intelligence.apex_scoring_engine
```

Expected output:
```
[APEX INTELLIGENCE] Starting scoring engine...
  → Database: apex.db
  → Scoring 23 contacts...
  → Scored 10/23 contacts
  → Scored 20/23 contacts

[APEX INTELLIGENCE] Scoring complete!
  → Total contacts scored: 23

[TOP 10 PRIORITY CONTACTS]
========================================
1. John Smith (Goldman Commercial)
   Lead Type: BROKER | Lifecycle: ESTABLISHED
   MDCP: 82/100 (HOT) | RSS: 87
   Priority: 84.8/100 (IMMEDIATE)
   Action: ⭐ STRATEGIC BROKER PARTNER - VIP treatment...
```

---

## 🔌 Integration with Apex Backend

### Option A: Direct Import (Recommended)

In your `apps/backend/main.py`:

```python
from apps.backend.intelligence import ApexScoringEngine, score_contact, score_all_contacts

# Score a single contact
result = score_contact(contact_id=123, db_path='apex.db')
print(f"Contact: {result['contact_name']}")
print(f"Priority: {result['priority_score']}/100 ({result['urgency_level']})")
print(f"Action: {result['recommended_action']}")

# Score all contacts
results = score_all_contacts(lead_type='BROKER', db_path='apex.db')
for contact in results[:10]:
    print(f"{contact['contact_name']}: {contact['priority_score']}/100")
```

### Option B: Add API Endpoints

Create `apps/backend/api/routes/scoring.py`:

```python
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from apps.backend.intelligence import ApexScoringEngine

router = APIRouter(prefix="/api/scoring", tags=["scoring"])

@router.get("/score/{contact_id}")
async def get_contact_score(contact_id: int):
    """Get MDCP/RSS/Priority scores for a contact"""
    try:
        engine = ApexScoringEngine('apex.db')
        result = engine.score_contact(contact_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/score/all")
async def score_all_contacts(lead_type: Optional[str] = None):
    """Score all contacts (optionally filtered by type)"""
    try:
        engine = ApexScoringEngine('apex.db')
        results = engine.score_all_contacts(lead_type)
        return {
            'total': len(results),
            'contacts': results[:50],  # Return top 50
            'lead_type_filter': lead_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/priority/immediate")
async def get_immediate_priority_contacts():
    """Get contacts requiring immediate action"""
    try:
        engine = ApexScoringEngine('apex.db')
        results = engine.score_all_contacts()
        immediate = [c for c in results if c['urgency_level'] == 'IMMEDIATE']
        return {
            'count': len(immediate),
            'contacts': immediate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lifecycle/{stage}")
async def get_contacts_by_lifecycle(stage: str):
    """Get contacts by lifecycle stage"""
    try:
        engine = ApexScoringEngine('apex.db')
        engine.cursor.execute("""
            SELECT * FROM v_latest_contact_scores
            WHERE lifecycle_stage = ?
            ORDER BY priority_score DESC
        """, (stage.upper(),))
        
        rows = engine.cursor.fetchall()
        return {
            'stage': stage,
            'count': len(rows),
            'contacts': [dict(row) for row in rows]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add to main.py:
# from apps.backend.api.routes import scoring
# app.include_router(scoring.router)
```

---

## 📊 Database Queries

### Get Top Priority Contacts

```sql
SELECT 
    c.firstname, c.lastname, c.company,
    p.priority_score, p.urgency_level,
    m.mdcp_total, m.mdcp_tier,
    r.rss_total, r.rss_tier
FROM v_latest_contact_scores
WHERE priority_score >= 70
ORDER BY priority_score DESC;
```

### Lifecycle Analytics

```sql
SELECT 
    lead_type,
    lifecycle_stage,
    COUNT(*) as count,
    AVG(mdcp_total) as avg_mdcp,
    AVG(rss_total) as avg_rss,
    AVG(priority_score) as avg_priority
FROM v_latest_contact_scores
GROUP BY lead_type, lifecycle_stage
ORDER BY lead_type, lifecycle_stage;
```

### Get Specific Lead Type Rankings

```sql
-- Top BROKER prospects
SELECT * FROM v_latest_contact_scores
WHERE lead_type = 'BROKER'
ORDER BY priority_score DESC
LIMIT 20;

-- BANKER relationships to nurture
SELECT * FROM v_latest_contact_scores
WHERE lead_type = 'BANKER' AND lifecycle_stage IN ('WARMING', 'ACTIVE')
ORDER BY days_since_last_contact DESC;
```

---

## 🎯 Configuration

### Lead Type Customization

Edit `apps/backend/intelligence/lead_types.py` to adjust weights:

```python
TYPES = {
    'CUSTOM_TYPE': {
        'description': 'Your custom lead type',
        'mdcp_weights': {
            'Money': 0.25,
            'Decision': 0.25,
            'Credibility': 0.25,
            'Pain': 0.25
        }
    }
}
```

### Lifecycle Stage Triggers

Modify `apex_scoring_engine.py` `_determine_lifecycle_stage()` method:

```python
def _determine_lifecycle_stage(self, contact: Dict) -> str:
    """Custom lifecycle logic"""
    # Your custom rules here
    if contact.get('custom_metric') > threshold:
        return 'CUSTOM_STAGE'
```

---

## 📈 Monitoring & Logging

### Enable Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

logger = logging.getLogger('apex_intelligence')

# In scoring engine:
logger.info(f"Scoring contact {contact_id}: {result['lead_type']}")
```

### Health Check

```python
def health_check():
    """Verify Apex Intelligence system health"""
    engine = ApexScoringEngine('apex.db')
    
    # Check database
    engine.cursor.execute("SELECT COUNT(*) FROM contacts")
    contacts = engine.cursor.fetchone()[0]
    
    # Check scores
    engine.cursor.execute("SELECT COUNT(*) FROM mdcp_scores")
    mdcp_scores = engine.cursor.fetchone()[0]
    
    engine.cursor.execute("SELECT COUNT(*) FROM rss_scores")
    rss_scores = engine.cursor.fetchone()[0]
    
    return {
        'status': 'healthy',
        'total_contacts': contacts,
        'mdcp_scores_calculated': mdcp_scores,
        'rss_scores_calculated': rss_scores
    }
```

---

## 🚀 Performance Tips

1. **Batch Scoring**: Score all contacts at once instead of individually
   ```python
   results = score_all_contacts()  # Much faster than looping
   ```

2. **Index Important Queries**: Use database indexes
   ```sql
   CREATE INDEX idx_priority_urgency ON priority_scores(urgency_level);
   ```

3. **Cache Results**: Store results for repeat queries
   ```python
   @cache(ttl=300)  # Cache for 5 minutes
   def get_immediate_priority():
       return score_all_contacts()
   ```

4. **Limit Recalculation**: Don't rescore constantly
   ```python
   # Only rescore if >1 day since last calculation
   if days_since_last_calculation > 1:
       results = score_all_contacts()
   ```

---

## 🔧 Troubleshooting

### Issue: "Column already exists"
**Solution**: Normal during first migration. Columns already exist from previous version.

### Issue: No scores appearing
**Solution**: Make sure `lead_type` is set for contacts:
```sql
UPDATE contacts SET lead_type = 'BORROWER' WHERE lead_type IS NULL;
```

### Issue: Low RSS scores
**Solution**: RSS requires touchpoint data. Log touchpoints:
```python
from apps.backend.intelligence import ApexScoringEngine
engine = ApexScoringEngine()
engine.cursor.execute("""
    INSERT INTO touchpoints (contact_id, touchpoint_type, touchpoint_date)
    VALUES (?, ?, CURRENT_TIMESTAMP)
""", (contact_id, 'phone_call'))
```

### Issue: Scores not updating
**Solution**: Database may need commit:
```python
engine.db.commit()
```

---

## 📞 Support

For issues or customization:
1. Check database schema: `SELECT * FROM sqlite_master WHERE type='table';`
2. Review migration log: `SELECT * FROM apex_metadata;`
3. Check calculation version: `SELECT DISTINCT calculation_version FROM mdcp_scores;`

---

## Version History

- **1.0.0** (Nov 18, 2025): Initial release
  - MDCP scoring with 5 lead types
  - RSS relationship scoring
  - Lifecycle stage tracking
  - Priority scoring & action recommendations

---

**Ready to launch Apex Intelligence! 🚀**
