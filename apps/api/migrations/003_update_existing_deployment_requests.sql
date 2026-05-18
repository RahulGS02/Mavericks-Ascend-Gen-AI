-- ============================================================================
-- Migration: Update Existing Deployment Requests
-- Description: Sets default values for new columns in existing records
-- Date: 2026-05-16
-- ============================================================================

-- ============================================================================
-- 1. Set default positions_count for existing records
-- ============================================================================

UPDATE deployment_requests
SET positions_count = 1
WHERE positions_count IS NULL;

-- ============================================================================
-- 2. Set default filled_count for existing records
-- ============================================================================

UPDATE deployment_requests
SET filled_count = 0
WHERE filled_count IS NULL;

-- ============================================================================
-- 3. Set workflow_stage based on current status
-- ============================================================================

-- Map existing status to new workflow_stage
UPDATE deployment_requests
SET workflow_stage = CASE 
    WHEN status = 'PENDING' THEN 'PENDING'
    WHEN status = 'APPROVED' THEN 'APPROVED'
    WHEN status = 'REJECTED' THEN 'CLOSED'
    ELSE 'PENDING'
END
WHERE workflow_stage IS NULL OR workflow_stage = 'PENDING';

-- ============================================================================
-- 4. Count filled positions for APPROVED requests
-- ============================================================================

-- Update filled_count based on actual deployments
UPDATE deployment_requests dr
SET filled_count = (
    SELECT COUNT(*)
    FROM deployments d
    WHERE d.maverick_id IN (
        SELECT maverick_id 
        FROM deployment_requests dr2 
        WHERE dr2.id = dr.id 
        AND dr2.maverick_id IS NOT NULL
    )
    AND d.status = 'ACTIVE'
)
WHERE dr.status = 'APPROVED' 
AND dr.maverick_id IS NOT NULL;

-- ============================================================================
-- Confirmation message
-- ============================================================================
DO $$
DECLARE
    updated_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO updated_count FROM deployment_requests;
    RAISE NOTICE 'Updated % existing deployment requests with workflow fields.', updated_count;
END $$;
