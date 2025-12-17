import os, json, logging
from fastapi import APIRouter, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor

router = APIRouter(tags=['outreach'])
logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv('DATABASE_URL')

@router.post('/api/contacts/{contact_id}/generate-email')
async def generate_email(contact_id: str):
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT name, title, company FROM contacts WHERE id = %s", (contact_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        email = f"""Subject: Quick thought on {row['company']}

Hi {row['name']},

I came across your profile and thought you might find value in what we do.

Your role as {row['title']} at {row['company']} caught my attention.

Would love to grab 15 minutes next week to explore if there's a fit.

Best"""
        
        return {'email': email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/api/contacts/{contact_id}/generate-call-script')
async def generate_call_script(contact_id: str):
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT name, title, company FROM contacts WHERE id = %s", (contact_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        script = f"""CALL SCRIPT: {row['name']} ({row['title']})

OPENING:
Hi {row['name']}, I hope I'm not catching you at a bad time. 
I'm calling because I came across your profile at {row['company']}.

HOOK:
We work with companies like {row['company']} to improve efficiency and revenue.

QUESTION:
Do you have about 15 minutes?

IF YES:
Great! Let's grab coffee or hop on a quick call.

IF NO:
No problem! Can I send you a 2-minute video instead?"""
        
        return {'script': script}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
