#!/usr/bin/env python3
"""
Apex 8-Persona bulk classifier

Usage:
  python bulk_classify_personas_prod.py --limit 5000 --reclassify-existing
"""

import os
import sys
import argparse
import logging

import psycopg2
from psycopg2.extras import RealDictCursor

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("bulk_persona_classifier")

# -----------------------------------------------------------------------------
# Wire up classifier module (same pathing style as api.py)
# -----------------------------------------------------------------------------
CLASSIFICATION_PATH = os.path.join(
    os.path.dirname(__file__),
    "apps/backend/intelligence/engines/classification",
)
if CLASSIFICATION_PATH not in sys.path:
    sys.path.insert(0, CLASSIFICATION_PATH)

try:
    from apex_8persona_classifier import Apex8PersonaClassifier  # type: ignore
    persona_engine = Apex8PersonaClassifier()
    PERSONA_AVAILABLE = True
    logger.info("✅ 8-Persona Classifier loaded")
except Exception as e:
    logger.error("❌ Failed to load Apex8PersonaClassifier: %s", e)
    persona_engine = None
    PERSONA_AVAILABLE = False

# -----------------------------------------------------------------------------
# DB helpers
# -----------------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("❌ DATABASE_URL is not set. Aborting.")
    sys.exit(1)


def get_db():
    return psycopg2.connect(DATABASE_URL)


def dict_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)


# -----------------------------------------------------------------------------
# Classification logic
# -----------------------------------------------------------------------------
def ensure_persona_columns(conn):
    cur = conn.cursor()
    columns = [
        ("persona", "VARCHAR(50)"),
        ("persona_confidence", "REAL"),
    ]
    for name, col_type in columns:
        try:
            cur.execute(f"ALTER TABLE contacts ADD COLUMN {name} {col_type};")
            logger.info("Added column: %s", name)
        except Exception:
            conn.rollback()
    conn.commit()


def fetch_contacts_to_classify(conn, limit: int, reclassify_existing: bool):
    cur = dict_cursor(conn)

    base_select = """
        SELECT
            id,
            name,
            title,
            company,
            email,
            phone,
            linkedin_url AS linkedinurl,
            profile_content
        FROM contacts
    """

    if reclassify_existing:
        logger.info("Reclassifying ALL contacts (up to %d)...", limit)
        query = base_select + " ORDER BY id LIMIT %s"
        params = (limit,)
    else:
        logger.info("Classifying ONLY contacts missing persona (up to %d)...", limit)
        query = base_select + " WHERE persona IS NULL OR persona = '' ORDER BY id LIMIT %s"
        params = (limit,)

    cur.execute(query, params)
    rows = cur.fetchall()
    logger.info("Fetched %d contacts for persona classification", len(rows))
    return rows


def classify_contact(row: dict):
    if not PERSONA_AVAILABLE or not persona_engine:
        raise RuntimeError("Persona classifier not available")

    persona_input = {
        "title": row.get("title") or "",
        "job_title": row.get("title") or "",
        "company": row.get("company") or "",
        "industry": "",
        "profile_content": row.get("profile_content") or "",
    }

    result = persona_engine.classify_contact(persona_input)
    persona = result.get("persona") or "unclassified"
    confidence = float(result.get("confidence_score") or 0.0)
    return persona, confidence, result


def bulk_classify(limit: int, reclassify_existing: bool, dry_run: bool = False):
    if not PERSONA_AVAILABLE:
        logger.error("❌ Persona engine is not available. Exiting.")
        return

    conn = get_db()
    ensure_persona_columns(conn)

    contacts = fetch_contacts_to_classify(conn, limit, reclassify_existing)
    if not contacts:
        logger.info("No contacts to classify. Nothing to do.")
        conn.close()
        return

    cur = conn.cursor()
    updated = 0
    errors = 0

    for row in contacts:
        cid = row["id"]
        try:
            persona, confidence, raw = classify_contact(row)
            logger.info(
                "ID=%s -> persona=%s (%.2f) | %s | %s | criteria=%s",
                cid,
                persona,
                confidence,
                row.get("title"),
                row.get("company"),
                ", ".join(raw.get("criteria") or [])[:200],
            )

            if not dry_run:
                cur.execute(
                    """
                    UPDATE contacts
                    SET persona = %s,
                        persona_confidence = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (persona, confidence, cid),
                )
            updated += 1
        except Exception as e:
            logger.error("Error classifying contact %s: %s", cid, e)
            conn.rollback()
            errors += 1

    if not dry_run:
        conn.commit()
    conn.close()

    logger.info("✅ Persona classification complete: %d updated, %d errors", updated, errors)


# -----------------------------------------------------------------------------
# CLI entrypoint
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Bulk classify personas for contacts.")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--reclassify-existing", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    logger.info("Starting bulk persona classification job...")
    logger.info("Limit=%d, reclassify_existing=%s, dry_run=%s",
                args.limit, args.reclassify_existing, args.dry_run)

    bulk_classify(args.limit, args.reclassify_existing, args.dry_run)


if __name__ == "__main__":
    main()
