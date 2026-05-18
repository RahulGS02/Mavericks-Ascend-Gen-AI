-- Fix FeedbackRating enum values
-- Run this if you get "invalid input value for enum feedbackrating: EXCELLENT"

-- Drop the table first (if it exists)
DROP TABLE IF EXISTS trainer_feedback CASCADE;

-- Drop the enum type
DROP TYPE IF EXISTS feedbackrating CASCADE;

-- Recreate the enum type with correct lowercase values
CREATE TYPE feedbackrating AS ENUM ('excellent', 'good', 'average', 'poor', 'very_poor');

-- Now re-run the migration
-- cd apps/api
-- venv\Scripts\activate
-- alembic upgrade head
