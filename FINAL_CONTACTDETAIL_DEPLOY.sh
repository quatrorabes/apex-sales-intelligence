#!/bin/bash
# FINAL DEPLOY: ContactDetail.tsx - Matches ContactsView color scheme exactly
# Date: Dec 15, 2025 4:02 PM PST | Target: dashboard_v1/src/pages/ContactDetail.tsx

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
TS=$(date +%Y%m%d_%H%M%S)
FILE="dashboard_v1/src/pages/ContactDetail.tsx"

cp "$FILE" "${FILE}.backup-${TS}"
echo "✅ Backup: ${FILE}.backup-${TS}"

cat > "$FILE" << 'EOF'
// dashboard_v1/src/pages/ContactDetail.tsx
// FINAL: Matches ContactsView styling (navy headers + subtle gradient bg)

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

const API_BASE = import.meta.env.VITE_API_URL || "https://apex-backend-i7b0.onrender.com";

interface Contact {
  id:
