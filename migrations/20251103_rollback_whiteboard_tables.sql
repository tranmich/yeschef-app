-- =====================================================
-- WHITEBOARD SYSTEM - ROLLBACK MIGRATION
-- =====================================================
-- Date: November 3, 2025
-- Phase: 1 - Foundation
-- 
-- Purpose: Safely remove whiteboard tables and restore
--          database to pre-migration state
-- 
-- IMPORTANT: This will permanently delete all whiteboard data!
-- =====================================================

BEGIN;

-- =====================================================
-- SAFETY CHECK
-- =====================================================

DO $$
DECLARE
    wb_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO wb_count FROM wb WHERE deleted_at IS NULL;
    
    IF wb_count > 0 THEN
        RAISE WARNING '⚠️  Found % active whiteboards', wb_count;
        RAISE WARNING '⚠️  This rollback will PERMANENTLY delete all whiteboard data';
        RAISE WARNING '⚠️  Press Ctrl+C to cancel, or wait 5 seconds to continue...';
        
        -- 5 second delay
        PERFORM pg_sleep(5);
    END IF;
END $$;

-- =====================================================
-- DROP FUNCTIONS
-- =====================================================

DROP FUNCTION IF EXISTS schedule_permanent_delete();
DROP FUNCTION IF EXISTS log_whiteboard_event(INTEGER, VARCHAR, INTEGER, JSONB);
DROP FUNCTION IF EXISTS update_whiteboard_activity();
DROP FUNCTION IF EXISTS update_updated_at_column();

RAISE NOTICE '✅ Dropped 4 functions';

-- =====================================================
-- DROP TABLES (in reverse dependency order)
-- =====================================================

DROP TABLE IF EXISTS wbe CASCADE;           -- whiteboard_events
RAISE NOTICE '✅ Dropped wbe (whiteboard_events)';

DROP TABLE IF EXISTS wbco CASCADE;          -- whiteboard_collaborators
RAISE NOTICE '✅ Dropped wbco (whiteboard_collaborators)';

DROP TABLE IF EXISTS wbc CASCADE;           -- whiteboard_comments
RAISE NOTICE '✅ Dropped wbc (whiteboard_comments)';

DROP TABLE IF EXISTS wbo CASCADE;           -- whiteboard_objects
RAISE NOTICE '✅ Dropped wbo (whiteboard_objects)';

DROP TABLE IF EXISTS wb CASCADE;            -- whiteboards
RAISE NOTICE '✅ Dropped wb (whiteboards)';

-- =====================================================
-- VERIFY ROLLBACK
-- =====================================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_name IN ('wb', 'wbo', 'wbc', 'wbco', 'wbe')
      AND table_schema = 'public';
    
    IF table_count = 0 THEN
        RAISE NOTICE '✅ Rollback successful: All whiteboard tables removed';
    ELSE
        RAISE EXCEPTION '❌ Rollback failed: Found % remaining tables', table_count;
    END IF;
END $$;

COMMIT;

RAISE NOTICE '';
RAISE NOTICE '====================================================';
RAISE NOTICE '✅ ROLLBACK COMPLETE';
RAISE NOTICE '====================================================';
RAISE NOTICE 'Database restored to pre-whiteboard state';
RAISE NOTICE 'All whiteboard data has been permanently deleted';
RAISE NOTICE '====================================================';
