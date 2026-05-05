-- VakeelLink Database Setup
-- Run this in your Supabase SQL Editor

-- 1. Profiles Table (Extends Supabase Auth)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    full_name TEXT NOT NULL,
    phone_number TEXT,
    role TEXT NOT NULL CHECK (role IN ('client', 'lawyer', 'admin')),
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Lawyers Table
CREATE TABLE IF NOT EXISTS public.lawyers (
    id UUID REFERENCES public.profiles(id) ON DELETE CASCADE PRIMARY KEY,
    specialization TEXT, -- e.g., 'criminal', 'family'
    domain TEXT,         -- same as specialization
    experience_years INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_online BOOLEAN DEFAULT FALSE,
    bar_council_id TEXT UNIQUE,
    bio TEXT,
    location TEXT,
    fee_per_consultation INTEGER,
    profile_image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Query History Table
CREATE TABLE IF NOT EXISTS public.query_history (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID, -- Optional link to profile
    query TEXT NOT NULL,
    answer JSONB NOT NULL,
    domain TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.lawyers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.query_history ENABLE ROW LEVEL SECURITY;

-- 5. Public Access Policies (For development)
CREATE POLICY "Allow public read profiles" ON public.profiles FOR SELECT USING (true);
CREATE POLICY "Allow public read lawyers" ON public.lawyers FOR SELECT USING (true);
CREATE POLICY "Allow public read history" ON public.query_history FOR SELECT USING (true);
