-- Add role fields to deployment_requests table
-- Run this SQL in your PostgreSQL database

-- Make maverick_id nullable
ALTER TABLE deployment_requests ALTER COLUMN maverick_id DROP NOT NULL;

-- Add role_title column
ALTER TABLE deployment_requests ADD COLUMN IF NOT EXISTS role_title VARCHAR(255);

-- Add role_description column
ALTER TABLE deployment_requests ADD COLUMN IF NOT EXISTS role_description TEXT;

-- Add required_skills column (stored as TEXT/JSON)
ALTER TABLE deployment_requests ADD COLUMN IF NOT EXISTS required_skills TEXT;

-- Add preferred_skills column (stored as TEXT/JSON)
ALTER TABLE deployment_requests ADD COLUMN IF NOT EXISTS preferred_skills TEXT;

-- Update existing records to have a default role_title
UPDATE deployment_requests SET role_title = 'Deployment Requirement' WHERE role_title IS NULL;

-- Now make role_title required
ALTER TABLE deployment_requests ALTER COLUMN role_title SET NOT NULL;
