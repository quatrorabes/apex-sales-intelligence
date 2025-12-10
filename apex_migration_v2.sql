#!/bin/bash

-- ============================================================================
-- APEX SALES INTELLIGENCE v2.0 - COMPLETE DATABASE MIGRATION
-- Integrates: APEX Scoring + SPICE Framework + BANT Framework
-- Multi-Vertical Support: SaaS, Insurance, Equipment Leasing
-- ============================================================================

BEGIN;

-- ============================================================================
-- PART 1: APEX SCORING COLUMNS
-- ============================================================================

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS apex_score INTEGER DEFAULT NULL CHECK (apex_score IS NULL OR (apex_score >= 0 AND apex_score <= 100));
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS mdcp_score INTEGER DEFAULT NULL CHECK (mdcp_score IS NULL OR (mdcp_score >= 0 AND mdcp_score <= 100));
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS rss_score INTEGER DEFAULT NULL CHECK (rss_score IS NULL OR (rss_score >= 0 AND rss_score <= 100));
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS readiness_score INTEGER DEFAULT 0 CHECK (readiness_score >= 0 AND readiness_score <= 100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS suitability_score INTEGER DEFAULT 0 CHECK (suitability_score >= 0 AND suitability_score <= 100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS seniority_score INTEGER DEFAULT 0 CHECK (seniority_score >= 0 AND seniority_score <= 100);

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS persona_type VARCHAR(50) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS persona_confidence DECIMAL(3,2) DEFAULT NULL CHECK (persona_confidence IS NULL OR (persona_confidence >= 0 AND persona_confidence <= 1));

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS match_tier VARCHAR(20) DEFAULT NULL CHECK (match_tier IS NULL OR match_tier IN ('HIGH', 'MEDIUM', 'LOW', 'UNQUALIFIED'));
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS icp_match_percentage INTEGER DEFAULT NULL CHECK (icp_match_percentage IS NULL OR (icp_match_percentage >= 0 AND icp_match_percentage <= 100));
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS icp_criteria JSONB DEFAULT NULL;

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS urgency_level VARCHAR(20) DEFAULT NULL CHECK (urgency_level IS NULL OR urgency_level IN ('HIGH', 'MEDIUM', 'LOW'));
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS intent_score INTEGER DEFAULT 0 CHECK (intent_score >= 0 AND intent_score <= 100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS last_intent_signal TIMESTAMP DEFAULT NULL;

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS cadence_status VARCHAR(20) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS cadence_name VARCHAR(100) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS cadence_step INTEGER DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS cadence_total_steps INTEGER DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS cadence_enrolled_at TIMESTAMP DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS next_cadence_action TIMESTAMP DEFAULT NULL;

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS total_touchpoints INTEGER DEFAULT 0;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS last_touchpoint_date TIMESTAMP DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS response_rate DECIMAL(5,2) DEFAULT 0.00;

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS vertical VARCHAR(50) DEFAULT 'SaaS';
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS vertical_metadata JSONB DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS vertical_fit_score INTEGER DEFAULT NULL;

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS estimated_deal_size DECIMAL(12,2) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS expected_close_date DATE DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS qualified_at TIMESTAMP DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS opportunity_created_at TIMESTAMP DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS deal_closed_at TIMESTAMP DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS deal_outcome VARCHAR(20) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS loss_reason TEXT DEFAULT NULL;

-- ============================================================================
-- PART 2: BANT FRAMEWORK COLUMNS
-- ============================================================================

-- Budget (B)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_budget_confirmed BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_budget_range VARCHAR(50) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_budget_score INTEGER DEFAULT 0 CHECK (bant_budget_score >= 0 AND bant_budget_score <= 25);

-- Authority (A)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_authority_level VARCHAR(50) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_decision_maker_identified BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_authority_score INTEGER DEFAULT 0 CHECK (bant_authority_score >= 0 AND bant_authority_score <= 25);

-- Need (N)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_need_identified BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_pain_severity VARCHAR(20) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_current_solution VARCHAR(255) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_need_score INTEGER DEFAULT 0 CHECK (bant_need_score >= 0 AND bant_need_score <= 25);

-- Timeline (T)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_timeline_identified BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_target_close_date DATE DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_urgency VARCHAR(20) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_timeline_score INTEGER DEFAULT 0 CHECK (bant_timeline_score >= 0 AND bant_timeline_score <= 25);

-- BANT Composite
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_total_score INTEGER DEFAULT 0 CHECK (bant_total_score >= 0 AND bant_total_score <= 100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS bant_qualification_status VARCHAR(20) DEFAULT 'UNQUALIFIED';

-- ============================================================================
-- PART 3: SPICE FRAMEWORK COLUMNS
-- ============================================================================

-- Situation (S)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_situation_documented BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_situation_summary TEXT DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_org_structure_known BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_situation_score INTEGER DEFAULT 0 CHECK (spice_situation_score >= 0 AND spice_situation_score <= 20);

-- Problem (P)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_problem_identified BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_problem_description TEXT DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_problem_owner_known BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_problem_score INTEGER DEFAULT 0 CHECK (spice_problem_score >= 0 AND spice_problem_score <= 20);

-- Implication (I)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_implication_quantified BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_business_impact TEXT DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_cost_of_inaction DECIMAL(12,2) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_revenue_opportunity DECIMAL(12,2) DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_implication_score INTEGER DEFAULT 0 CHECK (spice_implication_score >= 0 AND spice_implication_score <= 20);

-- Critical Event (C)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_critical_event_identified BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_critical_event_description TEXT DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_critical_event_date DATE DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_event_driving_urgency BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_critical_event_score INTEGER DEFAULT 0 CHECK (spice_critical_event_score >= 0 AND spice_critical_event_score <= 20);

-- Decision (D)
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_decision_process_known BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_decision_criteria JSONB DEFAULT NULL;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_stakeholders_mapped BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_decision_timeline_confirmed BOOLEAN DEFAULT FALSE;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_decision_score INTEGER DEFAULT 0 CHECK (spice_decision_score >= 0 AND spice_decision_score <= 20);

-- SPICE Composite
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_total_score INTEGER DEFAULT 0 CHECK (spice_total_score >= 0 AND spice_total_score <= 100);
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS spice_qualification_status VARCHAR(20) DEFAULT 'EXPLORATORY';

-- ============================================================================
-- PART 4: UNIFIED QUALIFICATION
-- ============================================================================

ALTER TABLE contacts ADD COLUMN IF NOT EXISTS unified_qualification_score INTEGER DEFAULT 0;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS primary_qualification_framework VARCHAR(10) DEFAULT 'APEX';
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS qualification_last_updated TIMESTAMP DEFAULT NOW();

-- ============================================================================
-- PART 5: PERFORMANCE INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_contacts_apex_score ON contacts(apex_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_contacts_mdcp_score ON contacts(mdcp_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_contacts_rss_score ON contacts(rss_score DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_contacts_persona_type ON contacts(persona_type) WHERE persona_type IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contacts_match_tier ON contacts(match_tier) WHERE match_tier IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contacts_urgency_level ON contacts(urgency_level) WHERE urgency_level IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_contacts_cadence_status ON contacts(cadence_status) WHERE cadence_status = 'active';
CREATE INDEX IF NOT EXISTS idx_contacts_vertical ON contacts(vertical);

CREATE INDEX IF NOT EXISTS idx_contacts_bant_total_score ON contacts(bant_total_score DESC) WHERE bant_total_score > 0;
CREATE INDEX IF NOT EXISTS idx_contacts_bant_status ON contacts(bant_qualification_status);
CREATE INDEX IF NOT EXISTS idx_contacts_spice_total_score ON contacts(spice_total_score DESC) WHERE spice_total_score > 0;
CREATE INDEX IF NOT EXISTS idx_contacts_spice_status ON contacts(spice_qualification_status);
CREATE INDEX IF NOT EXISTS idx_contacts_unified_score ON contacts(unified_qualification_score DESC) WHERE unified_qualification_score > 0;

CREATE INDEX IF NOT EXISTS idx_contacts_priority_dashboard ON contacts(
	COALESCE(apex_score, priority_score, 0) DESC,
	urgency_level,
	enrichment_status
);

CREATE INDEX IF NOT EXISTS idx_contacts_qualification_report ON contacts(
	unified_qualification_score DESC,
	bant_total_score DESC,
	spice_total_score DESC,
	apex_score DESC
) WHERE unified_qualification_score > 0;

COMMIT;

-- ============================================================================
-- VERIFICATION REPORT
-- ============================================================================

DO $$
DECLARE
apex_cols INTEGER;
bant_cols INTEGER;
spice_cols INTEGER;
total_contacts INTEGER;
enriched_contacts INTEGER;
BEGIN
SELECT COUNT(*) INTO apex_cols FROM information_schema.columns 
WHERE table_name = 'contacts' AND column_name IN ('apex_score', 'mdcp_score', 'rss_score');

SELECT COUNT(*) INTO bant_cols FROM information_schema.columns 
WHERE table_name = 'contacts' AND column_name LIKE 'bant_%';

SELECT COUNT(*) INTO spice_cols FROM information_schema.columns 
WHERE table_name = 'contacts' AND column_name LIKE 'spice_%';

SELECT COUNT(*) INTO total_contacts FROM contacts;
SELECT COUNT(*) INTO enriched_contacts FROM contacts WHERE enrichment_status = 'completed';

RAISE NOTICE '╔════════════════════════════════════════════════════════════╗';
RAISE NOTICE '║   APEX SALES INTELLIGENCE v2.0 - MIGRATION COMPLETE       ║';
RAISE NOTICE '╠════════════════════════════════════════════════════════════╣';
RAISE NOTICE '║ APEX Columns Added:    % / 3                              ║', apex_cols;
RAISE NOTICE '║ BANT Columns Added:    % / 16                             ║', bant_cols;
RAISE NOTICE '║ SPICE Columns Added:   % / 21                             ║', spice_cols;
RAISE NOTICE '║                                                            ║';
RAISE NOTICE '║ Total Contacts:        %                                  ║', total_contacts;
RAISE NOTICE '║ Enriched Contacts:     %                                  ║', enriched_contacts;
RAISE NOTICE '║                                                            ║';
RAISE NOTICE '║ ✅ Database ready for multi-framework qualification       ║';
RAISE NOTICE '╚════════════════════════════════════════════════════════════╝';
END $$;
