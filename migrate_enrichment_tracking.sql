-- Add missing enrichment tracking columns

ALTER TABLE contacts ADD COLUMN enrichment_count INTEGER DEFAULT 0;
ALTER TABLE contacts ADD COLUMN last_enriched_at DATETIME;
ALTER TABLE contacts ADD COLUMN enrichment_history TEXT DEFAULT '[]';

-- Update existing enriched contacts
UPDATE contacts 
SET enrichment_count = 1,
    last_enriched_at = enrichment_date
WHERE enrichment_status = 'complete' AND enrichment_count IS NULL;

SELECT 'Migration complete. Added enrichment tracking columns.' AS result;
