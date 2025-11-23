#!/usr/bin/env python3

# apps/backend/routes_enrichment.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from apex_intelligence_engine import enrich_contact, enrich_batch

router = APIRouter(prefix="/api/apex")

class Ids(BaseModel):
	contact_ids: list[int]
	
@router.post("/enrich")
async def enrich(ids: Ids):
	try:
		results = enrich_batch(ids.contact_ids)
		return {"processed": len(results), "details": results}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
		