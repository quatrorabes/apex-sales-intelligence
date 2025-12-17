# FIX: Make /api/batch/enrich accept contact_ids from Dashboard

## THE PROBLEM

Dashboard sends:
```json
{ "contact_ids": ["f37621eb-d4fe-445e-98ad-e8dbafa41969"] }
```

But backend ignores it and enriches the next unenriched contact instead.

## THE FIX

Edit `apps/backend/api/routes/enrichment.py`:

### Step 1: Add Pydantic model (after imports, around line 20)

```python
from pydantic import BaseModel
from typing import List, Optional

class BatchEnrichRequest(BaseModel):
    contact_ids: Optional[List[str]] = None
```

### Step 2: Modify batch_enrich function (around line 230)

FIND:
```python
@router.post("/api/batch/enrich")
async def batch_enrich(limit: int = Query(1, ge=1, le=1)):
    """Batch enrichment (1 at a time)"""
    if not ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Engine unavailable")

    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM contacts WHERE enrichment_status IS NULL OR enrichment_status != 'completed' ORDER BY created_at DESC LIMIT %s",
                (limit,)
            )
            targets = [row["id"] for row in cursor.fetchall()]
            cursor.close()
```

REPLACE WITH:
```python
@router.post("/api/batch/enrich")
async def batch_enrich(
    request: BatchEnrichRequest = None,
    limit: int = Query(1, ge=1, le=1)
):
    """Batch enrichment - accepts contact_ids from Dashboard"""
    if not ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Engine unavailable")

    try:
        # NEW: If Dashboard sends specific contact_ids, use those
        if request and request.contact_ids:
            targets = request.contact_ids[:5]  # Max 5 at once
            logger.info(f"🔄 Enriching {len(targets)} specific contacts from Dashboard")
        else:
            # Original: Get next unenriched contact
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM contacts WHERE enrichment_status IS NULL OR enrichment_status != 'completed' ORDER BY created_at DESC LIMIT %s",
                    (limit,)
                )
                targets = [row["id"] for row in cursor.fetchall()]
                cursor.close()
            logger.info(f"🔄 Auto-selecting {len(targets)} unenriched contacts")
```

## DEPLOY

```bash
git add apps/backend/api/routes/enrichment.py
git commit -m "fix: batch enrich now accepts contact_ids from Dashboard"
git push origin main
```

Wait 2 minutes for Render to restart.

## TEST

1. Select Shilo Hall checkbox in Dashboard
2. Click bulk enrich button
3. Should now enrich Shilo Hall, not Douglas Hansford!
