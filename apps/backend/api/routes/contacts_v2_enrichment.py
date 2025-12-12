#!/usr/bin/env python3

"""
V2 Contact Enrichment & Analytics Routes
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
import sys
import json
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import os

router = APIRouter(prefix="/api/v2/contacts", tags=["Enrichment V2"])

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://")


def get_contact_from_db(contact_id: str):
    """Get contact directly from Postgres"""
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(contact) if contact else None
    except Exception as e:
        print(f"Error fetching contact: {e}")
        return None


@router.get("/{contact_id}/enrichment/analytics")
async def get_enrichment_analytics(contact_id: str) -> Dict[str, Any]:
    """Get enrichment analytics for Intelligence/Qualification tabs."""
    contact = get_contact_from_db(contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Parse enrichment JSON
    enrichment = contact.get('enrichment') or {}

    # Handle both v1 (string) and v2 (dict) formats
    if isinstance(enrichment, str):
        try:
            enrichment = json.loads(enrichment)
        except:
            enrichment = {}

    sections = enrichment.get('sections', {}) if isinstance(enrichment, dict) else {}

    return {
        "contact_id": contact_id,
        "enriched_at": contact.get('enriched_at'),
        "enrichment_status": contact.get('enrichment_status', 'pending'),

        # Intelligence sections
        "sections": {
            "overview": sections.get('overview', ''),
            "company_overview": sections.get('company_overview', ''),
            "pain_points_and_challenges": sections.get('pain_points_and_challenges', ''),
            "budget_and_authority": sections.get('budget_and_authority', ''),
            "sales_intel": sections.get('sales_intel', ''),
            "opportunity_insights": sections.get('opportunity_insights', ''),
        },

        # Qualification scores
        "scores": {
            "mdcp": contact.get('mdcp_score', 0),
            "bant": contact.get('bant_total_score', 0),
            "spice": contact.get('spice_total_score', 0),
            "apex": contact.get('apex_score', 0),
            "unified": contact.get('unified_qualification_score', 0),
        },

        # Metadata
        "metadata": {
            "total_sections": len([s for s in sections.values() if s]),
            "character_count": sum(len(str(v)) for v in sections.values()),
            "has_pain_points": bool(sections.get('pain_points_and_challenges')),
            "has_budget_info": bool(sections.get('budget_and_authority')),
        }
    }


@router.get("/{contact_id}/enrichment/raw")
async def get_raw_enrichment(contact_id: str) -> Dict[str, Any]:
    """Get raw enrichment data for Raw Data tab."""
    contact = get_contact_from_db(contact_id)

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    enrichment = contact.get('enrichment') or {}
    if isinstance(enrichment, str):
        try:
            enrichment = json.loads(enrichment)
        except:
            enrichment = {}

    return {
        "contact_id": contact_id,
        "enriched_at": contact.get('enriched_at'),
        "enrichment_status": contact.get('enrichment_status', 'pending'),
        "raw_data": enrichment,
        "metadata": {
            "size_bytes": len(json.dumps(enrichment)),
            "keys": list(enrichment.keys()) if isinstance(enrichment, dict) else [],
            "has_sections": 'sections' in enrichment if isinstance(enrichment, dict) else False,
        }
    }
