# Premium Enrichment Visualization API
# Provides enhanced enrichment results with analytics and formatting

from fastapi import APIRouter, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgres://", "postgresql://")

def get_contact_from_db(contact_id: str):
    """Get contact directly from PostgreSQL"""
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

@router.get("/api/v2/contacts/{contact_id}/enrichment/premium")
async def get_premium_enrichment(contact_id: str):
    """
    Get premium formatted enrichment with analytics and visual hints.
    Returns enrichment data optimized for beautiful UI presentation.
    """
    contact = get_contact_from_db(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    enrichment_data = contact.get('enrichment') or ''
    if not enrichment_data:
        raise HTTPException(status_code=404, detail="No enrichment data found")
    
    # Handle both v1 (string) and v2 (dict) formats
    if isinstance(enrichment_data, str):
        try:
            enrichment = json.loads(enrichment_data)
        except:
            enrichment = {}
    else:
        enrichment = enrichment_data
    
    # Check if this is v2 format (has 'sections' key) or v1 format (plain dict/string)
    is_v2_format = isinstance(enrichment, dict) and 'sections' in enrichment
    
    if is_v2_format:
        # V2 format: enrichment has structured sections
        sections = enrichment.get('sections', {})
    else:
        # V1 format or plain text: wrap it
        sections = {"raw_data": str(enrichment_data)}
    
    # Extract analytics
    total_chars = len(str(enrichment_data))
    section_count = len([k for k, v in sections.items() if v]) if sections else 0
    
    # Calculate quality score (0-100)
    quality_score = min(100, (section_count * 10) + min(50, total_chars // 500))
    
    # Build premium response
    return {
        "success": True,
        "contact": {
            "id": contact_id,
            "name": contact.get('name', ''),
            "company": contact.get('company', ''),
            "title": contact.get('title', '')
        },
        "enrichment": {
            "sections": sections,
            "metadata": {
                "total_characters": total_chars,
                "section_count": section_count,
                "quality_score": quality_score,
                "enriched_at": str(contact.get('enriched_at', '')),
                "version": "2.1",
                "format": "v2" if is_v2_format else "v1"
            },
            "analytics": {
                "richness": "high" if total_chars > 10000 else "medium" if total_chars > 5000 else "low",
                "completeness": f"{(section_count/14)*100:.0f}%" if section_count > 0 else "0%",
                "data_density": total_chars // max(section_count, 1) if section_count > 0 else 0
            },
            "visual_hints": {
                "primary_color": "#3B82F6" if quality_score > 70 else "#F59E0B",
                "status_badge": "premium" if quality_score > 80 else "standard"
            }
        }
    }
