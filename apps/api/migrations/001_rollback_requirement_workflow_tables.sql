-- ============================================================================
-- ROLLBACK Migration: Requirement Card Workflow Tables
-- Description: Drops all tables and columns created by the workflow migration
-- Date: 2026-05-16
-- WARNING: This will DELETE ALL workflow data!
-- ============================================================================

-- Drop tables in reverse order (respect foreign key constraints)

DROP TABLE IF EXISTS requirement_notifications CASCADE;
DROP TABLE IF EXISTS requirement_workflow_history CASCADE;
DROP TABLE IF EXISTS requirement_interviews CASCADE;
DROP TABLE IF EXISTS requirement_candidates CASCADE;

-- Drop indexes
DROP INDEX IF EXISTS idx_deployment_requests_workflow_stage;

-- Remove columns from deployment_requests
ALTER TABLE deployment_requests DROP COLUMN IF EXISTS positions_count;
ALTER TABLE deployment_requests DROP COLUMN IF EXISTS filled_count;
ALTER TABLE deployment_requests DROP COLUMN IF EXISTS workflow_stage;

-- ============================================================================
-- Confirmation message
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Rollback completed successfully. All workflow tables and columns removed.';
END $$;
