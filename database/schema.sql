-- ===========================================
-- Property Voice Agent - Supabase Database Schema
-- ===========================================
-- Run this SQL in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/YOUR_PROJECT/sql/new
-- ===========================================

-- Enable UUID extension (usually enabled by default)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ===========================================
-- PROPERTIES TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS properties (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    manager_name VARCHAR(255),
    manager_email VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- UNITS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS units (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    property_id UUID REFERENCES properties(id) ON DELETE CASCADE,
    unit_number VARCHAR(50) NOT NULL,
    bedrooms INTEGER NOT NULL DEFAULT 1,
    bathrooms DECIMAL(3,1) NOT NULL DEFAULT 1.0,
    square_feet INTEGER,
    rent DECIMAL(10,2) NOT NULL,
    deposit DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'available', -- available, occupied, maintenance, pending
    amenities TEXT[], -- Array of amenities
    description TEXT,
    available_date DATE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- CONTACTS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS contacts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    type VARCHAR(50) NOT NULL, -- tenant, prospect, owner, vendor, other
    unit_id UUID REFERENCES units(id) ON DELETE SET NULL,
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- CALLS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS calls (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    bland_call_id VARCHAR(255) UNIQUE,
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    call_type VARCHAR(50), -- leasing, maintenance, payment, general
    status VARCHAR(50) DEFAULT 'completed', -- in_progress, completed, failed
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    duration INTEGER, -- in seconds
    recording_url TEXT,
    transcript TEXT,
    summary JSONB,
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    unit_id UUID REFERENCES units(id) ON DELETE SET NULL,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    sentiment VARCHAR(20), -- positive, neutral, negative
    resolved BOOLEAN DEFAULT false,
    email_sent BOOLEAN DEFAULT false,
    email_sent_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- MAINTENANCE TICKETS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS maintenance_tickets (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    ticket_number VARCHAR(20) UNIQUE,
    unit_id UUID REFERENCES units(id) ON DELETE SET NULL,
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    contact_id UUID REFERENCES contacts(id) ON DELETE SET NULL,
    call_id UUID REFERENCES calls(id) ON DELETE SET NULL,
    issue_type VARCHAR(100) NOT NULL,
    urgency VARCHAR(20) NOT NULL DEFAULT 'routine', -- emergency, urgent, routine
    description TEXT NOT NULL,
    location_in_unit VARCHAR(255),
    status VARCHAR(50) DEFAULT 'open', -- open, assigned, in_progress, completed, cancelled
    assigned_to VARCHAR(255),
    scheduled_date DATE,
    scheduled_time TIME,
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    notes TEXT,
    reported_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- TOUR REQUESTS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS tour_requests (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    property_id UUID REFERENCES properties(id) ON DELETE SET NULL,
    call_id UUID REFERENCES calls(id) ON DELETE SET NULL,
    visitor_name VARCHAR(255) NOT NULL,
    visitor_email VARCHAR(255),
    visitor_phone VARCHAR(20),
    preferred_date DATE,
    preferred_time TIME,
    alternate_date DATE,
    alternate_time TIME,
    bedrooms_interested INTEGER,
    max_budget DECIMAL(10,2),
    move_in_date DATE,
    notes TEXT,
    status VARCHAR(50) DEFAULT 'pending', -- pending, confirmed, completed, cancelled, no_show
    confirmed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ===========================================
-- INDEXES FOR PERFORMANCE
-- ===========================================
CREATE INDEX IF NOT EXISTS idx_calls_bland_call_id ON calls(bland_call_id);
CREATE INDEX IF NOT EXISTS idx_calls_from_number ON calls(from_number);
CREATE INDEX IF NOT EXISTS idx_calls_created_at ON calls(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_calls_call_type ON calls(call_type);

CREATE INDEX IF NOT EXISTS idx_units_property_id ON units(property_id);
CREATE INDEX IF NOT EXISTS idx_units_status ON units(status);
CREATE INDEX IF NOT EXISTS idx_units_bedrooms ON units(bedrooms);

CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email);
CREATE INDEX IF NOT EXISTS idx_contacts_type ON contacts(type);

CREATE INDEX IF NOT EXISTS idx_maintenance_tickets_unit_id ON maintenance_tickets(unit_id);
CREATE INDEX IF NOT EXISTS idx_maintenance_tickets_status ON maintenance_tickets(status);
CREATE INDEX IF NOT EXISTS idx_maintenance_tickets_urgency ON maintenance_tickets(urgency);

CREATE INDEX IF NOT EXISTS idx_tour_requests_status ON tour_requests(status);
CREATE INDEX IF NOT EXISTS idx_tour_requests_preferred_date ON tour_requests(preferred_date);

-- ===========================================
-- ROW LEVEL SECURITY (RLS)
-- ===========================================
-- Enable RLS on all tables
ALTER TABLE properties ENABLE ROW LEVEL SECURITY;
ALTER TABLE units ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE maintenance_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE tour_requests ENABLE ROW LEVEL SECURITY;

-- For MVP, allow all operations with the service key
-- In production, you'd create more specific policies
CREATE POLICY "Allow all operations for service role" ON properties FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON units FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON contacts FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON calls FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON maintenance_tickets FOR ALL USING (true);
CREATE POLICY "Allow all operations for service role" ON tour_requests FOR ALL USING (true);

-- ===========================================
-- HELPER FUNCTIONS
-- ===========================================

-- Function to generate ticket numbers
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TRIGGER AS $$
BEGIN
    NEW.ticket_number := 'MT-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(NEXTVAL('ticket_seq')::TEXT, 4, '0');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create sequence for ticket numbers
CREATE SEQUENCE IF NOT EXISTS ticket_seq START 1;

-- Trigger to auto-generate ticket numbers
DROP TRIGGER IF EXISTS set_ticket_number ON maintenance_tickets;
CREATE TRIGGER set_ticket_number
    BEFORE INSERT ON maintenance_tickets
    FOR EACH ROW
    WHEN (NEW.ticket_number IS NULL)
    EXECUTE FUNCTION generate_ticket_number();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_units_updated_at BEFORE UPDATE ON units
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contacts_updated_at BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maintenance_tickets_updated_at BEFORE UPDATE ON maintenance_tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tour_requests_updated_at BEFORE UPDATE ON tour_requests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===========================================
-- SEED DATA (Optional - for testing)
-- ===========================================
-- Uncomment and run this section to add test data

/*
-- Insert a test property
INSERT INTO properties (name, address, city, state, zip_code, phone, manager_email)
VALUES (
    'Sunset Apartments',
    '123 Main Street',
    'Jacksonville',
    'FL',
    '32201',
    '+19045551234',
    'manager@sunsetapts.com'
);

-- Get the property ID for inserting units
DO $$
DECLARE
    prop_id UUID;
BEGIN
    SELECT id INTO prop_id FROM properties WHERE name = 'Sunset Apartments' LIMIT 1;
    
    -- Insert test units
    INSERT INTO units (property_id, unit_number, bedrooms, bathrooms, square_feet, rent, status, amenities, description)
    VALUES 
        (prop_id, '101', 1, 1.0, 650, 1250.00, 'available', ARRAY['Washer/Dryer', 'Balcony'], 'Cozy 1BR with balcony'),
        (prop_id, '102', 1, 1.0, 700, 1350.00, 'available', ARRAY['Washer/Dryer', 'Updated Kitchen'], 'Recently renovated 1BR'),
        (prop_id, '201', 2, 1.0, 900, 1650.00, 'available', ARRAY['Washer/Dryer', 'Balcony', 'Walk-in Closet'], 'Spacious 2BR corner unit'),
        (prop_id, '202', 2, 2.0, 1000, 1850.00, 'occupied', ARRAY['Washer/Dryer', 'Balcony', 'Stainless Appliances'], 'Premium 2BR/2BA'),
        (prop_id, '301', 3, 2.0, 1200, 2250.00, 'available', ARRAY['Washer/Dryer', 'Balcony', 'Walk-in Closet', 'City Views'], 'Top floor 3BR with views'),
        (prop_id, '302', 3, 2.0, 1300, 2450.00, 'maintenance', ARRAY['Washer/Dryer', 'Balcony', 'Den', 'City Views'], 'Penthouse 3BR - being renovated');
END $$;
*/

-- ===========================================
-- VERIFICATION QUERIES
-- ===========================================
-- Run these to verify the schema was created correctly:

-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'calls';
-- SELECT * FROM properties LIMIT 5;
-- SELECT * FROM units LIMIT 10;
