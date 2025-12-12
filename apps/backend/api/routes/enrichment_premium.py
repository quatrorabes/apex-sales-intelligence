# Premium Enrichment Visualization API
# Provides enhanced enrichment results with analytics and formatting

from fastapi import APIRouter, HTTPException
from services import contact_service
from services.enrichment_parser_v2 import EnrichmentParser
from datetime import datetime
import re

router = APIRouter()

@router.get("/api/v2/contacts/{contact_id}/enrichment/premium")
async def get_premium_enrichment(contact_id: str):
    """
    Get premium formatted enrichment with analytics and visual hints.
    Returns enrichment data optimized for beautiful UI presentation.
    """
    contact = contact_service.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    enrichment_data = contact.get('enrichment', '')
    if not enrichment_data:
        raise HTTPException(status_code=404, detail="No enrichment data found")
    
    parser = EnrichmentParser()
    parsed = parser.parse(enrichment_data)
    
    # Extract analytics
    total_chars = len(enrichment_data)
    sections = parsed.get('sections', {})
    section_count = len([k for k, v in sections.items() if v])
    
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
                "enriched_at": contact.get('enriched_at', ''),
                "version": "2.1"
            },
            "analytics": {
                "richness": "high" if total_chars > 10000 else "medium" if total_chars > 5000 else "low",
                "completeness": f"{(section_count/14)*100:.0f}%",
                "data_density": total_chars / max(section_count, 1)
            },
            "visual_hints": {
                "primary_color": "#3B82F6" if quality_score > 70 else "#F59E0B",
                "status_badge": "premium" if quality_score > 80 else "standard"
            }
        }
    }
