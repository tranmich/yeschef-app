-- 🍳 Community Recipe Sharing Migration
-- Adds community sharing support to existing recipes table
-- Date: September 18, 2025

-- Add community sharing columns to recipes table
ALTER TABLE recipes 
ADD COLUMN IF NOT EXISTS is_community_shared BOOLEAN DEFAULT FALSE;

ALTER TABLE recipes 
ADD COLUMN IF NOT EXISTS shared_at TIMESTAMP NULL;

ALTER TABLE recipes 
ADD COLUMN IF NOT EXISTS community_title TEXT NULL;

ALTER TABLE recipes 
ADD COLUMN IF NOT EXISTS community_description TEXT NULL;

ALTER TABLE recipes 
ADD COLUMN IF NOT EXISTS community_background TEXT DEFAULT 'default';

ALTER TABLE recipes 
ADD COLUMN IF NOT EXISTS community_icon TEXT DEFAULT '🍽️';

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_recipes_community_shared 
ON recipes (is_community_shared) WHERE is_community_shared = TRUE;

CREATE INDEX IF NOT EXISTS idx_recipes_shared_at 
ON recipes (shared_at) WHERE shared_at IS NOT NULL;

-- Simple view for community recipes (for easy querying)
CREATE OR REPLACE VIEW community_recipes AS
SELECT 
    id,
    title,
    COALESCE(community_title, title) as display_title,
    COALESCE(community_description, description) as display_description,
    ingredients,
    instructions,
    community_background,
    community_icon,
    shared_at,
    created_at
FROM recipes 
WHERE is_community_shared = TRUE
ORDER BY shared_at DESC;

-- Success message
SELECT 'Community sharing schema added successfully! 🎉' as status;