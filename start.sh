#!/bin/bash
echo "🚀 Starting Apex Sales Intelligence System"
echo "==========================================="

# Create directories
mkdir -p ~/projects/apex/apps/backend/intelligence/scoring
mkdir -p ~/projects/apex/apps/backend/intelligence/why_me
mkdir -p ~/projects/apex/apps/backend/intelligence/cold_call
mkdir -p ~/projects/apex/migrations
mkdir -p ~/projects/apex/enrichment_profiles
mkdir -p ~/projects/apex/data/outputs/personas

# Initialize __init__.py files
touch ~/projects/apex/apps/__init__.py
touch ~/projects/apex/apps/backend/__init__.py
touch ~/projects/apex/apps/backend/intelligence/__init__.py
touch ~/projects/apex/apps/backend/intelligence/scoring/__init__.py
touch ~/projects/apex/apps/backend/intelligence/why_me/__init__.py
touch ~/projects/apex/apps/backend/intelligence/cold_call/__init__.py

# Apply database migrations
echo "📦 Applying database migrations..."
sqlite3 ~/projects/apex/apex.db << 'SQL'
-- User Profile
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL DEFAULT 'default',
    full_name TEXT, role TEXT, company TEXT, years_experience INTEGER,
    geographic_markets TEXT, primary_product TEXT, products_services TEXT,
    sweet_spot_min INTEGER, sweet_spot_max INTEGER, asset_types TEXT, loan_types TEXT,
    differentiators TEXT, speed_advantage TEXT, relationship_advantage TEXT, specialization TEXT,
    ideal_titles TEXT, ideal_company_types TEXT, ideal_deal_triggers TEXT,
    avoid_titles TEXT, avoid_company_types TEXT,
    weight_title_match INTEGER DEFAULT 30, weight_company_match INTEGER DEFAULT 25,
    weight_deal_size_match INTEGER DEFAULT 20, weight_geography_match INTEGER DEFAULT 15, weight_timing INTEGER DEFAULT 10,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Proof Points
CREATE TABLE IF NOT EXISTS proof_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    deals_closed_12mo INTEGER, total_volume_12mo REAL, avg_close_days INTEGER, approval_rate REAL,
    notable_deals TEXT, testimonials TEXT, awards TEXT, certifications TEXT,
    lender_relationships TEXT, exclusive_programs TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Cold Call Queue
CREATE TABLE IF NOT EXISTS cold_call_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    name TEXT NOT NULL, phone TEXT, mobile TEXT, email TEXT, linkedin_url TEXT, company TEXT, title TEXT,
    source TEXT, source_context TEXT, notes TEXT,
    quick_fit_score REAL, quick_fit_reason TEXT, priority INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new', attempts INTEGER DEFAULT 0, last_attempt TEXT, outcome TEXT, contact_id INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Contact Match (Why Me)
CREATE TABLE IF NOT EXISTS contact_match (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL, user_id TEXT NOT NULL DEFAULT 'default',
    match_score REAL, fit_score REAL, relevance_score REAL, timing_score REAL, match_tier TEXT,
    hook TEXT, proof_points_matched TEXT, why_now TEXT, suggested_opening TEXT,
    talking_points TEXT, objection_handlers TEXT, connection_angles TEXT,
    generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(contact_id, user_id)
);
SQL

echo "✅ Database ready"

# Start API
echo ""
echo "🔌 Starting API server..."
cd ~/projects/apex
python api.py &
API_PID=$!

sleep 2

# Start Dashboard
echo "🎨 Starting Dashboard..."
cd ~/projects/apex/dashboard_v1
npm run dev &
DASH_PID=$!

echo ""
echo "==========================================="
echo "✅ APEX RUNNING"
echo "==========================================="
echo "📊 API:       http://localhost:8000"
echo "🎨 Dashboard: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop all services"

wait
