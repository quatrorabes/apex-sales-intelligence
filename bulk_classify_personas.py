#!/usr/bin/env python3
"""
Bulk Persona Classifier for Apex (LOCAL SQLite)

- Reads contacts from apex.db
- Uses Apex8PersonaClassifier to assign one of 8 personas
- Writes persona, confidence, multiplier, criteria, persona_date back to DB
- Safe to re-run (will skip already-classified by default)

Environment: LOCAL (SQLite)
"""

import os
import sys
import json
from datetime import datetime
import sqlite3

# Ensure we can import the classifier module
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLASSIFIER_PATH = os.path.join(BASE_DIR, 'apps', 'backend', 'intelligence', 'engines', 'classification')
if CLASSIFIER_PATH not in sys.path:
    sys.path.insert(0, CLASSIFIER_PATH)

try:
    from apex_8persona_classifier import Apex8PersonaClassifier
except ImportError as e:
    print(f"❌ Could not import Apex8PersonaClassifier: {e}")
    sys.exit(1)

DB_PATH = os.path.join(BASE_DIR, 'apex.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_contacts(limit: int = 500, include_existing: bool = False):
    """
    Fetch contacts that need persona classification.
    - include_existing=False: only persona IS NULL
    - include_existing=True: all contacts (reclassify)
    """
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

    sql = """
        UPDATE contacts
        SET persona = ?,
            persona_confidence = ?,
            persona_multiplier = ?,
            persona_criteria = ?,
            persona_date = ?
        WHERE id = ?
    """
    cur.execute(sql, (persona, confidence, multiplier, criteria, ts, contact_id))
    conn.commit()
    conn.close()


def main(limit: int = 500, include_existing: bool = False):
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
    parser.add_argument("--limit", type=int, default=500, help="Max contacts to classify")
    parser.add_argument(
        "--reclassify-existing",
        action="store_true",
        help="If set, reclassify even if persona is already set"
    )
    args = parser.parse_args()
    main(limit=args.limit, include_existing=args.reclassify_existing)
