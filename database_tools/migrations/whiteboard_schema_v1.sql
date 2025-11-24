-- =====================================================
-- WHITEBOARD FEATURE - DATABASE SCHEMA V1
-- =====================================================
-- Phase 1 Week 4: Core Tables and Relationships
-- Author: GitHub Copilot
-- Date: November 3, 2025
--
-- Creates 5 tables for whiteboard functionality:
-- 1. whiteboards - Main whiteboard metadata
-- 2. whiteboard_objects - Individual objects on whiteboard
-- 3. whiteboard_containers - Grouping containers
-- 4. whiteboard_container_objects - Objects within containers
-- 5. whiteboard_events - Activity/change log
-- =====================================================

-- Drop tables if they exist (for clean migration)
DROP TABLE IF EXISTS whiteboard_events CASCADE;
DROP TABLE IF EXISTS whiteboard_container_objects CASCADE;
DROP TABLE IF EXISTS whiteboard_containers CASCADE;
DROP TABLE IF EXISTS whiteboard_objects CASCADE;
DROP TABLE IF EXISTS whiteboards CASCADE;

-- =====================================================
-- TABLE 1: WHITEBOARDS
-- =====================================================
CREATE TABLE whiteboards (
    id SERIAL PRIMARY KEY,
    household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50) DEFAULT 'blank',
    
    -- Canvas settings
    canvas_width INTEGER DEFAULT 3000,
    canvas_height INTEGER DEFAULT 2000,
    zoom_level DECIMAL(3,2) DEFAULT 1.00,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- Metadata
    created_by INTEGER REFERENCES users(id),
    last_modified_by INTEGER REFERENCES users(id),
    
    -- Search optimization
    search_vector TSVECTOR
);

-- Indexes for whiteboards
CREATE INDEX IF NOT EXISTS idx_whiteboards_household ON whiteboards(household_id);
CREATE INDEX IF NOT EXISTS idx_whiteboards_created_by ON whiteboards(created_by);
CREATE INDEX IF NOT EXISTS idx_whiteboards_deleted_at ON whiteboards(deleted_at);
CREATE INDEX IF NOT EXISTS idx_whiteboards_updated_at ON whiteboards(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_whiteboards_search ON whiteboards USING GIN(search_vector);

-- =====================================================
-- TABLE 2: WHITEBOARD_OBJECTS
-- =====================================================
CREATE TABLE whiteboard_objects (
    id SERIAL PRIMARY KEY,
    whiteboard_id INTEGER NOT NULL REFERENCES whiteboards(id) ON DELETE CASCADE,
    
    -- Object type and source
    object_type VARCHAR(20) NOT NULL, -- 'rc' (recipe card), 'note', 'image', 'list', 'link'
    entity_type VARCHAR(20), -- 'recipe', 'grocery_list', 'meal_plan'
    entity_id INTEGER, -- ID of linked entity
    
    -- Position and size [x, y, width, height, z_index]
    position DECIMAL[] NOT NULL DEFAULT '{100, 100, 300, 400, 0}',
    
    -- Content (for notes, images, etc)
    content JSONB,
    
    -- Visual styling
    style JSONB DEFAULT '{"backgroundColor": "#ffffff", "borderColor": "#e5e7eb"}',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    
    -- Ownership
    created_by INTEGER REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT valid_object_type CHECK (object_type IN ('rc', 'note', 'image', 'list', 'link', 'container'))
);

-- Indexes for whiteboard_objects
CREATE INDEX IF NOT EXISTS idx_wbo_whiteboard ON whiteboard_objects(whiteboard_id);
CREATE INDEX IF NOT EXISTS idx_wbo_type ON whiteboard_objects(object_type);
CREATE INDEX IF NOT EXISTS idx_wbo_entity ON whiteboard_objects(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_wbo_deleted ON whiteboard_objects(deleted_at);
CREATE INDEX IF NOT EXISTS idx_wbo_position ON whiteboard_objects USING GIN(position);

-- =====================================================
-- TABLE 3: WHITEBOARD_CONTAINERS
-- =====================================================
CREATE TABLE whiteboard_containers (
    id SERIAL PRIMARY KEY,
    whiteboard_id INTEGER NOT NULL REFERENCES whiteboards(id) ON DELETE CASCADE,
    
    -- Container metadata
    name VARCHAR(255) NOT NULL,
    container_type VARCHAR(20) DEFAULT 'section', -- 'section', 'group', 'folder'
    
    -- Position and size
    position DECIMAL[] NOT NULL DEFAULT '{100, 100, 600, 400, 0}',
    
    -- Styling
    style JSONB DEFAULT '{"backgroundColor": "#f9fafb", "borderColor": "#d1d5db"}',
    
    -- Behavior
    is_collapsed BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    created_by INTEGER REFERENCES users(id)
);

-- Indexes for containers
CREATE INDEX IF NOT EXISTS idx_wbc_whiteboard ON whiteboard_containers(whiteboard_id);
CREATE INDEX IF NOT EXISTS idx_wbc_type ON whiteboard_containers(container_type);

-- =====================================================
-- TABLE 4: WHITEBOARD_CONTAINER_OBJECTS
-- =====================================================
CREATE TABLE whiteboard_container_objects (
    id SERIAL PRIMARY KEY,
    container_id INTEGER NOT NULL REFERENCES whiteboard_containers(id) ON DELETE CASCADE,
    object_id INTEGER NOT NULL REFERENCES whiteboard_objects(id) ON DELETE CASCADE,
    
    -- Position within container
    relative_position DECIMAL[] DEFAULT '{10, 10}',
    
    -- Order
    display_order INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate entries
    CONSTRAINT unique_container_object UNIQUE (container_id, object_id)
);

-- Indexes for container objects
CREATE INDEX IF NOT EXISTS idx_wbco_container ON whiteboard_container_objects(container_id);
CREATE INDEX IF NOT EXISTS idx_wbco_object ON whiteboard_container_objects(object_id);

-- =====================================================
-- TABLE 5: WHITEBOARD_EVENTS
-- =====================================================
CREATE TABLE whiteboard_events (
    id SERIAL PRIMARY KEY,
    whiteboard_id INTEGER NOT NULL REFERENCES whiteboards(id) ON DELETE CASCADE,
    
    -- Event details
    event_type VARCHAR(50) NOT NULL, -- 'created', 'object_added', 'object_moved', 'object_deleted', etc.
    event_data JSONB,
    
    -- User and timestamp
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Optional object reference
    object_id INTEGER REFERENCES whiteboard_objects(id) ON DELETE SET NULL
);

-- Indexes for events
CREATE INDEX IF NOT EXISTS idx_wbe_whiteboard ON whiteboard_events(whiteboard_id);
CREATE INDEX IF NOT EXISTS idx_wbe_created_at ON whiteboard_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_wbe_type ON whiteboard_events(event_type);
CREATE INDEX IF NOT EXISTS idx_wbe_user ON whiteboard_events(user_id);

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Trigger 1: Auto-update updated_at on whiteboards
CREATE OR REPLACE FUNCTION update_whiteboard_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_whiteboard_updated
    BEFORE UPDATE ON whiteboards
    FOR EACH ROW
    EXECUTE FUNCTION update_whiteboard_timestamp();

-- Trigger 2: Auto-update updated_at on whiteboard_objects
CREATE OR REPLACE FUNCTION update_object_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_object_updated
    BEFORE UPDATE ON whiteboard_objects
    FOR EACH ROW
    EXECUTE FUNCTION update_object_timestamp();

-- Trigger 3: Update whiteboard timestamp when objects change
CREATE OR REPLACE FUNCTION touch_whiteboard_on_object_change()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE whiteboards 
    SET updated_at = CURRENT_TIMESTAMP,
        last_modified_by = COALESCE(NEW.created_by, OLD.created_by)
    WHERE id = COALESCE(NEW.whiteboard_id, OLD.whiteboard_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_touch_whiteboard_on_insert
    AFTER INSERT ON whiteboard_objects
    FOR EACH ROW
    EXECUTE FUNCTION touch_whiteboard_on_object_change();

CREATE TRIGGER trigger_touch_whiteboard_on_update
    AFTER UPDATE ON whiteboard_objects
    FOR EACH ROW
    EXECUTE FUNCTION touch_whiteboard_on_object_change();

CREATE TRIGGER trigger_touch_whiteboard_on_delete
    AFTER DELETE ON whiteboard_objects
    FOR EACH ROW
    EXECUTE FUNCTION touch_whiteboard_on_object_change();

-- Trigger 4: Update search vector on whiteboard changes
CREATE OR REPLACE FUNCTION update_whiteboard_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector = 
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_whiteboard_search_vector
    BEFORE INSERT OR UPDATE ON whiteboards
    FOR EACH ROW
    EXECUTE FUNCTION update_whiteboard_search_vector();

-- Trigger 5: Log events automatically
CREATE OR REPLACE FUNCTION log_whiteboard_event()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO whiteboard_events (whiteboard_id, event_type, event_data, user_id)
        VALUES (NEW.id, 'whiteboard_created', jsonb_build_object('name', NEW.name), NEW.created_by);
    ELSIF TG_OP = 'UPDATE' AND NEW.deleted_at IS NOT NULL AND OLD.deleted_at IS NULL THEN
        INSERT INTO whiteboard_events (whiteboard_id, event_type, user_id)
        VALUES (NEW.id, 'whiteboard_deleted', NEW.last_modified_by);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_whiteboard_changes
    AFTER INSERT OR UPDATE ON whiteboards
    FOR EACH ROW
    EXECUTE FUNCTION log_whiteboard_event();

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function 1: Get whiteboard with object count
CREATE OR REPLACE FUNCTION get_whiteboard_summary(p_whiteboard_id INTEGER)
RETURNS TABLE (
    id INTEGER,
    name VARCHAR,
    description TEXT,
    object_count BIGINT,
    last_updated TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        w.id,
        w.name,
        w.description,
        COUNT(wo.id) as object_count,
        w.updated_at as last_updated
    FROM whiteboards w
    LEFT JOIN whiteboard_objects wo ON w.id = wo.whiteboard_id AND wo.deleted_at IS NULL
    WHERE w.id = p_whiteboard_id AND w.deleted_at IS NULL
    GROUP BY w.id, w.name, w.description, w.updated_at;
END;
$$ LANGUAGE plpgsql;

-- Function 2: Soft delete whiteboard
CREATE OR REPLACE FUNCTION soft_delete_whiteboard(p_whiteboard_id INTEGER, p_user_id INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE whiteboards 
    SET deleted_at = CURRENT_TIMESTAMP,
        last_modified_by = p_user_id
    WHERE id = p_whiteboard_id AND deleted_at IS NULL;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function 3: Restore deleted whiteboard
CREATE OR REPLACE FUNCTION restore_whiteboard(p_whiteboard_id INTEGER, p_user_id INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE whiteboards 
    SET deleted_at = NULL,
        last_modified_by = p_user_id
    WHERE id = p_whiteboard_id AND deleted_at IS NOT NULL;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Function 4: Get whiteboard activity
CREATE OR REPLACE FUNCTION get_whiteboard_activity(p_whiteboard_id INTEGER, p_limit INTEGER DEFAULT 20)
RETURNS TABLE (
    event_type VARCHAR,
    event_data JSONB,
    user_id INTEGER,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        we.event_type,
        we.event_data,
        we.user_id,
        we.created_at
    FROM whiteboard_events we
    WHERE we.whiteboard_id = p_whiteboard_id
    ORDER BY we.created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- GRANT PERMISSIONS (if using specific database users)
-- =====================================================

-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO your_app_user;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Verify tables created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_name LIKE 'whiteboard%'
ORDER BY table_name;

-- Verify indexes created
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
  AND tablename LIKE 'whiteboard%'
ORDER BY tablename, indexname;

-- Verify triggers created
SELECT trigger_name, event_object_table, action_statement
FROM information_schema.triggers
WHERE trigger_schema = 'public'
  AND event_object_table LIKE 'whiteboard%'
ORDER BY event_object_table, trigger_name;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- All whiteboard tables, indexes, triggers, and helper
-- functions have been created successfully!
-- =====================================================
