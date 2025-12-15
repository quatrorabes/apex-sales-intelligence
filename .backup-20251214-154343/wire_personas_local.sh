#!/bin/bash
# 🚀 WIRE PERSONAS INTO APEX (LOCAL SQLITE)
# - Runs bulk persona classification
# - Prints persona stats from apex.db
# - Verifies /api/todays-board sees relationships

set -e

echo "════════════════════════════════════════════════════════════════════"
echo "🔥 APEX PERSONA WIRING (LOCAL)"
echo " - Bulk classify contacts with Apex8PersonaClassifier"
echo " - Verify personas in DB"
echo " - Check todays-board relationships"
echo "════════════════════════════════════════════════════════════════════"
echo

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="${BASE_DIR}/apex.db"

if [ ! -f "${DB_PATH}" ]; then
  echo "❌ apex.db not found at: ${DB_PATH}"
  exit 1
fi

echo "📂 Using DB: ${DB_PATH}"

# 1) Ensure bulk_classify_personas.py exists
if [ ! -f "${BASE_DIR}/bulk_classify_personas.py" ]; then
  echo "📄 Creating bulk_classify_personas.py ..."
  cat > "${BASE_DIR}/bulk_classify_personas.py" << 'PYEOF'
#!/usr/bin/env python3
"""
Bulk Persona Classifier for Apex (LOCAL SQLite)

- Reads contacts from apex.db
- Uses Apex8PersonaClassifier to assign one of 8 personas
- Writes persona, confidence, multiplier, criteria, persona_date back to DB
"""

import os
import sys
import json
from datetime import datetime
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'apex.db')

CLASSIFIER_PATH = os.path.join(
    BASE_DIR, 'apps', 'backend', 'intelligence', 'engines', 'classification'
)
if CLASSIFIER_PATH not in sys.path:
    sys.path.insert(0, CLASSIFIER_PATH)

try:
    from apex_8persona_classifier import Apex8PersonaClassifier
except ImportError as e:
    print(f"❌ Could not import Apex8PersonaClassifier: {e}")
    sys.exit(1)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_contacts(limit: int = 1000, include_existing: bool = False):
    conn = get_db()
    cur = conn.cursor()
    if include_existing:
        sql = "SELECT * FROM contacts ORDER BY id ASC LIMIT ?"
        params = (limit,)
    else:
        sql = "SELECT * FROM contacts WHERE persona IS NULL ORDER BY id ASC LIMIT ?"
        params = (limit,)
    cur.execute(sql, params)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def update_persona(contact_id: int, result: dict):
    conn = get_db()
    cur = conn.cursor()
    persona = result.get('persona')
    confidence = result.get('confidence_score', 0)
    multiplier = float(result.get('multiplier', 1.0))
    criteria = json.dumps(result.get('criteria', []))
    ts = datetime.now().isoformat()
    cur.execute(
        """
        UPDATE contacts
        SET persona = ?,
            persona_confidence = ?,
            persona_multiplier = ?,
            persona_criteria = ?,
            persona_date = ?
        WHERE id = ?
        """,
        (persona, confidence, multiplier, criteria, ts, contact_id),
    )
    conn.commit()
    conn.close()


def main(limit: int = 1000, include_existing: bool = False):
    print("════════════════════════════════════════════════════")
    print("🔎 APEX BULK PERSONA CLASSIFICATION (LOCAL SQLITE)")
    print(f"DB: {DB_PATH}")
    print(f"Limit: {limit} | Reclassify existing: {include_existing}")
    print("════════════════════════════════════════════════════")

    classifier = Apex8PersonaClassifier()
    contacts = fetch_contacts(limit=limit, include_existing=include_existing)
    total = len(contacts)
    if not total:
        print("No contacts found matching criteria (persona NULL or all).")
        return

    classified = 0
    for c in contacts:
        cid = c.get('id')
        name = c.get('name')
        print(f"\n→ Classifying contact {cid}: {name}")
        result = classifier.classify_contact(c)
        update_persona(cid, result)
        print(f"   Persona: {result['persona']} (score {result['confidence_score']})")
        classified += 1

    print("\n════════════════════════════════════════════════════")
    print(f"✅ Completed. Classified {classified} of {total} contacts.")
    print("════════════════════════════════════════════════════")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bulk persona classifier for Apex (SQLite).")
    parser.add_argument("--limit", type=int, default=1000, help="Max contacts to classify")
    parser.add_argument(
        "--reclassify-existing",
        action="store_true",
        help="If set, reclassify even if persona is already set",
    )
    args = parser.parse_args()
    main(limit=args.limit, include_existing=args.reclassify_existing)
PYEOF
  chmod +x "${BASE_DIR}/bulk_classify_personas.py"
fi

# 2) Run bulk classification
echo
echo "🚀 Running bulk persona classification (up to 1000 contacts)..."
"${BASE_DIR}/bulk_classify_personas.py" --limit 1000 || {
  echo "❌ Bulk classification failed"
  exit 1
}

# 3) Show persona stats from DB
echo
echo "📊 Persona distribution (top 10 rows):"
sqlite3 "${DB_PATH}" << 'SQL'
.headers on
.mode column
SELECT persona, COUNT(*) AS count, AVG(COALESCE(persona_confidence,0)) AS avg_conf
FROM contacts
WHERE persona IS NOT NULL
GROUP BY persona
ORDER BY count DESC
LIMIT 10;
SQL

# 4) Hit todays-board to confirm relationships are feeding from personas
echo
echo "📈 Checking /api/todays-board (relationships + new_prospects)..."
curl -s http://localhost:8000/api/todays-board | jq '{date, time, relationships: {total: .relationships.total, urgent: .relationships.urgent_count, warm: .relationships.warm_count}, new_prospects: {total: .new_prospects.total, hot: .new_prospects.hot_count, qualified: .new_prospects.qualified_count}}'

echo
echo "✅ Personas wired locally. Dashboard_v1 can now render relationship tiers driven by persona + MDCP."
echo "   Next step: mirror this in production via Railway (same pattern, Postgres instead of SQLite)."
echo "════════════════════════════════════════════════════════════════════"
