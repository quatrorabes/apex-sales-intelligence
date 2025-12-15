#!/usr/bin/env python3

# backend/api/routes/enrichment_v2.py
"""
APEX Enrichment API v2 - Uses ApexCustomEnrichment (Three-Stage)
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import sys
from pathlib import Path
import traceback

# Add intelligence path
BACKEND_DIR = Path(__file__).parent.parent.parent
INTELLIGENCE_PATH = BACKEND_DIR / 'intelligence'
sys.path.insert(0, str(INTELLIGENCE_PATH))

from apex_scoring_engine import ApexScoringEngine
from backend.models.database import Contact, SessionLocal
from intelligence.engines.enrichment.apex_custom_enrichment import ApexCustomEnrichment
from backend.services.enrichment_parser_v2 import EnrichmentParser

router = APIRouter()

# Initialize engines
scoring_engine = ApexScoringEngine(db_path='./apex.db')


class EnrichmentConfig:
	"""Configuration for ApexCustomEnrichment"""
	def __init__(self):
		import os
		self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
		self.openai_api_key = os.getenv('OPENAI_API_KEY')
		
		
@router.post("/api/contacts/{contact_id}/enrich")
async def enrich_contact(contact_id: str):
	"""
	Trigger deep enrichment with Apex Custom Intelligence (Three-Stage)
	Returns immediately after completion (synchronous)
	"""
	# Validate contact exists
	db = SessionLocal()
	try:
		contact = db.query(Contact).filter(Contact.id == contact_id).first
		