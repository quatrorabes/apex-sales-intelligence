#!/bin/bash
# 🔄 Reclassify ALL contacts with tuned rules (erases old personas)

set -e

echo "════════════════════════════════════════════════════"
echo "🔥 RECLASSIFY ALL CONTACTS (TUNED RULES)"
echo " - Resets personas to NULL"
echo " - Runs bulk classifier with stricter thresholds"
echo " - Shows before/after distribution"
echo "════════════════════════════════════════════════════"

DB_PATH="apex.db"

if [ ! -f "$DB_PATH" ]; then
  echo "❌ apex.db not found"
  exit 1
fi

# 1) Show current distribution
echo
echo "📊 BEFORE (current personas):"
sqlite3 "$DB_PATH" << 'SQL'
SELECT persona, COUNT(*) AS count FROM contacts WHERE persona IS NOT NULL GROUP BY persona ORDER BY count DESC;
SQL

# 2) Reset all personas to NULL
echo
echo "🧹 Resetting personas to NULL..."
sqlite3 "$DB_PATH" "UPDATE contacts SET persona = NULL, persona_confidence = NULL, persona_multiplier = 1.0, persona_criteria = NULL, persona_date = NULL;"

# 3) Run bulk classifier
echo
echo "🚀 Running bulk classification (limit 2000)..."
./bulk_classify_personas.py --limit 2000 --reclassify-existing || {
  echo "❌ Bulk classification failed"
  exit 1
}

# 4) Show new distribution
echo
echo "📊 AFTER (new personas):"
sqlite3 "$DB_PATH" << 'SQL'
SELECT persona, COUNT(*) AS count, ROUND(AVG(COALESCE(persona_confidence,0)),1) AS avg_conf FROM contacts WHERE persona IS NOT NULL GROUP BY persona ORDER BY count DESC;
SQL

echo
echo "✅ Reclassification complete. Check /api/todays-board to see relationships populate."
echo "════════════════════════════════════════════════════"
