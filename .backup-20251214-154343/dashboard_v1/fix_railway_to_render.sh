#!/bin/bash
cd ~/projects/apex/apex-sales-intelligence

echo "Finding Railway references..."
grep -r "railway" dashboard_v1/src/ --include="*.ts" --include="*.tsx"

echo ""
echo "Replacing with Render URL..."
find dashboard_v1/src -type f \( -name "*.ts" -o -name "*.tsx" \) \
  -exec sed -i '' 's|apex-backend-production-production.up.railway.app|apex-backend-i7b0.onrender.com|g' {} +

echo ""
echo "✓ Done! Verifying..."
grep -r "apex-backend-i7b0.onrender.com" dashboard_v1/src/ --include="*.ts" --include="*.tsx" | head -5

echo ""
echo "Now run:"
echo "  cd dashboard_v1 && npm run build && git add -A && git commit -m 'fix: Railway→Render' && git push"
