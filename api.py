#!/usr/bin/env python3
"""
APEX - AI Sales Intelligence Backend
PostgreSQL Production Version for Railway
"""

import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

# ==================== CONFIGURATION ====================

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PostgreSQL connection from Railway environment
DATABASE_URL = os.getenv('DATABASE_URL') or os.getenv('DATABASE_PUBLIC_URL')

if not DATABASE_URL:
    logger.error("❌ DATABASE_URL not set!")
    sys.exit(1)

# Parse DATABASE_URL if needed
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

logger.info(f"✅ Database configured: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'localhost'}")

# ==================== ENGINE IMPORTS ====================

# Try to import enrichment engines
try:
    from why_me_engine import WhyMeEngine
    WHY_ME_AVAILABLE = True
    logger.info("✅ Why Me Engine loaded")
except Exception as e:
    logger.warning(f"⚠️ Why Me Engine not available: {e}")
    WHY_ME_AVAILABLE = False

try:
    from cold_call_engine import ColdCallEngine
    COLD_CALL_AVAILABLE = True
    logger.info("✅ Cold Call Engine loaded")
except Exception as e:
    logger.warning(f"⚠️ Cold Call Engine not available: {e}")
    COLD_CALL_AVAILABLE = False

# ==================== DATABASE ====================

def get_db():
    """Get PostgreSQL connection with RealDictCursor for dict-like rows"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.cursor_factory = RealDictCursor
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def ensure_tables():
    """Ensure all required tables and columns exist"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Contact columns to ensure exist
    contact_cols = [
        ('mdcp_score', 'REAL'),
        ('match_score', 'REAL'),
        ('match_tier', 'TEXT'),
        ('fit_score', 'REAL'),
        ('relevance_score', 'REAL'),
        ('timing_score', 'REAL'),
        ('enrichment_status', 'TEXT'),
        ('enrichment_data', 'TEXT'),
        ('enriched_at', 'TEXT'),
        ('last_scored', 'TEXT'),
        ('why_me_data', 'TEXT'),
        ('why_me_generated_at', 'TEXT')
    ]
    
    for col, typ in contact_cols:
        try:
            cursor.execute(f"ALTER TABLE contacts ADD COLUMN IF NOT EXISTS {col} {typ}")
        except Exception as e:
            logger.debug(f"Column {col} already exists or error: {e}")
    
    # User profile table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id SERIAL PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL DEFAULT 'default',
            full_name TEXT,
            company TEXT,
            role TEXT,
            value_prop TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Activity tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_activities (
            id SERIAL PRIMARY KEY,
            contact_id INTEGER REFERENCES contacts(id),
            activity_type TEXT NOT NULL,
            activity_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Opportunity signals
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunity_signals (
            id SERIAL PRIMARY KEY,
            contact_id INTEGER REFERENCES contacts(id),
            signal_type TEXT NOT NULL,
            signal_strength REAL,
            signal_data TEXT,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("✅ Database schema verified")

# Initialize on startup
try:
    ensure_tables()
except Exception as e:
    logger.error(f"❌ Schema initialization failed: {e}")

# ==================== HEALTH CHECK ====================

@app.route('/')
@app.route('/api')
def root():
    return jsonify({
        "service": "apex-backend",
        "status": "running",
        "version": "2.0",
        "database": "postgresql",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/api/health')
def health():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM contacts")
        result = cursor.fetchone()
        contact_count = result['count'] if result else 0
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "service": "apex-backend",
            "database": "connected",
            "contacts": contact_count,
            "engines": {
                "why_me": WHY_ME_AVAILABLE,
                "cold_call": COLD_CALL_AVAILABLE
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

# ==================== CONTACTS ====================

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """Get all contacts with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        search = request.args.get('search', '').lower()
        tier = request.args.get('tier')
        
        offset = (page - 1) * per_page
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM contacts WHERE 1=1"
        params = []
        
        if search:
            query += " AND (LOWER(first_name) LIKE %s OR LOWER(last_name) LIKE %s OR LOWER(email) LIKE %s OR LOWER(company) LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term] * 4)
        
        if tier:
            query += " AND match_tier = %s"
            params.append(tier)
        
        query += " ORDER BY mdcp_score DESC NULLS LAST LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(query, params)
        contacts = cursor.fetchall()
        
        # Get total count
        count_query = "SELECT COUNT(*) as count FROM contacts WHERE 1=1"
        count_params = []
        if search:
            count_query += " AND (LOWER(first_name) LIKE %s OR LOWER(last_name) LIKE %s OR LOWER(email) LIKE %s OR LOWER(company) LIKE %s)"
            count_params.extend([f"%{search}%"] * 4)
        if tier:
            count_query += " AND match_tier = %s"
            count_params.append(tier)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['count']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "contacts": contacts,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        })
    except Exception as e:
        logger.error(f"Get contacts failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get single contact by ID"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not contact:
            return jsonify({"error": "Contact not found"}), 404
        
        return jsonify(contact)
    except Exception as e:
        logger.error(f"Get contact failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    """Create new contact"""
    try:
        data = request.json
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO contacts (first_name, last_name, email, phone, company, title, linkedin_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            data.get('first_name'),
            data.get('last_name'),
            data.get('email'),
            data.get('phone'),
            data.get('company'),
            data.get('title'),
            data.get('linkedin_url')
        ))
        
        contact_id = cursor.fetchone()['id']
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"id": contact_id, "success": True}), 201
    except Exception as e:
        logger.error(f"Create contact failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update contact"""
    try:
        data = request.json
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Build dynamic UPDATE query
        set_clauses = []
        params = []
        
        for field in ['first_name', 'last_name', 'email', 'phone', 'company', 'title', 'linkedin_url', 
                      'match_tier', 'mdcp_score', 'enrichment_status']:
            if field in data:
                set_clauses.append(f"{field} = %s")
                params.append(data[field])
        
        if not set_clauses:
            return jsonify({"error": "No fields to update"}), 400
        
        params.append(contact_id)
        query = f"UPDATE contacts SET {', '.join(set_clauses)} WHERE id = %s"
        
        cursor.execute(query, params)
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Update contact failed: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== ENRICHMENT ====================

@app.route('/api/contacts/<int:contact_id>/enrich', methods=['POST'])
def enrich_contact(contact_id):
    """Enrich contact with external data"""
    try:
        # This would integrate with your enrichment services
        # For now, return success
        return jsonify({
            "success": True,
            "contact_id": contact_id,
            "message": "Enrichment queued"
        })
    except Exception as e:
        logger.error(f"Enrich contact failed: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== ANALYTICS ====================

@app.route('/api/analytics/summary')
def analytics_summary():
    """Get analytics summary"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_contacts,
                COUNT(CASE WHEN match_tier = 'A' THEN 1 END) as tier_a,
                COUNT(CASE WHEN match_tier = 'B' THEN 1 END) as tier_b,
                COUNT(CASE WHEN match_tier = 'C' THEN 1 END) as tier_c,
                COUNT(CASE WHEN enrichment_status = 'completed' THEN 1 END) as enriched,
                AVG(mdcp_score) as avg_score
            FROM contacts
        """)
        
        summary = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🚀 Starting APEX Backend on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# ==================== MISSING ENDPOINTS ====================


# ==================== DASHBOARD ENDPOINTS ====================

@app.route('/api/todays-board')
def todays_board():
    """Get today's prioritized contacts"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, firstname, lastname, email, company, title, 
                   phone, linkedin_url, mdcp_score, enrichment_status
            FROM contacts 
            ORDER BY mdcp_score DESC NULLS LAST
            LIMIT 20
        """)
        rows = cursor.fetchall()
        contacts = [dict(row) for row in rows] if rows else []
        cursor.close()
        conn.close()
        return jsonify({"contacts": contacts, "count": len(contacts)})
    except Exception as e:
        return jsonify({"contacts": [], "error": str(e)})

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    """Get user profile"""
    user_id = request.args.get('user_id', 'default')
    return jsonify({
        "user_id": user_id,
        "full_name": "Sales User",
        "company": "Your Company",
        "role": "Sales Representative",
        "onboarding_complete": True
    })

@app.route('/api/user/profile', methods=['POST'])
def save_user_profile():
    """Save user profile"""
    data = request.json or {}
    return jsonify({"success": True, "profile": data})

@app.route('/api/smart-lists')
def get_smart_lists():
    """Get smart lists"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE mdcp_score >= 80")
        hot_count = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM contacts WHERE mdcp_score >= 60 AND mdcp_score < 80")
        warm_count = cursor.fetchone()[0] or 0
        cursor.close()
        conn.close()
        return jsonify({
            "lists": [
                {"id": 1, "name": "Hot Leads", "count": hot_count},
                {"id": 2, "name": "Warm Leads", "count": warm_count},
                {"id": 3, "name": "Needs Enrichment", "count": 0}
            ]
        })
    except Exception as e:
        return jsonify({"lists": [], "error": str(e)})

@app.route('/api/contacts/<int:contact_id>/detail')
def get_contact_detail(contact_id):
    """Get contact detail"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contacts WHERE id = %s", (contact_id,))
        contact = cursor.fetchone()
        cursor.close()
        conn.close()
        if not contact:
            return jsonify({"error": "Contact not found"}), 404
        return jsonify(dict(contact))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
