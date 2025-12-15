CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE scoring_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    contact_id INTEGER,
    original_score REAL,
    user_rating INTEGER,
    feedback_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE scoring_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            trigger TEXT NOT NULL,
            old_rss_score REAL,
            new_rss_score REAL,
            old_mdcp_score REAL,
            new_mdcp_score REAL,
            old_priority_score REAL,
            new_priority_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        );
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    user_email TEXT,
    user_phone TEXT,
    user_title TEXT,
    user_company TEXT,
    user_bio TEXT,
    user_style TEXT,
    user_value_props TEXT,
    user_industry_focus TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE company_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL UNIQUE,
    industry TEXT,
    size_range TEXT,
    location TEXT,
    key_products TEXT,
    target_market TEXT,
    pain_points TEXT,
    company_culture TEXT,
    recent_news TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE relationship_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    user_id INTEGER,
    relationship_level TEXT DEFAULT 'cold',
    years_known INTEGER DEFAULT 0,
    last_interaction TEXT,
    interaction_history TEXT,
    common_ground TEXT,
    referral_potential TEXT,
    personal_notes TEXT,
    professional_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (user_id) REFERENCES user_profiles(id)
);
CREATE TABLE generated_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    user_id INTEGER,
    channel TEXT,
    content_type TEXT,
    generated_content TEXT,
    ai_model TEXT,
    relationship_context TEXT,
    quality_score REAL,
    sent_status TEXT DEFAULT 'draft',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);
CREATE TABLE sales_nav_leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                linkedin_prospect_id INTEGER,
                sales_nav_lead_id TEXT UNIQUE,
                lead_data JSON,
                last_synced TEXT,
                notes TEXT,
                saved_to_list TEXT,
                FOREIGN KEY (contact_id) REFERENCES contacts(id),
                FOREIGN KEY (linkedin_prospect_id) REFERENCES linkedin_prospects(id)
            );
CREATE TABLE sales_nav_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                insight_type TEXT NOT NULL,
                insight_data JSON NOT NULL,
                discovered_at TEXT NOT NULL,
                relevance_score REAL,
                FOREIGN KEY (lead_id) REFERENCES sales_nav_leads(id)
            );
CREATE TABLE sales_nav_saved_searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_name TEXT UNIQUE NOT NULL,
                search_criteria JSON NOT NULL,
                auto_import INTEGER DEFAULT 0,
                last_run TEXT,
                total_results INTEGER DEFAULT 0
            );
CREATE TABLE linkedin_prospects (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				contact_id INTEGER,
				linkedin_url TEXT UNIQUE NOT NULL,
				profile_name TEXT,
				headline TEXT,
				company TEXT,
				connection_status TEXT DEFAULT 'not_connected',
				connection_request_sent TEXT,
				connection_accepted TEXT,
				last_message_sent TEXT,
				last_engaged TEXT,
				engagement_score INTEGER DEFAULT 0,
				notes TEXT,
				FOREIGN KEY (contact_id) REFERENCES contacts(id)
			);
CREATE TABLE linkedin_activities (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				prospect_id INTEGER NOT NULL,
				activity_type TEXT NOT NULL,
				activity_data TEXT,
				performed_at TEXT NOT NULL,
				result TEXT,
				FOREIGN KEY (prospect_id) REFERENCES linkedin_prospects(id)
			);
CREATE TABLE linkedin_message_templates (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				template_name TEXT UNIQUE NOT NULL,
				template_type TEXT NOT NULL,
				subject TEXT,
				message_body TEXT NOT NULL,
				variables TEXT,
				performance_score REAL DEFAULT 0.0,
				uses_count INTEGER DEFAULT 0
			);
CREATE TABLE user_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        
        -- Products/Services (JSON arrays)
        products TEXT,  
        services TEXT,
        value_propositions TEXT,
        target_customers TEXT,
        personal_differentiators TEXT,
        company_differentiators TEXT,
        
        -- Targeting preferences
        industry TEXT,
        target_verticals TEXT,
        ideal_titles TEXT,
        avoid_titles TEXT,
        min_company_size INTEGER DEFAULT 10,
        max_company_size INTEGER DEFAULT 5000,
        seniority_levels TEXT,
        exclude_c_suite INTEGER DEFAULT 0,
        
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE contact_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    activity_date TEXT NOT NULL,
    direction TEXT,
    subject TEXT,
    notes TEXT,
    outcome TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);
CREATE TABLE opportunity_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    signal_type TEXT NOT NULL,
    signal_date TEXT NOT NULL,
    signal_data TEXT,
    urgency_boost INTEGER DEFAULT 0,
    viewed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);
CREATE INDEX idx_activities_contact ON contact_activities(contact_id);
CREATE INDEX idx_activities_date ON contact_activities(activity_date);
CREATE INDEX idx_signals_contact ON opportunity_signals(contact_id);
CREATE INDEX idx_signals_viewed ON opportunity_signals(viewed);
CREATE TABLE contacts (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT,
	email TEXT,
	phone TEXT,
	company TEXT,
	job_title TEXT,
	linkedin_url TEXT,
	
	-- AI Scoring
	ai_prospect_score REAL,
	ai_confidence TEXT,
	prospect_score REAL,
	lead_score REAL,
	composite_score REAL,
	vip_intelligence_score REAL,
	
	-- Persona Fields
	borrower_persona_type TEXT,
	relationship_persona_type TEXT,
	persona TEXT,
	primary_persona_tier TEXT,
	persona_confidence_score REAL,
	
	-- Sales Pipeline
	sales_stage TEXT,
	lead_status TEXT,
	lifecycle_stage TEXT,
	scoring_tier TEXT,
	lead_priority TEXT,
	
	-- Activity Tracking
	last_contact DATE,
	last_activity_type TEXT,
	total_touchpoints INTEGER,
	days_since_contact INTEGER,
	days_in_pipeline INTEGER,
	
	-- Enrichment
	enrichment_status TEXT,
	enrichment_level TEXT,
	last_enriched DATE,
	last_scored DATE,
	
	-- Timestamps
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
, hubspot_id TEXT, firstname TEXT, lastname TEXT, phone_mobile TEXT, title TEXT, import_source TEXT, last_crm_sync TEXT, enrichment_ready INTEGER DEFAULT 0, hs_object_id TEXT, profile_content TEXT, overview TEXT, background TEXT, recent_mentions TEXT, social_profiles TEXT, personality_detail TEXT, mb_summary TEXT, company_overview TEXT, company_products_services TEXT, company_leadership TEXT, company_market_competitors TEXT, company_recent_news TEXT, company_fun_facts TEXT, sales_talking_points TEXT, deals_history TEXT, fun_facts TEXT, pain_points TEXT, talking_points TEXT, recommended_action TEXT, rss_score REAL, rss_tier TEXT, mdcp_score REAL, mdcp_tier TEXT, priority_score REAL, urgency_level TEXT, persona_multiplier REAL DEFAULT 1.0, enrichment_data TEXT, calculation_version TEXT, lead_type TEXT, email_1_subject TEXT, email_1_body TEXT, call_script_1 TEXT, linkedin_connect TEXT, last_contact_date TEXT, enriched INTEGER DEFAULT 0, enriched_at TEXT, first_name TEXT, last_name TEXT, company_domain TEXT, company_website TEXT, company_hq_city TEXT, company_hq_state TEXT, industry TEXT, data_completeness_score INTEGER DEFAULT 0, crm_id TEXT, money_score REAL, decision_score REAL, champion_score REAL, pain_score REAL, next_action TEXT, next_action_date TEXT, cadence_stage TEXT, cadence_started TEXT, matched_products TEXT, match_score REAL, match_tier TEXT, fit_score REAL, relevance_score REAL, timing_score REAL, why_me_data TEXT, why_me_generated_at TEXT);
CREATE TABLE user_products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            keywords TEXT,
            pain_points TEXT,
            ideal_titles TEXT,
            ideal_industries TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
CREATE TABLE cadence_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stages TEXT,
            active INTEGER DEFAULT 1
        );
CREATE TABLE activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            action_type TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
CREATE TABLE user_profile (
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
CREATE TABLE proof_points (
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
CREATE TABLE contact_match (
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
CREATE TABLE cold_call_queue (
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
CREATE TABLE cadences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    steps TEXT NOT NULL,  -- JSON array of steps
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE cadence_enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    cadence_id INTEGER NOT NULL,
    current_step INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',  -- active, paused, completed, replied, booked
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    next_action_date DATE,
    completed_at TIMESTAMP,
    paused_at TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (contact_id) REFERENCES contacts(id),
    FOREIGN KEY (cadence_id) REFERENCES cadences(id),
    UNIQUE(contact_id, cadence_id)
);
CREATE TABLE cadence_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL,
    step_index INTEGER NOT NULL,
    channel TEXT NOT NULL,  -- email, call, linkedin
    action TEXT NOT NULL,   -- sent, called, connected, no_answer, left_vm, replied
    outcome TEXT,           -- positive, neutral, negative
    notes TEXT,
    content_used TEXT,      -- The actual content sent/used
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (enrollment_id) REFERENCES cadence_enrollments(id)
);
CREATE INDEX idx_enrollments_contact ON cadence_enrollments(contact_id);
CREATE INDEX idx_enrollments_status ON cadence_enrollments(status);
CREATE INDEX idx_enrollments_next_action ON cadence_enrollments(next_action_date);
CREATE INDEX idx_activities_enrollment ON cadence_activities(enrollment_id);
