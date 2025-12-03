-- Add new fields for personality assessments and social profiles
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS myers_briggs TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS disc_profile TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS strengthsfinder_themes TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS instagram_url TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS twitter_url TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS facebook_url TEXT;
ALTER TABLE contacts ADD COLUMN IF NOT EXISTS best_contact_channel TEXT;
