# APEX Railway Deployment Debug Session
**Date:** December 6, 2025, 3:00-9:30 PM PST
**Status:** Backend deploys but routes not registering

## ISSUES FIXED SO FAR

✅ **Issue 1:** Duplicate `if __name__ == '__main__'` blocks (lines 1873 & 2594)
- **Fix:** Removed first block, kept routes before single main block
- **Verified:** Only 1 main block at line 2593, `/api/analytics` at line 1966

✅ **Issue 2:** SQLite syntax `AUTOINCREMENT` in PostgreSQL
- **Fix:** Changed to `SERIAL PRIMARY KEY`
- **Verified:** 0 AUTOINCREMENT instances

✅ **Issue 3:** Dockerfile using `python api.py` instead of Gunicorn
- **Fix:** Changed CMD to `gunicorn api:app`
- **Verified:** Dockerfile correct

✅ **Issue 4:** Missing `gunicorn` in requirements.txt
- **Fix:** Added to requirements.txt
- **Verified:** Present in requirements.txt

## CURRENT STATE

### What Works
- ✅ `/api/health` - Returns 200, shows 1338 contacts
- ✅ `/api/contacts` - Returns paginated contacts
- ✅ Railway healthcheck passes
- ✅ Database connection (PostgreSQL)

### What Doesn't Work
- ❌ `/api/analytics` - Returns 404 "Not found"
- ❌ `/api/todays-board` - Returns 404 "Not found"  
- ❌ `/api/debug/routes` - Returns 404 (even debug route not registered!)

### Code Verification (Local)
Current commit
git log --oneline | head -1

e4efa41 debug: add route listing endpoint
Route position
grep -n "@app.route('/api/analytics'" api.py

1984:@app.route('/api/analytics', methods=['GET'])
Main block position
grep -n "if name == 'main':" api.py

2611:if name == 'main':
Route count
grep -c "@app.route" api.py

45 (including debug route)
text

## HYPOTHESIS

**Routes aren't being registered because Flask module isn't loading properly.**

Evidence:
1. Even `/api/debug/routes` (added at line 372) returns 404
2. Only routes that work are the very early ones (health, contacts)
3. Local import fails with `ModuleNotFoundError: psycopg2` (expected)
4. Railway import status unknown - NEED LOGS

## NEXT STEPS

1. **Check Railway deployment logs** for Python import errors
2. **Look for Gunicorn worker boot failures**
3. **Check if all dependencies installed** during build

## FILES TO CHECK

- `api.py` - Main Flask app (2,614 lines)
- `Dockerfile` - Uses Gunicorn correctly
- `requirements.txt` - Has all deps including psycopg2-binary, gunicorn
- `railway.json` - Forces Dockerfile builder

## COMMANDS FOR NEXT SESSION

Test endpoint
curl https://apex-backend-production-production.up.railway.app/api/analytics

Check what routes work
for route in health contacts analytics todays-board smart-lists; do
echo "Testing /api/$route:"
curl -s https://apex-backend-production-production.up.railway.app/api/$route | head -20
echo ""
done

text

