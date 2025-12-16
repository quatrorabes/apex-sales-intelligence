UUID handling was the *root cause* of “Contact not found” and it can easily regress unless you lock a few rules in place across Dashboard_v1 + Apex API calls. Here’s exactly what we did and the guardrails so you never redo it for enrichment/persona/etc.[1][2]

## What broke (the UUID mismatch)
Your production contacts use UUID strings like `fdfb18f1-45b0-4273-99e2-a02e0f9f0fbe`.[2]
In the older Dashboard code path, the router param was treated like a numeric ID and ran through `parseInt(contactId)`, which turns a UUID into `NaN` (or truncates at the first non-digit), causing calls like `/api/contacts/NaN` or the wrong numeric id.[3][1]
That cascaded: contact fetch failed, and then enrichment UI also failed because enrichment/persona actions were built on the same `contactId` value.[3][2]

## The rule we enforced (single source of truth)
**Rule:** *Contact IDs are opaque strings in Dashboard_v1. Never parse them. Never assume integer semantics.*[1][2]
This applies to **every** endpoint that uses a contact identifier: fetch contact, enrich, enrichment-status polling, generate-persona, download persona PDFs, etc.[2][3]

## The concrete fixes we applied
### 1) Router param kept as string
Your route is already string-safe: `path="/contacts/:id"` (or `/contacts/:contactId` in other app variants).[1]
We treat `id` from `useParams()` as a string and pass it through untouched. (No `parseInt` anywhere.)[1]

### 2) Frontend types updated: `id: string`
We updated the `Contact` TypeScript interface to `id: string` so TS stops encouraging numeric conversions and so the UI matches the API reality.[2]
This is key because if `id` is typed as `number`, someone will “fix” a TS error by reintroducing `parseInt()`.[3]

### 3) Normalize API payload, don’t reinterpret ID
The API returns wrappers like `{ success: true, contact: {...} }` and uses snake_case fields (`first_name`, `enrichment_status`).[2]
We added a `normalizeContact(api)` helper that:
- Keeps `id` as `String(api.id)` (no numeric casts)
- Maps snake_case -> the UI model (`firstname`, `lastname`, `enrichment_status`, etc.)[2]

This prevents “UUID handling” and “payload shape handling” from being mixed into enrichment logic.[2]

### 4) Endpoint calls now use the UUID string
Every fetch now interpolates the UUID directly, e.g.:
- `GET ${API_BASE}/api/contacts/${id}`
- `POST ${API_BASE}/api/contacts/${id}/enrich`
- `GET ${API_BASE}/api/contacts/${id}/enrichment-status`
- `POST ${API_BASE}/api/contacts/${id}/generate-persona`[2]

Once the ID is treated as a string, enrichment never needs special handling for UUID vs int—it just works because it’s the same identifier all the way through.[2]

## Guardrails (so we never redo this)
### Hard rule: no parseInt on contact identifiers
Add a repo-wide check and fail builds if it appears in Dashboard_v1 contact code paths:

```bash
cat > scripts/apex_uuid_guard.sh <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

echo "Checking for UUID-breaking patterns..."
if rg -n "parseInt\\((contactId|id)\\)" dashboard_v1/src 2>/dev/null; then
  echo "FAIL: parseInt(contactId|id) found. UUIDs must remain strings."
  exit 1
fi

if rg -n "contactId:\\s*number|id:\\s*number" dashboard_v1/src/pages/ContactDetail.tsx dashboard_v1/src/api.ts 2>/dev/null; then
  echo "WARN: numeric contactId/id types found; verify UUID string typing."
fi

echo "OK: UUID guard passed."
BASH

chmod +x scripts/apex_uuid_guard.sh
```

### API contract rule: ID is opaque
Document it in your internal Apex contract: “`contact.id` is a UUID string; endpoints accept string path params.” This ensures enrichment/persona/polling endpoints stay consistent.[2]

## Why this prevents rework on enrichment
Enrichment isn’t “special”—it’s just additional data hanging off the same contact record, keyed by the same UUID.[2]
Once the UI always uses the UUID string, the only remaining enrichment work is **schema mapping** (e.g., reading `enrichment.sections`)—not identifier plumbing.[2]

Plain question: do you want the guard script wired into GitHub Actions (fail PRs) or just kept as a local `make verify` step?

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/711e7ab2-84bc-42e9-90bb-fa4f04a6c2cb/App.tsx)
[2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/images/46916355/a3f1cd65-8efd-4e15-88cc-ce4e93529355/CleanShot-2025-12-15-at-14.37.11-2x.jpg)
[3](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/4b890b95-08a3-40d7-a3bd-d85ef030cb05/ContactDetail.tsx)
[4](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_747aeb83-8e6a-4566-b2b1-733b8db8bda4/9c031784-5364-447d-8305-ec160d110728/paste.txt)