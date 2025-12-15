#!/usr/bin/env python3

from fastapi import APIRouter, HTTPException
from typing import Optional, List
from apps.backend.intelligence import ApexScoringEngine

router = APIRouter(prefix="/api/scoring", tags=["scoring"])

@router.get("/score/{contact_id}")
async def get_contact_score(contact_id: int):
		"""Get MDCP/RSS/Priority scores for a contact"""
		try:
				engine = ApexScoringEngine('apex.db')
				result = engine.score_contact(contact_id)
				return result
		except ValueError as e:
				raise HTTPException(status_code=404, detail=str(e))
		except Exception as e:
				raise HTTPException(status_code=500, detail=str(e))
			
@router.get("/score/all")
async def score_all_contacts(lead_type: Optional[str] = None):
		"""Score all contacts (optionally filtered by type)"""
		try:
				engine = ApexScoringEngine('apex.db')
				results = engine.score_all_contacts(lead_type)
				return {
						'total': len(results),
						'contacts': results[:50],  # Return top 50
						'lead_type_filter': lead_type
				}
		except Exception as e:
				raise HTTPException(status_code=500, detail=str(e))
			
@router.get("/priority/immediate")
async def get_immediate_priority_contacts():
		"""Get contacts requiring immediate action"""
		try:
				engine = ApexScoringEngine('apex.db')
				results = engine.score_all_contacts()
				immediate = [c for c in results if c['urgency_level'] == 'IMMEDIATE']
				return {
						'count': len(immediate),
						'contacts': immediate
				}
		except Exception as e:
				raise HTTPException(status_code=500, detail=str(e))
			
@router.get("/lifecycle/{stage}")
async def get_contacts_by_lifecycle(stage: str):
		"""Get contacts by lifecycle stage"""
		try:
				engine = ApexScoringEngine('apex.db')
				engine.cursor.execute("""
						SELECT * FROM v_latest_contact_scores
						WHERE lifecycle_stage = ?
						ORDER BY priority_score DESC
				""", (stage.upper(),))
			
				rows = engine.cursor.fetchall()
				return {
						'stage': stage,
						'count': len(rows),
						'contacts': [dict(row) for row in rows]
				}
		except Exception as e:
				raise HTTPException(status_code=500, detail=str(e))
			