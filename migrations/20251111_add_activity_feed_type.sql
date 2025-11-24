-- =====================================================
-- ADD ACTIVITY FEED TYPE TO WHITEBOARD OBJECTS
-- =====================================================
-- Date: November 11, 2025
-- Purpose: Add 'af' (activity feed) as a valid type for whiteboard objects
-- =====================================================

BEGIN;

-- Drop the existing constraint
ALTER TABLE wbo DROP CONSTRAINT IF EXISTS wbo_valid_type;

-- Add the new constraint with 'af' included
ALTER TABLE wbo ADD CONSTRAINT wbo_valid_type 
    CHECK (t IN ('rc','gl','mp','nt','im','cn','sc','af'));

COMMIT;

-- Verify the change
DO $$
BEGIN
    RAISE NOTICE '✅ Migration successful: Activity feed type (af) added to wbo valid types';
    RAISE NOTICE '   Valid types: rc, gl, mp, nt, im, cn, sc, af';
END $$;
