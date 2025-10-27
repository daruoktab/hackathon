-- ========================================
-- Supabase PostgreSQL Schema for Invoice RAG
-- ========================================
-- This schema migrates from SQLite to PostgreSQL
-- Run this in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search optimization

-- ========================================
-- Drop existing tables (for clean migration)
-- ========================================
DROP TABLE IF EXISTS spending_limits_v2 CASCADE;
DROP TABLE IF EXISTS spending_limits CASCADE;
DROP TABLE IF EXISTS invoice_items CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS platform_users CASCADE;

-- ========================================
-- Table 1: Invoices (Main transaction records)
-- ========================================
CREATE TABLE invoices (
    id BIGSERIAL PRIMARY KEY,
    shop_name VARCHAR(255) NOT NULL,
    invoice_date DATE,
    total_amount NUMERIC(15, 2) NOT NULL CHECK (total_amount >= 0),
    transaction_type VARCHAR(50),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    image_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE invoices IS 'Main invoice/receipt records from AI processing';
COMMENT ON COLUMN invoices.shop_name IS 'Name of the shop/vendor from the invoice';
COMMENT ON COLUMN invoices.invoice_date IS 'Original date from the invoice';
COMMENT ON COLUMN invoices.total_amount IS 'Total invoice amount in Rupiah';
COMMENT ON COLUMN invoices.transaction_type IS 'Type: bank, retail, or e-commerce';
COMMENT ON COLUMN invoices.processed_at IS 'When the invoice was processed by the system';

-- ========================================
-- Table 2: Invoice Items (Line items)
-- ========================================
CREATE TABLE invoice_items (
    id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL,
    item_name VARCHAR(500) NOT NULL,
    quantity INTEGER CHECK (quantity > 0),
    unit_price NUMERIC(15, 2) CHECK (unit_price >= 0),
    total_price NUMERIC(15, 2) NOT NULL CHECK (total_price >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_invoice
        FOREIGN KEY (invoice_id)
        REFERENCES invoices(id)
        ON DELETE CASCADE
);

-- Add comments
COMMENT ON TABLE invoice_items IS 'Individual line items from each invoice';
COMMENT ON COLUMN invoice_items.invoice_id IS 'Foreign key to parent invoice';
COMMENT ON COLUMN invoice_items.item_name IS 'Product/service name';
COMMENT ON COLUMN invoice_items.quantity IS 'Number of units purchased';
COMMENT ON COLUMN invoice_items.unit_price IS 'Price per unit';
COMMENT ON COLUMN invoice_items.total_price IS 'Total for this line item';

-- ========================================
-- Table 3: Platform Users (Multi-platform support)
-- ========================================
CREATE TABLE platform_users (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    platform_user_id VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    phone_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_platform_user UNIQUE(platform, platform_user_id)
);

-- Add comments
COMMENT ON TABLE platform_users IS 'Users from different platforms (Telegram, WhatsApp, etc.)';
COMMENT ON COLUMN platform_users.platform IS 'Platform name: telegram, whatsapp';
COMMENT ON COLUMN platform_users.platform_user_id IS 'User ID from the platform';

-- ========================================
-- Table 4: Spending Limits (Legacy - for backward compatibility)
-- ========================================
CREATE TABLE spending_limits (
    user_id BIGINT PRIMARY KEY,
    monthly_limit NUMERIC(15, 2) NOT NULL CHECK (monthly_limit >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE spending_limits IS 'Legacy spending limits table for Telegram bot';

-- ========================================
-- Table 5: Spending Limits V2 (Enhanced with platform support)
-- ========================================
CREATE TABLE spending_limits_v2 (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    monthly_limit NUMERIC(15, 2) NOT NULL CHECK (monthly_limit >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_platform_user
        FOREIGN KEY (user_id)
        REFERENCES platform_users(id)
        ON DELETE CASCADE,
    CONSTRAINT unique_user_limit UNIQUE(user_id)
);

COMMENT ON TABLE spending_limits_v2 IS 'Enhanced spending limits with platform user support';

-- ========================================
-- Indexes for Performance
-- ========================================

-- Invoices indexes
CREATE INDEX idx_invoices_date ON invoices(invoice_date DESC);
CREATE INDEX idx_invoices_shop ON invoices(shop_name);
CREATE INDEX idx_invoices_processed ON invoices(processed_at DESC);
CREATE INDEX idx_invoices_date_amount ON invoices(invoice_date DESC, total_amount);
CREATE INDEX idx_invoices_shop_date ON invoices(shop_name, invoice_date DESC);
CREATE INDEX idx_invoices_transaction_type ON invoices(transaction_type);

-- Invoice items indexes
CREATE INDEX idx_invoice_items_invoice_id ON invoice_items(invoice_id);
CREATE INDEX idx_invoice_items_name ON invoice_items(item_name);

-- Platform users indexes
CREATE INDEX idx_platform_users_platform ON platform_users(platform, platform_user_id);
CREATE INDEX idx_platform_users_last_active ON platform_users(last_active DESC);

-- Spending limits v2 indexes
CREATE INDEX idx_spending_limits_v2_user ON spending_limits_v2(user_id);

-- Full-text search index for shop names (optional, for future search features)
CREATE INDEX idx_invoices_shop_trgm ON invoices USING gin(shop_name gin_trgm_ops);
CREATE INDEX idx_invoice_items_name_trgm ON invoice_items USING gin(item_name gin_trgm_ops);

-- ========================================
-- Triggers for Auto-updating Timestamps
-- ========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to spending_limits
CREATE TRIGGER update_spending_limits_updated_at
    BEFORE UPDATE ON spending_limits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to spending_limits_v2
CREATE TRIGGER update_spending_limits_v2_updated_at
    BEFORE UPDATE ON spending_limits_v2
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- Useful Views for Analytics
-- ========================================

-- View: Invoice Summary with aggregated data
CREATE VIEW invoice_summary AS
SELECT
    i.id,
    i.shop_name,
    i.invoice_date,
    i.total_amount,
    i.transaction_type,
    i.processed_at,
    COUNT(ii.id) as item_count,
    EXTRACT(YEAR FROM i.invoice_date) as year,
    EXTRACT(MONTH FROM i.invoice_date) as month,
    EXTRACT(WEEK FROM i.invoice_date) as week,
    EXTRACT(DOY FROM i.invoice_date) as day_of_year
FROM invoices i
LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
GROUP BY i.id, i.shop_name, i.invoice_date, i.total_amount, i.transaction_type, i.processed_at;

COMMENT ON VIEW invoice_summary IS 'Aggregated view of invoices with item counts and time periods';

-- View: Monthly spending summary
CREATE VIEW monthly_spending AS
SELECT
    EXTRACT(YEAR FROM invoice_date) as year,
    EXTRACT(MONTH FROM invoice_date) as month,
    TO_CHAR(invoice_date, 'YYYY-MM') as month_key,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_spent,
    AVG(total_amount) as avg_transaction,
    MIN(total_amount) as min_transaction,
    MAX(total_amount) as max_transaction
FROM invoices
WHERE invoice_date IS NOT NULL
GROUP BY year, month, month_key
ORDER BY year DESC, month DESC;

COMMENT ON VIEW monthly_spending IS 'Monthly spending aggregates for quick analysis';

-- View: Top vendors by spending
CREATE VIEW top_vendors AS
SELECT
    shop_name,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_spent,
    AVG(total_amount) as avg_transaction,
    MAX(invoice_date) as last_transaction_date
FROM invoices
GROUP BY shop_name
ORDER BY total_spent DESC;

COMMENT ON VIEW top_vendors IS 'Vendors ranked by total spending';

-- ========================================
-- Functions for Common Queries
-- ========================================

-- Function: Get spending for a specific time period
CREATE OR REPLACE FUNCTION get_spending_by_period(
    start_date DATE,
    end_date DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    total_spent NUMERIC,
    transaction_count BIGINT,
    avg_transaction NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COALESCE(SUM(total_amount), 0)::NUMERIC as total_spent,
        COUNT(*)::BIGINT as transaction_count,
        COALESCE(AVG(total_amount), 0)::NUMERIC as avg_transaction
    FROM invoices
    WHERE invoice_date BETWEEN start_date AND end_date;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_spending_by_period IS 'Calculate spending metrics for a date range';

-- Function: Check if user exceeds spending limit
CREATE OR REPLACE FUNCTION check_spending_limit(
    p_user_id BIGINT,
    p_period_start DATE DEFAULT DATE_TRUNC('month', CURRENT_DATE)::DATE
)
RETURNS TABLE (
    monthly_limit NUMERIC,
    current_spending NUMERIC,
    remaining NUMERIC,
    percentage_used NUMERIC,
    is_exceeded BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sl.monthly_limit,
        COALESCE(spending.total, 0) as current_spending,
        sl.monthly_limit - COALESCE(spending.total, 0) as remaining,
        CASE
            WHEN sl.monthly_limit > 0 THEN
                (COALESCE(spending.total, 0) / sl.monthly_limit * 100)
            ELSE 0
        END as percentage_used,
        COALESCE(spending.total, 0) > sl.monthly_limit as is_exceeded
    FROM spending_limits_v2 sl
    LEFT JOIN (
        SELECT SUM(total_amount) as total
        FROM invoices
        WHERE invoice_date >= p_period_start
    ) spending ON true
    WHERE sl.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION check_spending_limit IS 'Check if user has exceeded their monthly spending limit';

-- ========================================
-- Row Level Security (RLS) Setup
-- ========================================
-- Note: Uncomment and customize based on your security requirements

-- Enable RLS on tables
-- ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE invoice_items ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE platform_users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE spending_limits ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE spending_limits_v2 ENABLE ROW LEVEL SECURITY;

-- Example policy: Allow all access for authenticated users
-- CREATE POLICY "Enable all access for authenticated users"
--     ON invoices FOR ALL
--     TO authenticated
--     USING (true);

-- Example policy: Users can only see their own data
-- CREATE POLICY "Users can view their own invoices"
--     ON invoices FOR SELECT
--     TO authenticated
--     USING (auth.uid() = user_id);

-- ========================================
-- Grant Permissions
-- ========================================
-- Grant necessary permissions to postgres role
GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;

-- For anon and authenticated users (adjust as needed)
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
-- GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;

-- ========================================
-- Sample Data Validation Queries
-- ========================================
-- Run these after migration to verify data integrity

-- Check record counts
-- SELECT
--     (SELECT COUNT(*) FROM invoices) as invoices_count,
--     (SELECT COUNT(*) FROM invoice_items) as items_count,
--     (SELECT COUNT(*) FROM platform_users) as users_count,
--     (SELECT COUNT(*) FROM spending_limits_v2) as limits_count;

-- Verify foreign key relationships
-- SELECT
--     i.id,
--     i.shop_name,
--     COUNT(ii.id) as item_count
-- FROM invoices i
-- LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
-- GROUP BY i.id, i.shop_name
-- LIMIT 10;

-- Check for orphaned records
-- SELECT COUNT(*) as orphaned_items
-- FROM invoice_items ii
-- WHERE NOT EXISTS (
--     SELECT 1 FROM invoices i WHERE i.id = ii.invoice_id
-- );

-- ========================================
-- Maintenance Tasks
-- ========================================

-- Analyze tables for query optimization
ANALYZE invoices;
ANALYZE invoice_items;
ANALYZE platform_users;
ANALYZE spending_limits;
ANALYZE spending_limits_v2;

-- Vacuum tables (optional, but recommended after bulk import)
-- VACUUM ANALYZE invoices;
-- VACUUM ANALYZE invoice_items;

-- ========================================
-- Success Message
-- ========================================
DO $$
BEGIN
    RAISE NOTICE '✅ Schema created successfully!';
    RAISE NOTICE '📊 Tables: invoices, invoice_items, platform_users, spending_limits, spending_limits_v2';
    RAISE NOTICE '📈 Views: invoice_summary, monthly_spending, top_vendors';
    RAISE NOTICE '🔧 Functions: get_spending_by_period, check_spending_limit';
    RAISE NOTICE '⚡ Next steps: Run data migration script';
END $$;
