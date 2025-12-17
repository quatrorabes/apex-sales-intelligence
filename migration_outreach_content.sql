#!/usr/bin/env python3

-- ============================================================================
-- APEX SALES INTELLIGENCE - OUTREACH CONTENT SCHEMA
-- December 15, 2025 - 10:55 PM PST
-- ============================================================================

-- Outreach Content Storage (Emails + Call Scripts + LinkedIn)
CREATE TABLE IF NOT EXISTS outreach_content (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
	
	-- Email Sequence (3 emails)
	email_1_subject TEXT,
	email_1_body TEXT,
	email_2_subject TEXT,
	email_2_body TEXT,
	email_3_subject TEXT,
	email_3_body TEXT,
	
	-- Call Scripts (3 variants)
	call_script_1 TEXT,
	call_script_2 TEXT,
	call_script_3 TEXT,
	
	-- LinkedIn Outreach
	linkedin_connection_note TEXT,
	linkedin_followup_message TEXT,
	
	-- Metadata
	generated_at TIMESTAMPTZ DEFAULT NOW(),
	updated_at TIMESTAMPTZ DEFAULT NOW(),
	
	-- Ensure one content package per contact
	UNIQUE(contact_id)
);

-- LinkedIn Prospects Management
CREATE TABLE IF NOT EXISTS linkedin_prospects (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	contact_id UUID REFERENCES contacts(id) ON DELETE CASCADE,
	linkedin_url TEXT UNIQUE NOT NULL,
	profile_name TEXT,
	headline TEXT,
	company TEXT,
	connection_status TEXT DEFAULT 'not_connected',
	connection_request_sent TIMESTAMPTZ,
	connection_accepted TIMESTAMPTZ,
	last_message_sent TIMESTAMPTZ,
	last_engaged TIMESTAMPTZ,
	engagement_score INTEGER DEFAULT 0,
	notes TEXT,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- LinkedIn Activity Tracking
CREATE TABLE IF NOT EXISTS linkedin_activities (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	prospect_id UUID REFERENCES linkedin_prospects(id) ON DELETE CASCADE,
	activity_type TEXT NOT NULL,
	activity_data JSONB,
	performed_at TIMESTAMPTZ DEFAULT NOW(),
	result TEXT
);

-- LinkedIn Message Templates
CREATE TABLE IF NOT EXISTS linkedin_message_templates (
	id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
	template_name TEXT UNIQUE NOT NULL,
	template_type TEXT NOT NULL,
	subject TEXT,
	message_body TEXT NOT NULL,
	variables JSONB,
	performance_score REAL DEFAULT 0.0,
	uses_count INTEGER DEFAULT 0,
	created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_outreach_contact ON outreach_content(contact_id);
CREATE INDEX IF NOT EXISTS idx_linkedin_contact ON linkedin_prospects(contact_id);
CREATE INDEX IF NOT EXISTS idx_linkedin_status ON linkedin_prospects(connection_status);
CREATE INDEX IF NOT EXISTS idx_linkedin_activities_prospect ON linkedin_activities(prospect_id);
CREATE INDEX IF NOT EXISTS idx_linkedin_activities_date ON linkedin_activities(performed_at);

-- Insert Default LinkedIn Templates
INSERT INTO linkedin_message_templates (template_name, template_type, message_body, variables)
VALUES 
	('connection_request_1', 'connection_request', 
	'Hi {firstname}, I noticed we''re both in {industry}. I''d love to connect and potentially explore synergies between our work. Looking forward to connecting!',
	'{"firstname": "", "industry": ""}'::jsonb),

	('connection_request_2', 'connection_request',
	'Hi {firstname}, Really impressed by your work at {company}. Would love to connect and learn more about what you''re building. Best regards!',
	'{"firstname": "", "company": ""}'::jsonb),

	('follow_up_1', 'follow_up',
	'Hi {firstname},\n\nHope you''re doing well! I''ve been following {company}''s recent growth and wanted to reach out.\n\nI work with similar companies in {industry} helping them {value_prop}. Would you be open to a quick 15-min call to explore if there''s mutual value?\n\nBest,\n{sender_name}',
	'{"firstname": "", "company": "", "industry": "", "value_prop": "", "sender_name": ""}'::jsonb),

	('value_add_1', 'value_add',
	'Hi {firstname},\n\nSaw your recent post about {topic} and thought you might find this interesting:\n\n{insight_or_resource}\n\nWould love to hear your thoughts!\n\nBest,\n{sender_name}',
	'{"firstname": "", "topic": "", "insight_or_resource": "", "sender_name": ""}'::jsonb)
ON CONFLICT (template_name) DO NOTHING;

COMMENT ON TABLE outreach_content IS 'Stores generated outreach content (emails, call scripts, LinkedIn messages)';
COMMENT ON TABLE linkedin_prospects IS 'LinkedIn-specific prospect tracking with connection status';
COMMENT ON TABLE linkedin_activities IS 'Activity log for LinkedIn outreach automation';
COMMENT ON TABLE linkedin_message_templates IS 'Reusable message templates with performance tracking';
