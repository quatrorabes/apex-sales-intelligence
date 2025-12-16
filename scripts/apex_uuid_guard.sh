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
