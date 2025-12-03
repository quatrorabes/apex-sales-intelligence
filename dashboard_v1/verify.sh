#!/bin/bash

echo "🔍 Apex Dashboard Health Check"
echo "=============================="

# Check API connectivity (local)
echo "Testing local API..."
if curl -s http://localhost:8000/api/health > /dev/null; then
  echo "✅ Local API responding"
else
  echo "⚠️  Local API not responding (may not be running)"
fi

# Check API connectivity (Railway)
echo "Testing production API..."
if curl -s https://apex-intelligence-production.up.railway.app/api/health > /dev/null; then
  echo "✅ Production API responding"
else
  echo "❌ Production API not responding"
fi

# Check if dev server is running
echo "Checking dev server..."
if curl -s http://localhost:5173 > /dev/null; then
  echo "✅ Dev server running at http://localhost:5173"
else
  echo "ℹ️  Dev server not running. Start with 'npm run dev'"
fi

echo ""
echo "File Structure:"
ls -lh src/{config,api,types}.ts 2>/dev/null || echo "⚠️  Core files missing"
ls -lh src/components/*.tsx 2>/dev/null | wc -l | xargs echo "Component files:"

echo ""
echo "✅ Health check complete"
