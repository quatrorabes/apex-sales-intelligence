# 🔧 TROUBLESHOOTING & DIAGNOSTICS

**Last Updated:** November 13, 2025

---

## PROBLEM: Dashboard Won't Start

### Symptom
```
ModuleNotFoundError: No module named 'streamlit'
```

### Fix
```bash
pip install streamlit openai python-dotenv pandas
streamlit run dashboard.py
```

---

## PROBLEM: "OPENAI_API_KEY not set"

### Symptom
During generation:
```
❌ ERROR: OPENAI_API_KEY not found in .env
```

### Fix

**Option 1: Create .env file**
```bash
cat > .env << EOF
OPENAI_API_KEY=sk-your-actual-key-here
EOF
```

**Option 2: Export as environment variable**
```bash
export OPENAI_API_KEY=sk-your-actual-key-here
streamlit run dashboard.py
```

**Verify it's set:**
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

---

## PROBLEM: Email Generator Fails with Banned Terms

### Symptom
```
⚠️ WARNING: Generated content mentioned off-topic terms (fintech/software/etc)
```

### Why
The generator is detecting off-topic content like "platform", "software", "AI", etc.

### Fix
The code auto-regenerates. If it still fails:

1. Check prompt in `loan_email_generator.py` - it has guards
2. Review contact data - maybe wrong industry?
3. Try with different contact

---

## PROBLEM: Database Locked Error

### Symptom
```
sqlite3.OperationalError: database is locked
```

### Why
Two processes accessing database simultaneously

### Fix
```bash
# Stop Streamlit (Ctrl+C)
# Delete database (will auto-recreate)
rm sales_angel.db

# Restart
streamlit run dashboard.py
```

---

## PROBLEM: Generation Hangs

### Symptom
Dashboard stuck on "Generating content..." for >30 seconds

### Why
1. OpenAI API slow or down
2. Network timeout
3. Invalid API key

### Fix
```bash
# Check OpenAI API status
curl https://status.openai.com

# Check if key is valid
python -c "
import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
try:
    client = OpenAI()
    response = client.chat.completions.create(
        model='gpt-4',
        messages=[{'role': 'user', 'content': 'test'}],
        max_tokens=10
    )
    print('✅ API key works!')
except Exception as e:
    print(f'❌ API error: {e}')
"
```

---

## PROBLEM: "Contact not found" on Generate

### Symptom
Dropdown is empty or contact disappears

### Why
Database connection issue or no contacts exist

### Fix
```bash
# Verify database has contacts
sqlite3 sales_angel.db "SELECT COUNT(*) FROM contacts;"

# Should return: 1 (or higher)

# If 0, add a contact via dashboard first
```

---

## PROBLEM: Generated Content Is Generic

### Symptom
Emails don't reference specific details about company/person

### Why
1. Contact data incomplete (missing MBTI, company, etc)
2. Prompt not specific enough
3. OpenAI model hallucinating

### Fix
1. **Fill in all contact fields** (company, title, MBTI, DISC)
2. **Use different contact** to test
3. **Check email_generator prompt** - it has guardrails

---

## PROBLEM: "ModuleNotFoundError" for loan_email_generator

### Symptom
```
ModuleNotFoundError: No module named 'loan_email_generator'
```

### Why
Files not in same directory or wrong path

### Fix
```bash
# Check files are in same directory
ls -la *.py | grep -E "(dashboard|loan_email|loan_call|sales_angel)"

# Output should show all files in current directory

# If not, copy them to same folder
cp /path/to/loan_email_generator.py .
cp /path/to/loan_call_generator.py .
```

---

## PROBLEM: Streamlit Session State Issues

### Symptom
Buttons not responding or page reloads unexpectedly

### Why
Streamlit caching/session state conflict

### Fix
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart dashboard
streamlit run dashboard.py
```

---

## PROBLEM: Generation Produces Invalid JSON for Calls

### Symptom
Call script generation fails with "JSON parse error"

### Why
OpenAI returned malformed JSON

### Fix - Already Handled
The `loan_call_generator.py` has auto-retry logic. If it fails 3 times:

1. Check model is `gpt-4` (not gpt-3.5)
2. Try different contact
3. Check API quota

---

## PROBLEM: Dashboard Loads but Crashes on Tab Click

### Symptom
Click a tab → error like "name 'db' is not defined"

### Why
Database not initialized or import failed

### Fix
```bash
# Check imports work
python -c "from loan_email_generator import *; from sales_angel_db import *; print('✅ Imports OK')"

# If error, run:
pip install --upgrade openai

# Restart:
streamlit run dashboard.py
```

---

## PROBLEM: Contact Added But Not Showing in Generate

### Symptom
Contact visible in "Contacts" tab but missing in "Generate Content" dropdown

### Why
Query caching issue

### Fix
```bash
# Streamlit cache issue - clear and restart
streamlit cache clear
streamlit run dashboard.py
```

---

## PROBLEM: Accepted Content Not Appearing in Analytics

### Symptom
Click Accept → "Saved!" but ML Analytics doesn't update

### Why
Dashboard not refreshing after click

### Fix
The dashboard has `st.rerun()` after Accept. If not working:

```bash
# Try manual refresh (F5)
# Or restart dashboard
```

---

## PROBLEM: CSV Import Fails

### Symptom
Error when uploading CSV in Contacts

### Why
CSV format wrong or missing required columns

### Fix
CSV must have (at minimum):
- `firstname`
- `company` OR `email`

Optional:
- `lastname`, `email`, `phone`, `jobtitle`, `mbti`, `disc`, `score`

**Example valid CSV:**
```
firstname,lastname,email,company,jobtitle,mbti,disc,score
John,Smith,john@example.com,Acme Corp,VP Sales,ESTJ,C-Type,75.0
```

---

## DIAGNOSTIC SCRIPT

Run this to diagnose issues:

```bash
#!/bin/bash

echo "🔍 SALES ANGEL DIAGNOSTIC"
echo ""

echo "1️⃣ Checking Python..."
python --version || echo "❌ Python not found"

echo ""
echo "2️⃣ Checking packages..."
python -c "import streamlit; print('✅ streamlit')" || echo "❌ streamlit missing"
python -c "import openai; print('✅ openai')" || echo "❌ openai missing"
python -c "import sqlite3; print('✅ sqlite3')" || echo "❌ sqlite3 missing"

echo ""
echo "3️⃣ Checking .env..."
if [ -f ".env" ]; then
    echo "✅ .env exists"
    if grep -q "OPENAI_API_KEY" .env; then
        echo "✅ OPENAI_API_KEY is set"
    else
        echo "❌ OPENAI_API_KEY not in .env"
    fi
else
    echo "❌ .env not found"
fi

echo ""
echo "4️⃣ Checking files..."
for file in dashboard.py loan_email_generator.py loan_call_generator.py sales_angel_db.py sales_angel_ml.py
do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file missing"
    fi
done

echo ""
echo "5️⃣ Checking database..."
if [ -f "sales_angel.db" ]; then
    count=$(sqlite3 sales_angel.db "SELECT COUNT(*) FROM contacts;")
    echo "✅ Database exists ($count contacts)"
else
    echo "ℹ️  Database will be created on first run"
fi

echo ""
echo "6️⃣ Testing OpenAI API..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
if os.getenv('OPENAI_API_KEY'):
    print('✅ API key found')
    from openai import OpenAI
    try:
        client = OpenAI()
        print('✅ OpenAI client initialized')
    except Exception as e:
        print(f'❌ Client error: {e}')
else:
    print('❌ API key not set')
" || echo "❌ API check failed"

echo ""
echo "✅ Diagnostic complete"
```

Save as `diagnose.sh` and run:
```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

## WHEN ALL ELSE FAILS

### Nuclear Option - Fresh Start

```bash
# 1. Stop dashboard (Ctrl+C)

# 2. Remove database
rm sales_angel.db

# 3. Clear cache
streamlit cache clear

# 4. Verify files exist
ls -la dashboard.py loan_*.py sales_angel_*.py .env

# 5. Verify .env
cat .env  # Should show OPENAI_API_KEY=sk-...

# 6. Fresh start
streamlit run dashboard.py

# 7. Add a test contact
# 8. Generate content
# 9. Review
```

---

## GETTING HELP

**If stuck:**

1. **Check files exist** in current directory
2. **Check .env has API key**
3. **Run diagnostic script**
4. **Check OpenAI API status**
5. **Clear cache and restart**

**Error message includes:**
- Exact error text
- What you were doing
- Output of diagnostic script

---

## SUCCESS INDICATORS

✅ Dashboard loads on http://localhost:8501  
✅ Can add contact  
✅ Can select contact in Generate tab  
✅ Can click Generate (starts process)  
✅ Emails appear in Review tab  
✅ Calls appear in Review tab  
✅ Can accept/reject items  
✅ ML Analytics updates  

---

**You've got this. The system is proven. Persist. 🚀**
