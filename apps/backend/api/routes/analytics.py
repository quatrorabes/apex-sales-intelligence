#!/usr/bin/env python3

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, List

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
	"""Get dashboard statistics"""
	from backend.database import Contact, EmailSend, EmailEvent, ContactReply, LeadScore
	
	total_contacts = db.query(Contact).count()
	
	total_sent = db.query(EmailSend).filter(
		EmailSend.status == 'sent'
	).count()
	
	total_opens = db.query(EmailEvent).filter(
		EmailEvent.event_type == 'open'
	).count()
	
	total_clicks = db.query(EmailEvent).filter(
		EmailEvent.event_type == 'click'
	).count()
	
	total_replies = db.query(ContactReply).count()
	
	open_rate = (total_opens / total_sent * 100) if total_sent > 0 else 0
	click_rate = (total_clicks / total_sent * 100) if total_sent > 0 else 0
	reply_rate = (total_replies / total_sent * 100) if total_sent > 0 else 0
	
	return {
		"total_contacts": total_contacts,
		"total_emails_sent": total_sent,
		"total_opens": total_opens,
		"total_clicks": total_clicks,
		"total_replies": total_replies,
		"open_rate": round(open_rate, 2),
		"click_rate": round(click_rate, 2),
		"reply_rate": round(reply_rate, 2)
	}