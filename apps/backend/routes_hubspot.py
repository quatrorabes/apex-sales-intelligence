#!/usr/bin/env python3

# apps/backend/routes_hubspot.py
from fastapi import APIRouter, HTTPException
from hubspot import HubSpot           # pip install hubspot-api-client
from os import getenv

router = APIRouter(prefix="/api/hubspot")
hubspot = HubSpot(access_token=getenv("HUBSPOT_TOKEN"))

@router.post("/import")
async def import_contacts():
	try:
		contacts = hubspot.crm.contacts.get_all()      # pulls every HubSpot contact
		# upsert into SQLite here…
		return {"imported": len(contacts)}
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
		