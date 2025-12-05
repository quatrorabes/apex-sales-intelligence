-- =============================================================================
-- APEX USER SYSTEM + MATCH SCORING + COLD CALL
-- =============================================================================

-- USER PROFILE: Who is using Apex and what do they offer?
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL DEFAULT 'default',
    
    -- Identity
    full_name TEXT,
    role TEXT,                          -- 'commercial_banker', 'sba_lender', 'cre_broker', 'mortgage_broker'
    company TEXT,
    years_experience INTEGER,
    geographic_markets TEXT,            -- JSON array: ["Los Angeles", "Orange County", "San Diego"]
    
    -- Products & Services
    primary_product TEXT,               -- Main offering
    products_services TEXT,             -- JSON array of all products
    sweet_spot_min INTEGER,             -- Deal size minimum
    sweet_spot_max INTEGER,             -- Deal size maximum
    asset_types TEXT,                   -- JSON array: ["Multifamily", "Retail", "Industrial"]
    loan_types TEXT,                    -- JSON array: ["Bridge", "Perm", "Construction", "SBA 7a"]
    
    -- Unique Value Proposition
    differentiators TEXT,               -- What makes them special (free text)
    speed_advantage TEXT,               -- e.g., "Close in 21 days vs industry 45"
    relationship_advantage TEXT,        -- e.g., "Direct to 12 bridge lenders"
    specialization TEXT,                -- e.g., "Value-add multifamily expert"
    
    -- Ideal Client Profile
    ideal_titles TEXT,                  -- JSON array
    ideal_company_types TEXT,           -- JSON array
    ideal_deal_triggers TEXT,           -- JSON array: ["Acquisition", "Refi", "Construction"]
    avoid_titles TEXT,                  -- JSON array
    avoid_company_types TEXT,           -- JSON array
    
    -- Scoring Weights (0-100, how much each matters)
    weight_title_match INTEGER DEFAULT 30,
    weight_company_match INTEGER DEFAULT 25,
    weight_deal_size_match INTEGER DEFAULT 20,
    weight_geography_match INTEGER DEFAULT 15,
    weight_timing INTEGER DEFAULT 10,
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- PROOF POINTS: User's track record for credibility
CREATE TABLE IF NOT EXISTS proof_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    
    -- Metrics
    deals_closed_12mo INTEGER,
    total_volume_12mo REAL,             -- In millions
    avg_close_days INTEGER,
    approval_rate REAL,                 -- Percentage
    
    -- Notable Wins (JSON array of objects)
    notable_deals TEXT,                 -- [{amount, type, timeline, client_type, highlight}]
    
    -- Testimonials / Social Proof
    testimonials TEXT,                  -- JSON array
    awards TEXT,                        -- JSON array
    certifications TEXT,                -- JSON array
    
    -- Lender/Partner Relationships
    lender_relationships TEXT,          -- JSON array: ["Bank A", "Credit Union B"]
    exclusive_programs TEXT,            -- JSON array
    
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user_profile(user_id)
);

-- CONTACT MATCH DATA: Store match analysis per contact
CREATE TABLE IF NOT EXISTS contact_match (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    user_id TEXT NOT NULL DEFAULT 'default',
    
    -- Match Scores
    match_score REAL,
    fit_score REAL,
    relevance_score REAL,
    timing_score REAL,
    match_tier TEXT,                    -- 'HIGH', 'MEDIUM', 'LOW'
    
    -- Why Me Content (AI-generated)
    hook TEXT,
    proof_points_matched TEXT,          -- JSON array
    why_now TEXT,
    suggested_opening TEXT,
    talking_points TEXT,                -- JSON array
    objection_handlers TEXT,            -- JSON array
    
    -- Match Details
    matched_pain_points TEXT,           -- JSON: which pains match user's solutions
    matched_triggers TEXT,              -- JSON: timing triggers detected
    connection_angles TEXT,             -- JSON: personal connection opportunities
    
    generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    UNIQUE(contact_id, user_id)
);

-- COLD CALL QUEUE: Minimal data contacts for quick outreach
CREATE TABLE IF NOT EXISTS cold_call_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    
    -- Minimal Contact Info
    name TEXT NOT NULL,
    phone TEXT,
    mobile TEXT,
    email TEXT,
    linkedin_url TEXT,
    company TEXT,
    title TEXT,
    
    -- Source & Context
    source TEXT,                        -- 'linkedin', 'referral', 'list', 'event', 'manual'
    source_context TEXT,                -- e.g., "Met at ICSC conference"
    notes TEXT,
    
    -- Quick Scoring (before enrichment)
    quick_fit_score REAL,               -- Based on title/company alone
    quick_fit_reason TEXT,
    priority INTEGER DEFAULT 0,         -- 1=high, 2=medium, 3=low
    
    -- Status Tracking
    status TEXT DEFAULT 'new',          -- 'new', 'attempted', 'connected', 'meeting_set', 'not_interested', 'enriched'
    attempts INTEGER DEFAULT 0,
    last_attempt TEXT,
    outcome TEXT,
    
    -- Link to full contact (after enrichment)
    contact_id INTEGER,                 -- Links to contacts table once promoted
    
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES user_profile(user_id)
);

-- Add match columns to contacts if not exist
-- (Run these separately if needed)
