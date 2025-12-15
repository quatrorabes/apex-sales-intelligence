#!/usr/bin/env python3

-- ~/projects/apex/add_user_preferences.sql

CREATE TABLE IF NOT EXISTS user_preferences (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id TEXT UNIQUE NOT NULL,  -- Email or unique identifier
	scoring_profile TEXT DEFAULT 'DEFAULT',
	custom_ideal_titles TEXT,  -- JSON array of ideal titles
	custom_avoid_titles TEXT,  -- JSON array of titles to avoid
	ideal_company_size_min INTEGER,
	ideal_company_size_max INTEGER,
	ideal_industries TEXT,  -- JSON array
	ideal_revenue_min INTEGER,
	ideal_revenue_max INTEGER,
	target_seniority_levels TEXT,  -- JSON array: ["VP", "SVP", "Director"]
	exclude_c_suite BOOLEAN DEFAULT 0,
	custom_weights TEXT,  -- JSON object with weight overrides
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Store scoring history for learning
CREATE TABLE IF NOT EXISTS scoring_feedback (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id TEXT NOT NULL,
	contact_id INTEGER,
	original_score REAL,
	user_rating INTEGER,  -- 1-5 stars on how good the lead was
	feedback_notes TEXT,
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
