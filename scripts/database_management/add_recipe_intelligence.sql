-- Migration: add_recipe_intelligence.sql
-- Enhance existing recipes table with intelligence fields (preserve all current data)
-- Created: August 17, 2025

-- Add intelligence fields to existing recipes table
ALTER TABLE recipes 
ADD COLUMN IF NOT EXISTS meal_role TEXT,
ADD COLUMN IF NOT EXISTS meal_role_confidence INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS time_min INTEGER,
ADD COLUMN IF NOT EXISTS steps_count INTEGER,
ADD COLUMN IF NOT EXISTS pots_pans_count INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS is_easy BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_one_pot BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS leftover_friendly BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS kid_friendly BOOLEAN DEFAULT FALSE;

-- Performance index for intelligent filtering
CREATE INDEX IF NOT EXISTS idx_recipes_intelligence 
ON recipes(meal_role, is_easy, is_one_pot, time_min);

-- Index for pantry-first searches (future enhancement)
CREATE INDEX IF NOT EXISTS idx_recipes_time_difficulty 
ON recipes(time_min, is_easy) WHERE time_min IS NOT NULL;

-- Commit changes
COMMIT;
