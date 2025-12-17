# ENRICHMENT BUTTON BUG FIX

## THE PROBLEM

When you click "Enrich" on Shilo Hall, the Dashboard calls:
```
POST /api/batch/enrich
```

This enriches Douglas Hansford (the next unenriched contact), not Shilo Hall.

It SHOULD call:
```
POST /api/v2/contacts/f37621eb-d4fe-445e-98ad-e8dbafa41969/enrich
```

## THE FIX

Find which Dashboard file calls "batch/enrich" and change it to use the contact-specific endpoint.

Run this:
```bash
cd dashboard_v1
grep -rn "batch.*enrich" src/
grep -rn "batchEnrich" src/
```

Then paste the output here and I'll create the exact fix!
