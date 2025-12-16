# THREAD TRANSFER — Apex Enrichment Parsing + Wiring (DEC 16, 2025)

Owner: Apex Sales Intelligence (Apex backend + Dashboard_v1)  
Date: 2025-12-16  
Scope: Keep endpoints/calls stable; fix parsing so downstream steps (persona, icp-match, score, why-fit, rescore) operate on clean structured sections.

---

## Executive goal

Maintain the working pipeline:

Perplexity (open-ended, lots of data) → OpenAI (structured output) → Parse (normalize into JSON sections) → Persona/ICP/Score/Why-fit/Rescore → Dashboard_v1.

Do **not** change endpoint names or move calls; only fix post-OpenAI parsing + persistence so Dashboard_v1 and downstream logic receive structured sections.

---

## What is live / what is called

### Backend entrypoint + enrichment engine wiring (current)
- The backend has multiple entrypoints/structures in repo (e.g., top-level `api.py` and `apps/backend/main.py` are both present). [file:1]
- The enrichment endpoints in the v2 route set include `/api/contacts/{contact_id}/enrich` and `/api/contacts/{contact_id}/enrichment-status` under `/api/contacts`. [file:1]

### What actually runs for `/api/contacts/{id}/enrich` and `/api/batch/enrich`
- `apps/backend/main.py` imports and instantiates `EnhancedEnrichment` from `apps/backend/enrichment_engine.py` (confirmed by grep output during session).
- The call path for single enrich is:
  - main.py endpoint `/api/contacts/{contact_id}/enrich`
  - calls `enrichment_engine.enrich_contact(contact_dict)`
  - then persists to DB using `integrate_enrichment_result(raw_profile)` (from `apps/backend/services/enrichment_integration.py`)

### Secondary endpoint path (custom)
- There is also a route `apps/backend/api/routes/enrichment_apex_custom.py` exposing `/api/contacts/{contact_id}/apex-enrich` (used for testing a separate flow).
- A previous DB error occurred because that route attempted to update a non-existent `profile_context` column; the route UPDATE statement has been edited to remove `profile_context` to align with actual DB schema.

---

## Current failure mode (the real blocker)

### Symptom
- “Only raw data populated” in `enrichment_data`:
  - `sections` contains only `raw_text` (or content lands under `raw_profile` but not split into multiple section keys)
  - `metadata.format_detected` shows `"unknown"`
  - `metadata.total_sections` shows `1`

### Root cause
- **Parsing mismatch** between generator output and parser expectations.
- The currently active engine (`apps/backend/enrichment_engine.py`) produces markdown sections like:
  - `## overview`
  - `## background_and_experience`
  - `## company_overview`
  - etc.
- The current parser in `apps/backend/services/enrichment_parser.py` primarily looks for a different format:
  - `### PERSON PROFILE`, `### COMPANY PROFILE`, etc.
- As a result, parse auto-detection falls to `"unknown"` and returns `{"raw_text": raw_profile}` which makes the UI feel like “raw only”.

### Important: why engine-side parsing didn’t help
- Even though `EnhancedEnrichment.enrich_contact()` already calls `_extract_sections()` and returns `sections`,
  main.py **does not persist that dict**.
- main.py persists the output of `integrate_enrichment_result(raw_profile)`, which re-parses the markdown output via `services/enrichment_parser.py`.
- Therefore: the parser must support the engine’s `## section_key` format OR main.py must store the engine’s `sections` directly (we are choosing parser upgrade to avoid structural changes).

---

## Correct approach (minimal change, stable endpoints)

### Strategy
Keep everything structurally the same:
- Keep Perplexity → OpenAI inside the active engine (`EnhancedEnrichment`).
- Keep main.py endpoints and call sites unchanged.
- Keep `integrate_enrichment_result(raw_profile)` unchanged as the orchestration step.
- **Fix parsing** in `apps/backend/services/enrichment_parser.py` so it understands the engine’s `##` headers.

This aligns with the “after OpenAI returns, then parse” requirement.

---

## Implementation plan (recommended)

### Patch 1 — Update parser to support `##` headers
Edit:
- `apps/backend/services/enrichment_parser.py`

Add a new detection + parse path:
- Detect: `^## [a-z_]+$` (multiline)
- Parse: split on `## ` headers into `sections` dict
- Preserve backwards compatibility:
  - If old `###` format exists, still parse with existing logic
  - If legacy `===` exists, still parse with existing logic
  - Else fallback to `raw_text`

Expected result:
- `metadata.format_detected` becomes something like `"markdown_v3"` (or `"double_hash"`)
- `metadata.total_sections` becomes `>= 5`
- `sections` includes keys:
  - `overview`
  - `background_and_experience`
  - `company_overview`
  - `pain_points_and_challenges`
  - `budget_and_authority`
  - etc.

### Patch 2 — Re-enrich one contact to validate
- Call:
  - `POST /api/contacts/{id}/enrich` (single)
  - or `POST /api/batch/enrich` (batch)
- Verify in DB:
  - `contacts.enrichment_data` JSON now includes multiple keys under `sections`
- Verify in Dashboard_v1:
  - ContactDetail renders sections without dumping raw markdown.

---

## Operational validation checklist

### Backend logs
- On enrich call, confirm:
  - enrichment engine returns `profile_text` (structured markdown)
  - parser detects the correct format
  - saved JSON includes multi-section dict

### DB verification
- Inspect `contacts.enrichment_data` for a recently enriched contact:
  - Should contain:
    - `sections.overview` (string)
    - `sections.company_overview` (string)
    - `metadata.total_sections` > 1

### Frontend validation (Dashboard_v1)
- Contact detail page:
  - uses parsed sections where available
  - has fallback to raw markdown if missing (defensive UI)

---

## Files touched / key files to know

### Active enrichment path (do not break)
- `apps/backend/main.py`
  - `/api/contacts/{contact_id}/enrich`
  - `/api/batch/enrich`
  - persists via `integrate_enrichment_result(raw_profile)`
- `apps/backend/enrichment_engine.py`
  - class `EnhancedEnrichment`
  - method `enrich_contact()`

### Integration + parsing (the actual fix target)
- `apps/backend/services/enrichment_integration.py`
  - `integrate_enrichment_result(raw_enrichment_output: str) -> dict`
  - calls `services.enrichment_parser.parse_enrichment(raw_profile)`
- `apps/backend/services/enrichment_parser.py`
  - **must be updated** to parse the `##` header format

### Secondary path (custom endpoint; not the primary)
- `apps/backend/api/routes/enrichment_apex_custom.py`
  - `/api/contacts/{contact_id}/apex-enrich`
  - had DB write mismatch (`profile_context` column) and was adjusted

---

## Rollback plan (if parsing patch regresses)
- Revert only the parser file:
  - `apps/backend/services/enrichment_parser.py`
- This will revert format detection to previous behavior (raw_text-only fallback).
- Endpoints remain stable; no API changes required.

---

## Next actions (exact)
1) Patch parser (`apps/backend/services/enrichment_parser.py`) to support `## section_key` outputs.
2) Deploy.
3) Re-enrich 1 contact and verify `enrichment_data.sections` has multiple keys.
4) If Dashboard_v1 still shows raw only, check UI mapping for section keys vs UI expectations.

