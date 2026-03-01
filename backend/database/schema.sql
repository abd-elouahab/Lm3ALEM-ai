-- L'M3alem AI — PostgreSQL schema
-- Run against Supabase/PostgreSQL

-- Enums
CREATE TYPE user_role AS ENUM ('client', 'artisan');
CREATE TYPE specialty_enum AS ENUM ('zlayji', 'sebbagh', 'gebbas', 'plombier', 'electricien');
CREATE TYPE complexity_enum AS ENUM ('simple', 'moyenne', 'complexe');
CREATE TYPE job_status_enum AS ENUM ('pending', 'matching', 'accepted', 'in_progress', 'completed', 'disputed', 'cancelled');
CREATE TYPE matching_response_enum AS ENUM ('pending', 'accepted', 'refused', 'no_response');
CREATE TYPE guarantee_status_enum AS ENUM ('open', 'claimed', 'resolved', 'expired');
CREATE TYPE payment_status_enum AS ENUM ('held', 'released', 'refunded');

-- Users (base for clients and artisans)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Artisans (extends users)
CREATE TABLE artisans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    specialty specialty_enum NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    is_available BOOLEAN DEFAULT true,
    ranking_score DOUBLE PRECISION DEFAULT 100,
    savings DOUBLE PRECISION DEFAULT 0,
    total_jobs INTEGER DEFAULT 0,
    bio TEXT,
    profile_photo_url VARCHAR(500),
    refusal_count INTEGER DEFAULT 0,
    requires_medical_certificate BOOLEAN DEFAULT false,
    priority_boost BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Clients (extends users)
CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    city VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    reliability_score DOUBLE PRECISION DEFAULT 100,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Jobs (service requests)
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    artisan_id INTEGER REFERENCES artisans(id) ON DELETE SET NULL,
    problem_type specialty_enum NOT NULL,
    symptom TEXT,
    photo_url VARCHAR(500),
    ai_description TEXT,
    severity INTEGER CHECK (severity >= 1 AND severity <= 5),
    surface_area_m2 DOUBLE PRECISION,
    complexity complexity_enum,
    nb_elements_affected INTEGER,
    estimated_price_min DOUBLE PRECISION,
    estimated_price_max DOUBLE PRECISION,
    estimated_duration_hours DOUBLE PRECISION,
    final_price DOUBLE PRECISION,
    status job_status_enum DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    confirmed_start TIMESTAMPTZ,
    confirmed_end TIMESTAMPTZ,
    after_photo_url VARCHAR(500)
);

-- Matching attempts (Phase 1 notifications)
CREATE TABLE matching_attempts (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    artisan_id INTEGER NOT NULL REFERENCES artisans(id) ON DELETE CASCADE,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    response matching_response_enum DEFAULT 'pending',
    refusal_count INTEGER DEFAULT 0
);

-- Ratings (post-service)
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    artisan_id INTEGER NOT NULL REFERENCES artisans(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(job_id)
);

-- Guarantees (48h post-service window)
CREATE TABLE guarantees (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    opened_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    status guarantee_status_enum DEFAULT 'open',
    complaint_text TEXT,
    complaint_photo_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(job_id)
);

-- Payments (escrow)
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    amount DOUBLE PRECISION NOT NULL,
    artisan_share DOUBLE PRECISION NOT NULL,
    savings_share DOUBLE PRECISION NOT NULL,
    platform_share DOUBLE PRECISION NOT NULL,
    status payment_status_enum DEFAULT 'held',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    released_at TIMESTAMPTZ,
    UNIQUE(job_id)
);

-- Indexes
CREATE INDEX idx_artisans_specialty ON artisans(specialty);
CREATE INDEX idx_artisans_city ON artisans(city);
CREATE INDEX idx_artisans_available ON artisans(is_available);
CREATE INDEX idx_jobs_client ON jobs(client_id);
CREATE INDEX idx_jobs_artisan ON jobs(artisan_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_matching_attempts_job ON matching_attempts(job_id);
CREATE INDEX idx_guarantees_expires ON guarantees(expires_at);
CREATE INDEX idx_guarantees_status ON guarantees(status);
