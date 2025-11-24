-- Fix the whiteboard activity trigger for comments
-- The wbc table doesn't have wid, it has oid which references wbo
-- We need to look up the wid through the wbo table

-- Drop the old trigger
DROP TRIGGER IF EXISTS update_wb_activity_on_comment ON wbc;

-- Create a new function that handles comments correctly
CREATE OR REPLACE FUNCTION update_whiteboard_activity_on_comment()
RETURNS TRIGGER AS $$
BEGIN
    -- Get the whiteboard_id from the object
    UPDATE wb 
    SET laa = NOW() 
    WHERE id = (SELECT wid FROM wbo WHERE id = NEW.oid);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the new trigger
CREATE TRIGGER update_wb_activity_on_comment 
    AFTER INSERT OR UPDATE ON wbc
    FOR EACH ROW 
    EXECUTE FUNCTION update_whiteboard_activity_on_comment();
