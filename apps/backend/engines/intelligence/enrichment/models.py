# apps/backend/engines/intelligence/enrichment/models.py
"""Data models for enrichment request/response"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from datetime import datetime

class ContactInfo(BaseModel):
    """Contact information (all fields as strings, UUID preserved)"""
    id: str  # UUID as string, NEVER integer
    name: str
    title: str
    company: str
    email: Optional[str] = None
    linkedin_url: Optional[str] = None

class EnrichmentRequest(BaseModel):
    """Request to enrich a contact"""
    contact_ids: Optional[List[str]] = None  # UUID strings

class EnrichmentMetadata(BaseModel):
    """Metadata about enrichment"""
    enrichment_engine: str = "v3.0"
    total_sections: int
    character_count: int
    word_count: int
    research_sources: List[str]
    generated_at: str  # ISO format
    processing_time_seconds: float

class EnrichmentResponse(BaseModel):
    """Response from enrichment engine"""
    success: bool
    contact_id: Optional[str] = None  # UUID as string
    contact_info: Optional[ContactInfo] = None
    sections: Dict[str, str] = {}  # 10 sections: executive_summary, personality_profile, etc.
    raw_profile: str = ""  # Full markdown
    metadata: Optional[EnrichmentMetadata] = None
    preserved_fields: Dict[str, Any] = {}  # All other contact fields preserved
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
