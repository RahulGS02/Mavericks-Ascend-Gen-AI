-- ============================================================================
-- Migration: Seed Workflow Test Data (OPTIONAL)
-- Description: Creates sample data for testing the workflow
-- Date: 2026-05-16
-- WARNING: This is for TESTING only! Skip in production.
-- ============================================================================

-- ============================================================================
-- Prerequisites: Run this only if you want test data
-- ============================================================================

-- You need:
-- 1. At least one manager user
-- 2. At least one HR user  
-- 3. At least 3 approved mavericks

-- ============================================================================
-- EXAMPLE: Create sample candidates (COMMENTED - Customize as needed)
-- ============================================================================

/*
-- Get IDs for testing (replace with actual UUIDs from your database)
DO $$
DECLARE
    v_requirement_id UUID;
    v_maverick_id_1 UUID;
    v_maverick_id_2 UUID;
    v_maverick_id_3 UUID;
    v_hr_user_id UUID;
    v_candidate_id_1 UUID;
    v_candidate_id_2 UUID;
BEGIN
    -- Get the first requirement card
    SELECT id INTO v_requirement_id 
    FROM deployment_requests 
    ORDER BY created_at DESC 
    LIMIT 1;
    
    -- Get HR user
    SELECT id INTO v_hr_user_id 
    FROM users 
    WHERE role = 'HR' 
    LIMIT 1;
    
    -- Get 3 available mavericks
    SELECT id INTO v_maverick_id_1 
    FROM mavericks 
    WHERE profile_status = 'APPROVED' 
    ORDER BY created_at 
    LIMIT 1;
    
    SELECT id INTO v_maverick_id_2 
    FROM mavericks 
    WHERE profile_status = 'APPROVED' 
    AND id != v_maverick_id_1
    ORDER BY created_at 
    LIMIT 1 OFFSET 1;
    
    SELECT id INTO v_maverick_id_3 
    FROM mavericks 
    WHERE profile_status = 'APPROVED' 
    AND id NOT IN (v_maverick_id_1, v_maverick_id_2)
    ORDER BY created_at 
    LIMIT 1 OFFSET 2;
    
    -- Insert suggested candidates
    INSERT INTO requirement_candidates 
    (id, requirement_id, maverick_id, suggested_by, match_score, status, manager_notes)
    VALUES 
    (gen_random_uuid(), v_requirement_id, v_maverick_id_1, v_hr_user_id, 92.5, 'SUGGESTED', NULL),
    (gen_random_uuid(), v_requirement_id, v_maverick_id_2, v_hr_user_id, 85.0, 'SUGGESTED', NULL),
    (gen_random_uuid(), v_requirement_id, v_maverick_id_3, v_hr_user_id, 78.5, 'SUGGESTED', NULL)
    RETURNING id INTO v_candidate_id_1;
    
    -- Update requirement workflow stage
    UPDATE deployment_requests 
    SET workflow_stage = 'CANDIDATES_SUGGESTED'
    WHERE id = v_requirement_id;
    
    -- Create workflow history entry
    INSERT INTO requirement_workflow_history 
    (requirement_id, from_stage, to_stage, changed_by, change_reason)
    VALUES 
    (v_requirement_id, 'PENDING', 'UNDER_REVIEW', v_hr_user_id, 'HR reviewing requirement'),
    (v_requirement_id, 'UNDER_REVIEW', 'CANDIDATES_SUGGESTED', v_hr_user_id, 'Added 3 suggested candidates');
    
    RAISE NOTICE 'Sample workflow data created successfully.';
    RAISE NOTICE 'Requirement ID: %', v_requirement_id;
    RAISE NOTICE 'Suggested 3 candidates';
END $$;
*/

-- ============================================================================
-- Alternative: Manual insert template (customize with your UUIDs)
-- ============================================================================

/*
-- Example template - replace UUIDs with actual values

-- 1. Suggest candidates
INSERT INTO requirement_candidates 
(requirement_id, maverick_id, suggested_by, match_score, status)
VALUES 
('YOUR-REQUIREMENT-UUID', 'MAVERICK-1-UUID', 'HR-USER-UUID', 92.5, 'SUGGESTED'),
('YOUR-REQUIREMENT-UUID', 'MAVERICK-2-UUID', 'HR-USER-UUID', 85.0, 'SUGGESTED'),
('YOUR-REQUIREMENT-UUID', 'MAVERICK-3-UUID', 'HR-USER-UUID', 78.5, 'SUGGESTED');

-- 2. Update workflow stage
UPDATE deployment_requests 
SET workflow_stage = 'CANDIDATES_SUGGESTED'
WHERE id = 'YOUR-REQUIREMENT-UUID';

-- 3. Create workflow history
INSERT INTO requirement_workflow_history 
(requirement_id, from_stage, to_stage, changed_by, change_reason)
VALUES 
('YOUR-REQUIREMENT-UUID', 'PENDING', 'CANDIDATES_SUGGESTED', 'HR-USER-UUID', 'HR suggested candidates');
*/

-- ============================================================================
-- Confirmation message
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Test data script loaded (commented out)';
    RAISE NOTICE 'Uncomment and customize to create test data';
    RAISE NOTICE '========================================';
END $$;
