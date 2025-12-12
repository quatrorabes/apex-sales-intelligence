"""Sales Playbook API Routes"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import os

router = APIRouter(prefix="/api/playbook", tags=["playbook"])

# Pydantic models for request/response
class PlaybookOverview(BaseModel):
    companyName: str
    website: Optional[str] = None
    tagline: Optional[str] = None

class PlaybookProducts(BaseModel):
    products: List[str] = []

class PlaybookValueProps(BaseModel):
    valueProps: List[str] = []

class PlaybookICP(BaseModel):
    industries: List[str] = []
    companySize: Optional[str] = None
    geography: Optional[str] = None
    titles: List[str] = []

class PlaybookPainPoints(BaseModel):
    painPoints: List[str] = []

class PlaybookProofPoints(BaseModel):
    proofPoints: List[str] = []

class PlaybookCompetitors(BaseModel):
    competitors: List[str] = []

class SalesPlaybook(BaseModel):
    overview: Optional[PlaybookOverview] = None
    products: Optional[PlaybookProducts] = None
    valueProps: Optional[PlaybookValueProps] = None
    icp: Optional[PlaybookICP] = None
    painPoints: Optional[PlaybookPainPoints] = None
    proofPoints: Optional[PlaybookProofPoints] = None
    competitors: Optional[PlaybookCompetitors] = None
    lastUpdated: Optional[datetime] = None

# In-memory storage (replace with database later)
PLAYBOOK_STORAGE = {}

@router.get("", response_model=SalesPlaybook)
async def get_playbook():
    """Get the current sales playbook configuration"""
    if not PLAYBOOK_STORAGE:
        # Return empty playbook structure
        return SalesPlaybook()
    return SalesPlaybook(**PLAYBOOK_STORAGE)

@router.post("", response_model=SalesPlaybook)
async def save_playbook(playbook: SalesPlaybook):
    """Save or update the sales playbook configuration"""
    playbook.lastUpdated = datetime.now()
    playbook_dict = playbook.dict(exclude_none=True)
    PLAYBOOK_STORAGE.clear()
    PLAYBOOK_STORAGE.update(playbook_dict)
    return playbook

@router.get("/overview", response_model=PlaybookOverview)
async def get_overview():
    """Get company overview section"""
    overview = PLAYBOOK_STORAGE.get("overview", {})
    return PlaybookOverview(**overview) if overview else PlaybookOverview(companyName="")

@router.post("/overview", response_model=PlaybookOverview)
async def save_overview(overview: PlaybookOverview):
    """Save company overview section"""
    if "overview" not in PLAYBOOK_STORAGE:
        PLAYBOOK_STORAGE["overview"] = {}
    PLAYBOOK_STORAGE["overview"] = overview.dict()
    return overview
