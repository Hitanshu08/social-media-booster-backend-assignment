-- PostgreSQL 16 schema for Social Booster campaigns.
-- Designed for fast filtering (status/platform), substring search, and insights time series.

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

DO $$
BEGIN
  CREATE TYPE campaign_status AS ENUM ('active', 'paused', 'completed', 'draft');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
  CREATE TYPE platform AS ENUM ('facebook', 'google', 'instagram', 'linkedin', 'twitter');
EXCEPTION
  WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS campaigns (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  status campaign_status NOT NULL,
  platform platform NOT NULL,
  budget numeric(12,2) NOT NULL CHECK (budget > 0),
  start_date date NOT NULL,
  end_date date NOT NULL,
  description text NOT NULL,
  target_audience text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT campaigns_date_range CHECK (start_date <= end_date)
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER campaigns_set_updated_at
BEFORE UPDATE ON campaigns
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- Filtering and sorting
CREATE INDEX IF NOT EXISTS campaigns_status_idx ON campaigns (status);
CREATE INDEX IF NOT EXISTS campaigns_platform_idx ON campaigns (platform);
CREATE INDEX IF NOT EXISTS campaigns_dates_idx ON campaigns (start_date, end_date);
CREATE INDEX IF NOT EXISTS campaigns_updated_at_idx ON campaigns (updated_at DESC);

-- Substring search for name/description/target_audience
CREATE INDEX IF NOT EXISTS campaigns_name_trgm_idx
  ON campaigns USING gin (lower(name) gin_trgm_ops);
CREATE INDEX IF NOT EXISTS campaigns_desc_trgm_idx
  ON campaigns USING gin (lower(description) gin_trgm_ops);
CREATE INDEX IF NOT EXISTS campaigns_audience_trgm_idx
  ON campaigns USING gin (lower(target_audience) gin_trgm_ops);

CREATE TABLE IF NOT EXISTS campaign_insights (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id uuid NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  captured_at timestamptz NOT NULL DEFAULT now(),
  impressions bigint NOT NULL CHECK (impressions >= 0),
  clicks bigint NOT NULL CHECK (clicks >= 0),
  conversions bigint NOT NULL CHECK (conversions >= 0),
  ctr numeric(5,2) NOT NULL CHECK (ctr >= 0),
  cpc numeric(10,2) NOT NULL CHECK (cpc >= 0),
  roi numeric(8,2) NOT NULL,
  engagement_likes bigint NOT NULL CHECK (engagement_likes >= 0),
  engagement_shares bigint NOT NULL CHECK (engagement_shares >= 0),
  engagement_comments bigint NOT NULL CHECK (engagement_comments >= 0)
);

CREATE INDEX IF NOT EXISTS campaign_insights_campaign_time_idx
  ON campaign_insights (campaign_id, captured_at DESC);
