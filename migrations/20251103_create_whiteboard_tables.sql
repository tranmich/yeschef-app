-- =====================================================
-- WHITEBOARD SYSTEM - DATABASE MIGRATION
-- =====================================================
-- Date: November 3, 2025
-- Phase: 1 - Foundation
-- 
-- Features:
-- ✅ Compact naming (wid, hid, rid for performance)
-- ✅ Soft delete + 14-day expiry
-- ✅ Event log for major changes
-- ✅ Optimized JSONB with GIN indexes
-- ✅ Automatic timestamps with triggers
-- =====================================================

BEGIN;

-- =====================================================
-- TABLE 1: wb (whiteboards)
-- Stores whiteboard metadata and canvas settings
-- =====================================================

CREATE TABLE IF NOT EXISTS wb (
    id SERIAL PRIMARY KEY,
    hid INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    
    -- Metadata (compact names)
    n VARCHAR(255) NOT NULL,                    -- name
    d TEXT,                                     -- description
    tt VARCHAR(20) DEFAULT 'freeform',          -- template_type
    
    -- Canvas data (compact JSONB keys for performance)
    cs JSONB DEFAULT '{
        "vp": [0, 0, 1.0],
        "bg": "#ffffff",
        "gr": [true, 20, true]
    }'::jsonb,
    -- vp = viewport [x, y, zoom]
    -- bg = background color
    -- gr = grid [enabled, size, snap]
    
    -- Audit fields
    cby INTEGER NOT NULL REFERENCES users(id),  -- created_by
    ca TIMESTAMP DEFAULT NOW(),                 -- created_at
    ua TIMESTAMP DEFAULT NOW(),                 -- updated_at
    laa TIMESTAMP DEFAULT NOW(),                -- last_activity_at
    
    -- Soft delete (Option D - Enhanced)
    deleted_at TIMESTAMP,                       -- null = active, set = deleted
    deleted_by INTEGER REFERENCES users(id),    -- who deleted it
    
    -- Constraints
    CONSTRAINT wb_name_not_empty CHECK (LENGTH(TRIM(n)) > 0),
    CONSTRAINT wb_template_type_valid CHECK (tt IN ('freeform', 'weekly_planner', 'party_board', 'meal_prep'))
);

-- Indexes for performance
CREATE INDEX idx_wb_hid ON wb(hid) WHERE deleted_at IS NULL;
CREATE INDEX idx_wb_laa ON wb(laa DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_wb_deleted ON wb(deleted_at) WHERE deleted_at IS NOT NULL;
CREATE INDEX idx_wb_cs ON wb USING GIN(cs);

COMMENT ON TABLE wb IS 'Whiteboards - collaborative canvas for household meal planning';
COMMENT ON COLUMN wb.cs IS 'Canvas settings: viewport, background, grid (compact JSONB)';
COMMENT ON COLUMN wb.deleted_at IS 'Soft delete timestamp - 14 day retention for restore';

-- =====================================================
-- TABLE 2: wbo (whiteboard_objects)
-- Stores modular blocks with links to existing data
-- =====================================================

CREATE TABLE IF NOT EXISTS wbo (
    id SERIAL PRIMARY KEY,
    wid INTEGER NOT NULL REFERENCES wb(id) ON DELETE CASCADE,
    
    t VARCHAR(10) NOT NULL,                     -- type: 'rc', 'gl', 'mp', 'nt', 'im', 'cn', 'sc'
    
    -- Polymorphic references (links to existing data - NO duplication!)
    rid INTEGER REFERENCES recipes(id) ON DELETE SET NULL,              -- recipe_id
    gid INTEGER REFERENCES grocery_lists(id) ON DELETE SET NULL,        -- grocery_list_id
    mid INTEGER REFERENCES meal_plans(id) ON DELETE SET NULL,           -- meal_plan_id
    
    -- Visual properties (compact JSONB arrays for performance)
    p JSONB NOT NULL DEFAULT '[0,0,300,400,0]'::jsonb,  -- position [x,y,w,h,z]
    s JSONB DEFAULT '{"bg":"#fff","bc":"#e5e7eb","bw":1,"br":8}'::jsonb,
    -- s = style: bg=background, bc=borderColor, bw=borderWidth, br=borderRadius
    
    -- Organization (tags for filtering/grouping)
    tags TEXT[],                                -- ['weeknight', 'kids', 'party']
    
    -- Freeform content (for notes/images only - no external link)
    c JSONB DEFAULT '{}'::jsonb,                -- content
    
    -- Audit fields
    cby INTEGER NOT NULL REFERENCES users(id),
    ca TIMESTAMP DEFAULT NOW(),
    ua TIMESTAMP DEFAULT NOW(),
    
    -- Edit lock (for collaboration - prevents concurrent edits)
    lby INTEGER REFERENCES users(id),           -- locked_by
    lat TIMESTAMP,                              -- locked_at
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by INTEGER REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT wbo_valid_type CHECK (t IN ('rc','gl','mp','nt','im','cn','sc')),
    CONSTRAINT wbo_position_array CHECK (jsonb_array_length(p) = 5),
    CONSTRAINT wbo_one_reference CHECK (
        (rid IS NOT NULL)::int + 
        (gid IS NOT NULL)::int + 
        (mid IS NOT NULL)::int <= 1
    )
);

-- Indexes for performance
CREATE INDEX idx_wbo_wid ON wbo(wid) WHERE deleted_at IS NULL;
CREATE INDEX idx_wbo_rid ON wbo(rid) WHERE rid IS NOT NULL AND deleted_at IS NULL;
CREATE INDEX idx_wbo_gid ON wbo(gid) WHERE gid IS NOT NULL AND deleted_at IS NULL;
CREATE INDEX idx_wbo_mid ON wbo(mid) WHERE mid IS NOT NULL AND deleted_at IS NULL;
CREATE INDEX idx_wbo_t ON wbo(t) WHERE deleted_at IS NULL;
CREATE INDEX idx_wbo_p ON wbo USING GIN(p);
CREATE INDEX idx_wbo_tags ON wbo USING GIN(tags);
CREATE INDEX idx_wbo_deleted ON wbo(deleted_at) WHERE deleted_at IS NOT NULL;

COMMENT ON TABLE wbo IS 'Whiteboard objects - modular blocks linking to existing data';
COMMENT ON COLUMN wbo.p IS 'Position array: [x, y, width, height, z-index]';
COMMENT ON COLUMN wbo.tags IS 'Organization tags for filtering (e.g., weeknight, kids, party)';
COMMENT ON COLUMN wbo.rid IS 'Links to recipes table (no data duplication)';

-- =====================================================
-- TABLE 3: wbc (whiteboard_comments)
-- Threaded comments on whiteboard objects
-- =====================================================

CREATE TABLE IF NOT EXISTS wbc (
    id SERIAL PRIMARY KEY,
    oid INTEGER NOT NULL REFERENCES wbo(id) ON DELETE CASCADE,  -- object_id
    
    pid INTEGER REFERENCES wbc(id) ON DELETE CASCADE,           -- parent_id (threading)
    td INTEGER DEFAULT 0,                                       -- thread_depth
    
    uid INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    txt TEXT NOT NULL,                                          -- content
    
    -- Reactions (compact JSONB)
    rx JSONB DEFAULT '{}'::jsonb,  -- {"👍":[1,5,12],"❤️":[3,7]} (user_ids)
    
    -- Mentions (array)
    mu INTEGER[],  -- mentioned_users [2, 5, 11]
    
    -- Status
    rv BOOLEAN DEFAULT false,                                   -- is_resolved
    rby INTEGER REFERENCES users(id),                           -- resolved_by
    rat TIMESTAMP,                                              -- resolved_at
    
    ca TIMESTAMP DEFAULT NOW(),
    ua TIMESTAMP DEFAULT NOW(),
    
    -- Soft delete
    deleted_at TIMESTAMP,
    deleted_by INTEGER REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT wbc_content_not_empty CHECK (LENGTH(TRIM(txt)) > 0),
    CONSTRAINT wbc_thread_depth_valid CHECK (td >= 0 AND td <= 5)
);

-- Indexes
CREATE INDEX idx_wbc_oid ON wbc(oid) WHERE deleted_at IS NULL;
CREATE INDEX idx_wbc_uid ON wbc(uid);
CREATE INDEX idx_wbc_pid ON wbc(pid) WHERE pid IS NOT NULL;
CREATE INDEX idx_wbc_ca ON wbc(ca DESC);
CREATE INDEX idx_wbc_deleted ON wbc(deleted_at) WHERE deleted_at IS NOT NULL;

COMMENT ON TABLE wbc IS 'Comments on whiteboard objects with threading support';
COMMENT ON COLUMN wbc.rx IS 'Reactions: {"emoji": [user_id_array]}';
COMMENT ON COLUMN wbc.mu IS 'Mentioned user IDs for @mention notifications';

-- =====================================================
-- TABLE 4: wbco (whiteboard_collaborators)
-- User presence and roles on whiteboards
-- =====================================================

CREATE TABLE IF NOT EXISTS wbco (
    wid INTEGER NOT NULL REFERENCES wb(id) ON DELETE CASCADE,
    uid INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    rl VARCHAR(10) DEFAULT 'user',                              -- role ('admin','user')
    ia BOOLEAN DEFAULT false,                                   -- is_active
    lsa TIMESTAMP DEFAULT NOW(),                                -- last_seen_at
    
    -- Cursor position (for future real-time features)
    cp JSONB,  -- [x, y]
    
    -- Activity tracking
    coid INTEGER REFERENCES wbo(id),                            -- current_object_id
    ast VARCHAR(20),  -- activity_status ('viewing','editing','commenting')
    
    -- Cached user info (for quick display)
    un VARCHAR(255),                                            -- user_name
    ua JSONB,  -- user_avatar {bg, icon}
    
    ja TIMESTAMP DEFAULT NOW(),                                 -- joined_at
    ua_ts TIMESTAMP DEFAULT NOW(),                              -- updated_at (timestamp)
    
    PRIMARY KEY (wid, uid),
    CONSTRAINT wbco_valid_role CHECK (rl IN ('admin','user')),
    CONSTRAINT wbco_valid_status CHECK (ast IS NULL OR ast IN ('viewing','editing','commenting'))
);

-- Indexes
CREATE INDEX idx_wbco_wid ON wbco(wid);
CREATE INDEX idx_wbco_ia ON wbco(wid, ia) WHERE ia = true;
CREATE INDEX idx_wbco_lsa ON wbco(lsa DESC);

COMMENT ON TABLE wbco IS 'Whiteboard collaborators - presence and permissions';
COMMENT ON COLUMN wbco.rl IS 'Role: admin (can add/remove users), user (can edit)';
COMMENT ON COLUMN wbco.ia IS 'Is active on whiteboard right now';

-- =====================================================
-- TABLE 5: wbe (whiteboard_events)
-- Event log for major changes (Q3 requirement)
-- =====================================================

CREATE TABLE IF NOT EXISTS wbe (
    id SERIAL PRIMARY KEY,
    wid INTEGER NOT NULL REFERENCES wb(id) ON DELETE CASCADE,
    
    et VARCHAR(50) NOT NULL,                                    -- event_type
    uid INTEGER REFERENCES users(id),                           -- user_id (who did it)
    
    -- Event data (flexible JSONB)
    ed JSONB DEFAULT '{}'::jsonb,  -- event_data
    
    ca TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT wbe_valid_event_type CHECK (et IN (
        'whiteboard_created',
        'whiteboard_deleted',
        'whiteboard_restored',
        'user_added',
        'user_removed',
        'permission_changed',
        'object_created',
        'object_deleted',
        'recipe_added',
        'note_added',
        'comment_added'
    ))
);

-- Indexes
CREATE INDEX idx_wbe_wid ON wbe(wid);
CREATE INDEX idx_wbe_et ON wbe(et);
CREATE INDEX idx_wbe_ca ON wbe(ca DESC);
CREATE INDEX idx_wbe_ed ON wbe USING GIN(ed);

COMMENT ON TABLE wbe IS 'Event log for major whiteboard changes (audit trail)';
COMMENT ON COLUMN wbe.et IS 'Event type for filtering activity feed';
COMMENT ON COLUMN wbe.ed IS 'Event data: object_id, old/new values, etc.';

-- =====================================================
-- TRIGGERS: Auto-update timestamps
-- =====================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ua = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update last_activity_at on whiteboard
CREATE OR REPLACE FUNCTION update_whiteboard_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE wb SET laa = NOW() WHERE id = NEW.wid;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_wb_ua BEFORE UPDATE ON wb
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wbo_ua BEFORE UPDATE ON wbo
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wbc_ua BEFORE UPDATE ON wbc
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wb_activity_on_object AFTER INSERT OR UPDATE ON wbo
    FOR EACH ROW EXECUTE FUNCTION update_whiteboard_activity();

CREATE TRIGGER update_wb_activity_on_comment AFTER INSERT OR UPDATE ON wbc
    FOR EACH ROW EXECUTE FUNCTION update_whiteboard_activity();

-- =====================================================
-- FUNCTION: Log major events
-- =====================================================

CREATE OR REPLACE FUNCTION log_whiteboard_event(
    p_wid INTEGER,
    p_event_type VARCHAR(50),
    p_user_id INTEGER,
    p_event_data JSONB DEFAULT '{}'::jsonb
)
RETURNS void AS $$
BEGIN
    INSERT INTO wbe (wid, et, uid, ed, ca)
    VALUES (p_wid, p_event_type, p_user_id, p_event_data, NOW());
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION log_whiteboard_event IS 'Log major whiteboard events for activity feed';

-- =====================================================
-- FUNCTION: Schedule permanent deletion (14 days)
-- =====================================================

CREATE OR REPLACE FUNCTION schedule_permanent_delete()
RETURNS void AS $$
BEGIN
    -- Delete whiteboards older than 14 days in trash
    DELETE FROM wb 
    WHERE deleted_at IS NOT NULL 
      AND deleted_at < NOW() - INTERVAL '14 days';
      
    -- Delete objects older than 14 days in trash
    DELETE FROM wbo 
    WHERE deleted_at IS NOT NULL 
      AND deleted_at < NOW() - INTERVAL '14 days';
      
    -- Delete comments older than 14 days in trash
    DELETE FROM wbc 
    WHERE deleted_at IS NOT NULL 
      AND deleted_at < NOW() - INTERVAL '14 days';
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION schedule_permanent_delete IS 'Cleanup function: permanently delete items in trash >14 days';

-- =====================================================
-- SEED DATA: Create test whiteboard for user_id 11
-- =====================================================

-- Insert test whiteboard for tran.mich@gmail.com (user_id: 11)
-- Uses first available household for user 11, or creates in any household they're a member of
INSERT INTO wb (hid, n, d, cby, ca, ua, laa)
SELECT 
    id as household_id,
    'Test Whiteboard - Phase 1',
    'Foundation testing for modular block system',
    11,  -- tran.mich@gmail.com
    NOW(),
    NOW(),
    NOW()
FROM households
WHERE owner_user_id = 11 OR id IN (
    SELECT household_id FROM household_members WHERE user_id = 11
)
ORDER BY id
LIMIT 1
ON CONFLICT DO NOTHING;

-- Add creator as admin collaborator
INSERT INTO wbco (wid, uid, rl, un, ja)
SELECT 
    id,
    11,
    'admin',
    (SELECT name FROM users WHERE id = 11),
    NOW()
FROM wb 
WHERE n = 'Test Whiteboard - Phase 1'
ON CONFLICT (wid, uid) DO NOTHING;

-- Log creation event
SELECT log_whiteboard_event(
    (SELECT id FROM wb WHERE n = 'Test Whiteboard - Phase 1' LIMIT 1),
    'whiteboard_created',
    11,
    '{"template": "freeform", "phase": 1}'::jsonb
);

-- =====================================================
-- VERIFY MIGRATION
-- =====================================================

DO $$
DECLARE
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_name IN ('wb', 'wbo', 'wbc', 'wbco', 'wbe')
      AND table_schema = 'public';
    
    IF table_count = 5 THEN
        RAISE NOTICE '✅ Migration successful: All 5 tables created';
        RAISE NOTICE '   - wb (whiteboards)';
        RAISE NOTICE '   - wbo (whiteboard_objects)';
        RAISE NOTICE '   - wbc (whiteboard_comments)';
        RAISE NOTICE '   - wbco (whiteboard_collaborators)';
        RAISE NOTICE '   - wbe (whiteboard_events)';
    ELSE
        RAISE EXCEPTION '❌ Migration failed: Expected 5 tables, found %', table_count;
    END IF;
END $$;

COMMIT;

-- =====================================================
-- USAGE EXAMPLES
-- =====================================================

-- Example 1: Query active whiteboards for household
-- SELECT * FROM wb WHERE hid = 1 AND deleted_at IS NULL;

-- Example 2: Get whiteboard with objects (fetch actual data separately)
-- SELECT * FROM wbo WHERE wid = 1 AND deleted_at IS NULL;
-- Then fetch: GET /api/v2/recipes?ids=2577,2578

-- Example 3: Get trash items (for restore)
-- SELECT id, n, deleted_at, deleted_by, 
--        EXTRACT(DAY FROM NOW() - deleted_at) as days_in_trash
-- FROM wb 
-- WHERE hid = 1 AND deleted_at IS NOT NULL
-- ORDER BY deleted_at DESC;

-- Example 4: Get activity feed
-- SELECT * FROM wbe WHERE wid = 1 ORDER BY ca DESC LIMIT 20;

-- Example 5: Get active collaborators
-- SELECT * FROM wbco WHERE wid = 1 AND ia = true;
