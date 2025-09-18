-- Migration: create_friends_schema.sql
-- Create tables for Friends, Households, and Collaboration features
-- Created: September 17, 2025
-- Follows existing PostgreSQL patterns and user authentication system

-- Friendships table - handles friend relationships
CREATE TABLE IF NOT EXISTS friendships (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    friend_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_friendship UNIQUE(user_id, friend_id),
    CONSTRAINT no_self_friendship CHECK (user_id != friend_id),
    CONSTRAINT valid_status CHECK (status IN ('pending', 'accepted', 'blocked', 'declined'))
);

-- Friend requests table - tracks request messages and metadata
CREATE TABLE IF NOT EXISTS friend_requests (
    id SERIAL PRIMARY KEY,
    requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    responded_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT unique_request UNIQUE(requester_id, recipient_id),
    CONSTRAINT no_self_request CHECK (requester_id != recipient_id),
    CONSTRAINT valid_request_status CHECK (status IN ('pending', 'accepted', 'declined', 'cancelled'))
);

-- Households table - family/group collaboration spaces
CREATE TABLE IF NOT EXISTS households (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    owner_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    invite_code VARCHAR(32) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Household members table - who belongs to which households
CREATE TABLE IF NOT EXISTS household_members (
    id SERIAL PRIMARY KEY,
    household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    invited_by INTEGER REFERENCES users(id),
    
    -- Constraints
    CONSTRAINT unique_household_member UNIQUE(household_id, user_id),
    CONSTRAINT valid_role CHECK (role IN ('owner', 'admin', 'member'))
);

-- Shares table - controls what is shared with whom
CREATE TABLE IF NOT EXISTS shares (
    id SERIAL PRIMARY KEY,
    resource_type VARCHAR(50) NOT NULL,  -- 'meal_plan', 'grocery_list', 'recipe'
    resource_id INTEGER NOT NULL,        -- ID of the shared resource
    owner_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Sharing target (either friend or household)
    scope VARCHAR(20) NOT NULL,          -- 'friend', 'household', 'public'
    grantee_user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,  -- For friend shares
    household_id INTEGER REFERENCES households(id) ON DELETE CASCADE, -- For household shares
    
    -- Permissions
    permission VARCHAR(20) NOT NULL DEFAULT 'view', -- 'view', 'edit', 'admin'
    status VARCHAR(20) NOT NULL DEFAULT 'active',   -- 'active', 'revoked', 'expired'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_share_scope CHECK (scope IN ('friend', 'household', 'public')),
    CONSTRAINT valid_permission CHECK (permission IN ('view', 'edit', 'admin')),
    CONSTRAINT valid_share_status CHECK (status IN ('active', 'revoked', 'expired')),
    CONSTRAINT valid_share_target CHECK (
        (scope = 'friend' AND grantee_user_id IS NOT NULL AND household_id IS NULL) OR
        (scope = 'household' AND household_id IS NOT NULL AND grantee_user_id IS NULL) OR
        (scope = 'public' AND grantee_user_id IS NULL AND household_id IS NULL)
    )
);

-- Performance indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_friendships_user_id ON friendships(user_id);
CREATE INDEX IF NOT EXISTS idx_friendships_friend_id ON friendships(friend_id);
CREATE INDEX IF NOT EXISTS idx_friendships_status ON friendships(status);

CREATE INDEX IF NOT EXISTS idx_friend_requests_requester ON friend_requests(requester_id);
CREATE INDEX IF NOT EXISTS idx_friend_requests_recipient ON friend_requests(recipient_id);
CREATE INDEX IF NOT EXISTS idx_friend_requests_status ON friend_requests(status);

CREATE INDEX IF NOT EXISTS idx_household_members_household ON household_members(household_id);
CREATE INDEX IF NOT EXISTS idx_household_members_user ON household_members(user_id);

CREATE INDEX IF NOT EXISTS idx_shares_resource ON shares(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_shares_owner ON shares(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_shares_grantee ON shares(grantee_user_id);
CREATE INDEX IF NOT EXISTS idx_shares_household ON shares(household_id);
CREATE INDEX IF NOT EXISTS idx_shares_status ON shares(status);

-- Functions for friendship management
CREATE OR REPLACE FUNCTION create_mutual_friendship(user1_id INTEGER, user2_id INTEGER)
RETURNS VOID AS $$
BEGIN
    -- Create friendship from user1 to user2
    INSERT INTO friendships (user_id, friend_id, status) 
    VALUES (user1_id, user2_id, 'accepted')
    ON CONFLICT (user_id, friend_id) 
    DO UPDATE SET status = 'accepted', updated_at = CURRENT_TIMESTAMP;
    
    -- Create friendship from user2 to user1
    INSERT INTO friendships (user_id, friend_id, status) 
    VALUES (user2_id, user1_id, 'accepted')
    ON CONFLICT (user_id, friend_id) 
    DO UPDATE SET status = 'accepted', updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function to generate household invite codes
CREATE OR REPLACE FUNCTION generate_household_invite_code()
RETURNS TEXT AS $$
DECLARE
    code TEXT;
BEGIN
    code := upper(substring(md5(random()::text || clock_timestamp()::text) for 8));
    RETURN code;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate invite codes for households
CREATE OR REPLACE FUNCTION set_household_invite_code()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.invite_code IS NULL THEN
        NEW.invite_code := generate_household_invite_code();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_household_invite_code
    BEFORE INSERT ON households
    FOR EACH ROW
    EXECUTE FUNCTION set_household_invite_code();

-- Commit all changes
COMMIT;

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_app_user;