#!/bin/bash
set -e

cd ~/projects/apex/apex-sales-intelligence

echo "=========================================="
echo "🔍 APEX FINAL DEBUG & VERIFY"
echo "=========================================="
echo ""

# 1) LOCAL CODE INTEGRITY CHECKS
# --------------------------------

echo "1) Verifying psycopg2 / PostgreSQL syntax..."
echo "---------------------------------------------"

# Check for leftover SQLite-style placeholders
SQLITE_Q=$(grep -n "LIMIT \?" api.py || true)
if [ -n "$SQLITE_Q" ]; then
  echo "❌ Found SQLite-style LIMIT ? placeholders:"
  echo "$SQLITE_Q"
else
  echo "✅ No SQLite-style LIMIT ? placeholders found (using %s as psycopg2 requires).[web:3][web:4]"
fi

Q_MARKS=$(grep -n " \?" api.py || true)
if [ -n "$Q_MARKS" ]; then
  echo ""
  echo "⚠️ Found other '?' usages in SQL; review these:"
  echo "$Q_MARKS"
else
  echo "✅ No raw '?' SQL placeholders remain."
fi

echo ""
echo "Checking ALTER TABLE statements for IF NOT EXISTS..."
ALTER_NO_IF=$(grep -n "ALTER TABLE contacts ADD COLUMN " api.py | grep -v "IF NOT EXISTS" || true)
if [ -n "$ALTER_NO_IF" ]; then
  echo "❌ Found ALTER TABLE ADD COLUMN without IF NOT EXISTS (can abort Postgres transaction):[web:16]"
  echo "$ALTER_NO_IF"
else
  echo "✅ All ALTER TABLE contacts ADD COLUMN use IF NOT EXISTS (idempotent migration).[web:16]"
fi

echo ""
echo "Python syntax check..."
python3 -m py_compile api.py && echo "✅ api.py compiles cleanly" || echo "❌ Syntax error in api.py"

echo ""
echo "Route definitions overview..."
grep -n "@app.route" api.py | sed 's/^/  /'

echo ""
echo "Main block position..."
grep -n "if __name__ == '__main__':" api.py || echo "❌ No main block found (expected for python api.py mode)"

echo ""
echo "Git HEAD and recent commits..."
git log --oneline | head -5
echo ""

# 2) GIT PUSH CONFIRMATION (OPTIONAL)
# --------------------------------
read -p "Push current api.py to main and trigger Railway deploy? [y/N] " PUSH
if [[ "$PUSH" =~ ^[Yy]$ ]]; then
  git add api.py railway.json Dockerfile || true
  git commit -m "chore: finalize Apex backend SQL & route fixes

- Ensure all psycopg2 placeholders use %s (PostgreSQL, not SQLite).[web:3][web:4]
- Ensure ALTER TABLE ADD COLUMN uses IF NOT EXISTS to avoid aborted transactions.[web:16]
- Keep single Flask app instance and single main block.
" || echo "No changes to commit."
  git push origin main
  echo ""
  echo "✅ Pushed to GitHub; Railway will rebuild."
  echo "⏳ Waiting 120 seconds for deployment..."
  for i in {120..1}; do printf "\r   ⏱️  %3d seconds..." "$i"; sleep 1; done
  echo ""
else
  echo "Skipping push; assuming Railway already built latest commit."
fi

# 3) LIVE RUNTIME VERIFICATION
# --------------------------------
BASE_URL="https://apex-backend-production-production.up.railway.app"

echo ""
echo "=========================================="
echo "🧪 LIVE ENDPOINT VERIFICATION"
echo "=========================================="
echo ""

echo "Health:"
echo "-------"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/api/health" | sed 's/^/  /'
echo ""

echo "Contacts collection:"
echo "--------------------"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/api/contacts?limit=5" | sed 's/^/  /'
echo ""

echo "Single contact (id=1):"
echo "----------------------"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/api/contacts/1" | sed 's/^/  /'
echo ""

echo "Today's board:"
echo "--------------"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/api/todays-board" | sed 's/^/  /'
echo ""

echo "Analytics:"
echo "----------"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/api/analytics" | sed 's/^/  /'
echo ""

echo "Smart lists:"
echo "------------"
curl -s -w "\nHTTP %{http_code}\n" "$BASE_URL/api/smart-lists" | sed 's/^/  /'
echo ""

echo "=========================================="
echo "📊 INTERPRETATION"
echo "=========================================="
echo "If /api/health is 200 but others are 404 with body {\"error\":\"Not found\"}:"
echo "  - Routes are still not registered in the running app instance."
echo "  - Next suspect: multiple Flask('...') app instances, or wrong app object served."
echo ""
echo "Check for multiple Flask app instances:"
echo "  grep -n \"Flask(\" api.py"
echo "There should be exactly one app = Flask(__name__). Extra ones will cause"
echo "routes to attach to the wrong app instance."
echo ""
echo "If any of the critical SQL checks above showed ❌, fix those first and rerun."
echo "=========================================="
