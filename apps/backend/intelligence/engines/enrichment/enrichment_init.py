# apps/backend/engines/intelligence/enrichment/__init__.py
"""
APEX Sales Intelligence Enrichment Engine v3.0
10,000+ word buyer intelligence profiles with personality analysis,
pain points, and engagement strategies.
"""

from .engine_v3 import ApexEnrichmentEngineV3
from .models import EnrichmentRequest, EnrichmentResponse, ContactInfo

__all__ = [
    "ApexEnrichmentEngineV3",
    "EnrichmentRequest",
    "EnrichmentResponse",
    "ContactInfo",
]

__version__ = "3.0.0"
__author__ = "APEX Sales Intelligence"
__description__ = "Production enrichment engine for B2B sales intelligence"