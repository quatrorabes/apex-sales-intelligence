#!/bin/bash

# 1. Local smoke test
cd ~/projects/apex/apex-sales-intelligence/dashboard_v1
npm run dev
# Visit http://localhost:5173/contacts/1
# Click "Enrich" → should POST to backend → reload contact

# 2. Verify backend responds
curl -X POST https://apex-backend-i7b0.onrender.com/api/contacts/1/enrich

# 3. Deploy to Vercel
vercel --prod

# 4. Production test
# Visit https://your-dashboard.vercel.app/contacts/1
# Click "Enrich" → verify sections populate
