#!/usr/bin/env python3
"""
APEX Intelligence Platform - Production API
Minimal FastAPI with Import Filters
"""

import os
import json
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Database setup
DATABASE = os.getenv("DATABASE_PATH", "apex.db")

@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize FastAPI
app = FastAPI(
    title="APEX Intelligence Platform",
    version="1.0-SIMPLE",
    description="Import Filters + Contact Management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Import Filters API
from api.import_filters import router as import_filters_router
app.include_router(import_filters_router)

print("✅ Import Filters API registered at /api/import/*")

# CORS middleware
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,http://localhost:8000,https://apex-sales-intelligence.vercel.app,https://*.vercel.app"
).split(",")


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== PYDANTIC MODELS ====================

class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    title: Optional[str] = None
    industry: Optional[str] = None

# ==================== ROOT & HEALTH ====================

@app.get("/", tags=["System"])
async def root():
    """API root endpoint"""
    return {
        "name": "APEX Intelligence Platform",
        "version": "1.0-SIMPLE",
        "status": "operational",
        "features": [
            "Import Filters",
            "Contact Management",
            "Lead Status Validation",
            "Lifecycle Stage Validation"
        ],
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()[0]
        return {
            "status": "healthy",
            "contacts": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# ==================== CONTACT MANAGEMENT ====================

@app.get("/api/contacts", tags=["Contacts"])
async def list_contacts(
    limit: int = 100,
    offset: int = 0,
    sort_by: str = "id",
    order: str = "desc"
):
    """List contacts with pagination"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            valid_sorts = ["id", "name", "company", "created_at"]
            if sort_by not in valid_sorts:
                sort_by = "id"
            
            query = f"""
                SELECT * FROM contacts 
                ORDER BY {sort_by} {order.upper()}
                LIMIT ? OFFSET ?
            """
            
            cursor.execute(query, (limit, offset))
            contacts = [dict(row) for row in cursor.fetchall()]
            
            cursor.execute("SELECT COUNT(*) FROM contacts")
            total = cursor.fetchone()[0]
            
            return {
                "contacts": contacts,
                "total": total,
                "limit": limit,
                "offset": offset
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts/{contact_id}", tags=["Contacts"])
async def get_contact(contact_id: int):
    """Get single contact by ID"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,))
            row = cursor.fetchone()
            
            if not row:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            return dict(row)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/contacts", tags=["Contacts"])
async def create_contact(contact: ContactCreate):
    """Create new contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Check for duplicates
            if contact.email:
                cursor.execute("SELECT id FROM contacts WHERE email = ?", (contact.email,))
                if cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Contact with this email already exists")
            
            cursor.execute("""
                INSERT INTO contacts (name, email, phone, company, title, industry, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                contact.name,
                contact.email,
                contact.phone,
                contact.company,
                contact.title,
                contact.industry,
                datetime.now().isoformat()
            ))
            conn.commit()
            contact_id = cursor.lastrowid
            
            return {
                "id": contact_id,
                "message": "Contact created successfully"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/contacts/{contact_id}", tags=["Contacts"])
async def update_contact(contact_id: int, contact: ContactUpdate):
    """Update existing contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            updates = []
            values = []
            
            for field, value in contact.dict(exclude_unset=True).items():
                updates.append(f"{field} = ?")
                values.append(value)
            
            if not updates:
                raise HTTPException(status_code=400, detail="No fields to update")
            
            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(contact_id)
            
            query = f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            return {"id": contact_id, "message": "Contact updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/contacts/{contact_id}", tags=["Contacts"])
async def delete_contact(contact_id: int):
    """Delete a contact"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Contact not found")
            
            return {"message": "Contact deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("=" * 70)
    print("🚀 APEX Intelligence Platform Starting...")
    print("=" * 70)
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM contacts")
            count = cursor.fetchone()[0]
            print(f"✅ Database connected: {count} contacts")
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
    
    print("✅ Import Filters API ready")
    print("🎯 APEX Platform operational!")
    print("=" * 70)
    
@app.get("/api/todays-board", tags=["Dashboard"])
async def get_todays_board():
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Total contacts
        cursor.execute("SELECT COUNT(*) FROM contacts")
        total = cursor.fetchone()[0]
        
        # Enriched contacts
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE enriched = 1")
        enriched = cursor.fetchone()[0]
        
        # High priority
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE urgency_level = 'HIGH'")
        high_priority = cursor.fetchone()[0]
        
        return {
            "total_contacts": total,
            "enriched": enriched,
            "high_priority": high_priority,
            "in_call_queue": 0
        }
    
@app.get("/api/user/profile", tags=["User"])
async def get_user_profile(user_id: str = "default"):
    return {
        "user_id": user_id,
        "name": "Sales User",
        "role": "Sales Rep"
    }
    
@app.post("/api/batch/rescore", tags=["Scoring"])
async def batch_rescore():
    return {"message": "Rescoring initiated", "status": "success"}

# Add this to apps/backend/main.py

@app.get("/api/todays-board", tags=["Dashboard"])
async def todays_board():
    """
    Dashboard statistics - returns top contacts and stats
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get top contacts by score
        cursor.execute("""
            SELECT * FROM contacts 
            ORDER BY COALESCE(match_score, 0) DESC, id DESC 
            LIMIT 20
        """)
        contacts = [dict(row) for row in cursor.fetchall()]
        
        # Get total contacts
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        total = cursor.fetchone()['count']
        
        # Get enriched count
        cursor.execute("""
            SELECT COUNT(*) as count FROM contacts 
            WHERE enrichment_status = 'completed'
        """)
        enriched = cursor.fetchone()['count']
        
        return {
            "contacts": contacts,
            "count": len(contacts),
            "stats": {
                "total_contacts": total,
                "enriched": enriched
            }
        }
    


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    config = {
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", 8000)),
        "reload": os.getenv("ENVIRONMENT", "development") == "development",
        "log_level": "info"
    }
    
    print("🚀 APEX Intelligence Platform")
    print(f"📍 Server: http://{config['host']}:{config['port']}")
    print(f"📚 Docs: http://{config['host']}:{config['port']}/docs")
    
    uvicorn.run("main:app", **config)
    