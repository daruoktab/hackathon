-- ========================================
-- Premium Feature Schema for Supabase
-- ========================================
-- This schema adds premium user management tables
-- Run this AFTER create_schema.sql in Supabase SQL Editor

-- ========================================
-- Drop existing premium tables (for clean migration)
-- ========================================
DROP TABLE IF EXISTS premium_data CASCADE;
DROP TABLE IF EXISTS token CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

-- ========================================
-- Table 1: User (Main user profile with premium status)
-- ========================================
CREATE TABLE "user" (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,  -- Telegram ID or platform user ID
    status_account VARCHAR(20) NOT NULL DEFAULT 'Free' CHECK (status_account IN ('Free', 'Premium')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add comments
COMMENT ON TABLE "user" IS 'User profiles with premium account status';
COMMENT ON COLUMN "user".user_id IS 'Unique user ID from platform (e.g., Telegram ID)';
COMMENT ON COLUMN "user".status_account IS 'Account status: Free or Premium';

-- ========================================
-- Table 2: Premium Data (Premium subscription details)
-- ========================================
CREATE TABLE premium_data (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    premium_for VARCHAR(50) NOT NULL CHECK (premium_for IN ('payment', 'claim token')),
    expired_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES "user"(id)
        ON DELETE CASCADE
);

-- Add comments
COMMENT ON TABLE premium_data IS 'Premium subscription details for users';
COMMENT ON COLUMN premium_data.user_id IS 'Foreign key to user table';
COMMENT ON COLUMN premium_data.premium_for IS 'How premium was obtained: payment or claim token';
COMMENT ON COLUMN premium_data.expired_at IS 'When the premium subscription expires';

-- ========================================
-- Table 3: Token (JWT tokens for premium claims)
-- ========================================
CREATE TABLE token (
    token TEXT PRIMARY KEY,  -- JWT string
    is_used BOOLEAN NOT NULL DEFAULT FALSE
);

-- Add comments
COMMENT ON TABLE token IS 'JWT tokens for claiming premium access';
COMMENT ON COLUMN token.token IS 'JWT token string (used as primary key)';
COMMENT ON COLUMN token.is_used IS 'Whether this token has been claimed';

-- ========================================
-- Indexes for Performance
-- ========================================

-- User indexes
CREATE INDEX idx_user_user_id ON "user"(user_id);
CREATE INDEX idx_user_status ON "user"(status_account);

-- Premium data indexes
CREATE INDEX idx_premium_data_user_id ON premium_data(user_id);
CREATE INDEX idx_premium_data_expired_at ON premium_data(expired_at);

-- Token indexes
CREATE INDEX idx_token_is_used ON token(is_used);

-- ========================================
-- Triggers for Auto-updating Timestamps
-- ========================================

-- Apply trigger to premium_data
CREATE TRIGGER update_premium_data_updated_at
    BEFORE UPDATE ON premium_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- Useful Functions for Premium Management
-- ========================================

-- Function: Check if user is premium and not expired
CREATE OR REPLACE FUNCTION is_user_premium(p_user_id VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    user_status VARCHAR(20);
    expiry_date TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get user status
    SELECT status_account INTO user_status
    FROM "user"
    WHERE user_id = p_user_id;
    
    -- If user doesn't exist or is Free, return false
    IF user_status IS NULL OR user_status = 'Free' THEN
        RETURN FALSE;
    END IF;
    
    -- Check expiry date
    SELECT expired_at INTO expiry_date
    FROM premium_data pd
    JOIN "user" u ON pd.user_id = u.id
    WHERE u.user_id = p_user_id;
    
    -- If expired, auto-downgrade to Free
    IF expiry_date IS NOT NULL AND NOW() > expiry_date THEN
        UPDATE "user" SET status_account = 'Free'
        WHERE user_id = p_user_id;
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION is_user_premium IS 'Check if user has active premium subscription';

-- Function: Activate or extend premium
CREATE OR REPLACE FUNCTION activate_premium(
    p_user_id VARCHAR,
    p_method VARCHAR,
    p_duration INTERVAL
)
RETURNS VOID AS $$
DECLARE
    v_internal_user_id BIGINT;
    v_new_expiry TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get internal user ID
    SELECT id INTO v_internal_user_id
    FROM "user"
    WHERE user_id = p_user_id;
    
    IF v_internal_user_id IS NULL THEN
        RAISE EXCEPTION 'User not found: %', p_user_id;
    END IF;
    
    -- Calculate new expiry date
    v_new_expiry := NOW() + p_duration;
    
    -- Upsert premium_data
    INSERT INTO premium_data (user_id, premium_for, expired_at, updated_at)
    VALUES (v_internal_user_id, p_method, v_new_expiry, NOW())
    ON CONFLICT (user_id) DO UPDATE
    SET premium_for = EXCLUDED.premium_for,
        expired_at = EXCLUDED.expired_at,
        updated_at = NOW();
    
    -- Update user status to Premium
    UPDATE "user"
    SET status_account = 'Premium'
    WHERE id = v_internal_user_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION activate_premium IS 'Activate or extend premium subscription for a user';

-- ========================================
-- Grant Permissions
-- ========================================
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- ========================================
-- Success Message
-- ========================================
DO $$
BEGIN
    RAISE NOTICE '✅ Premium feature schema created successfully!';
    RAISE NOTICE '📊 Tables: user, premium_data, token';
    RAISE NOTICE '🔧 Functions: is_user_premium, activate_premium';
    RAISE NOTICE '⚡ Ready for premium feature implementation!';
END $$;
