-- ============================================================================
-- Migration: Workflow Enums and Constraints
-- Description: Creates enums and adds check constraints for workflow tables
-- Date: 2026-05-16
-- ============================================================================

-- ============================================================================
-- 1. Workflow Stage Enum (for deployment_requests)
-- ============================================================================

-- Valid workflow stages
-- PENDING: Just created by manager
-- UNDER_REVIEW: HR is reviewing the requirement
-- CANDIDATES_SUGGESTED: HR has added candidate suggestions
-- INTERVIEW_SCHEDULING: Manager has shortlisted, HR is scheduling
-- INTERVIEWS_IN_PROGRESS: Interviews are ongoing
-- SELECTION_IN_PROGRESS: Interviews completed, manager is selecting
-- AWAITING_APPROVAL: Manager has selected, waiting HR approval
-- APPROVED: HR approved the selections
-- COMPLETED: All positions filled and deployed
-- CLOSED: Requirement archived

ALTER TABLE deployment_requests 
DROP CONSTRAINT IF EXISTS chk_workflow_stage;

ALTER TABLE deployment_requests 
ADD CONSTRAINT chk_workflow_stage 
CHECK (workflow_stage IN (
    'PENDING',
    'UNDER_REVIEW',
    'CANDIDATES_SUGGESTED',
    'INTERVIEW_SCHEDULING',
    'INTERVIEWS_IN_PROGRESS',
    'SELECTION_IN_PROGRESS',
    'AWAITING_APPROVAL',
    'APPROVED',
    'COMPLETED',
    'CLOSED'
));

-- ============================================================================
-- 2. Candidate Status Enum (for requirement_candidates)
-- ============================================================================

-- Valid candidate statuses
-- SUGGESTED: HR suggested this candidate
-- SHORTLISTED: Manager shortlisted for interview
-- REJECTED: Manager/HR rejected the candidate
-- INTERVIEW_SCHEDULED: Interview has been scheduled
-- INTERVIEWED: Interview completed
-- SELECTED: Manager selected this candidate
-- APPROVED: HR approved the selection
-- DEPLOYED: Deployment record created
-- ON_HOLD: Kept in reserve

ALTER TABLE requirement_candidates 
DROP CONSTRAINT IF EXISTS chk_candidate_status;

ALTER TABLE requirement_candidates 
ADD CONSTRAINT chk_candidate_status 
CHECK (status IN (
    'SUGGESTED',
    'SHORTLISTED',
    'REJECTED',
    'INTERVIEW_SCHEDULED',
    'INTERVIEWED',
    'SELECTED',
    'APPROVED',
    'DEPLOYED',
    'ON_HOLD'
));

-- ============================================================================
-- 3. Interview Type Enum (for requirement_interviews)
-- ============================================================================

ALTER TABLE requirement_interviews 
DROP CONSTRAINT IF EXISTS chk_interview_type;

ALTER TABLE requirement_interviews 
ADD CONSTRAINT chk_interview_type 
CHECK (interview_type IN ('ONLINE', 'OFFLINE'));

-- ============================================================================
-- 4. Interview Mode Enum (for requirement_interviews)
-- ============================================================================

ALTER TABLE requirement_interviews 
DROP CONSTRAINT IF EXISTS chk_interview_mode;

ALTER TABLE requirement_interviews 
ADD CONSTRAINT chk_interview_mode 
CHECK (interview_mode IN (
    'VIDEO_CALL',
    'PHONE_CALL',
    'IN_PERSON',
    'PANEL_INTERVIEW',
    'TECHNICAL_ROUND',
    'HR_ROUND',
    'MANAGERIAL_ROUND'
));

-- ============================================================================
-- 5. Interview Status Enum (for requirement_interviews)
-- ============================================================================

ALTER TABLE requirement_interviews 
DROP CONSTRAINT IF EXISTS chk_interview_status;

ALTER TABLE requirement_interviews 
ADD CONSTRAINT chk_interview_status 
CHECK (status IN (
    'SCHEDULED',
    'CONFIRMED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED',
    'RESCHEDULED',
    'NO_SHOW'
));

-- ============================================================================
-- 6. Rating Constraints (for requirement_interviews)
-- ============================================================================

ALTER TABLE requirement_interviews 
DROP CONSTRAINT IF EXISTS chk_rating_range;

ALTER TABLE requirement_interviews 
ADD CONSTRAINT chk_rating_range 
CHECK (rating IS NULL OR (rating >= 1.0 AND rating <= 5.0));

ALTER TABLE requirement_interviews 
DROP CONSTRAINT IF EXISTS chk_technical_rating_range;

ALTER TABLE requirement_interviews 
ADD CONSTRAINT chk_technical_rating_range 
CHECK (technical_rating IS NULL OR (technical_rating >= 1.0 AND technical_rating <= 5.0));

ALTER TABLE requirement_interviews 
DROP CONSTRAINT IF EXISTS chk_communication_rating_range;

ALTER TABLE requirement_interviews 
ADD CONSTRAINT chk_communication_rating_range 
CHECK (communication_rating IS NULL OR (communication_rating >= 1.0 AND communication_rating <= 5.0));

ALTER TABLE requirement_interviews 
DROP CONSTRAINT IF EXISTS chk_cultural_fit_rating_range;

ALTER TABLE requirement_interviews 
ADD CONSTRAINT chk_cultural_fit_rating_range 
CHECK (cultural_fit_rating IS NULL OR (cultural_fit_rating >= 1.0 AND cultural_fit_rating <= 5.0));

-- ============================================================================
-- 7. Match Score Constraint (for requirement_candidates)
-- ============================================================================

ALTER TABLE requirement_candidates 
DROP CONSTRAINT IF EXISTS chk_match_score_range;

ALTER TABLE requirement_candidates 
ADD CONSTRAINT chk_match_score_range 
CHECK (match_score IS NULL OR (match_score >= 0 AND match_score <= 100));

-- ============================================================================
-- 8. Positions Count Constraints (for deployment_requests)
-- ============================================================================

ALTER TABLE deployment_requests 
DROP CONSTRAINT IF EXISTS chk_positions_count_positive;

ALTER TABLE deployment_requests 
ADD CONSTRAINT chk_positions_count_positive 
CHECK (positions_count > 0);

ALTER TABLE deployment_requests 
DROP CONSTRAINT IF EXISTS chk_filled_count_valid;

ALTER TABLE deployment_requests 
ADD CONSTRAINT chk_filled_count_valid 
CHECK (filled_count >= 0 AND filled_count <= positions_count);

-- ============================================================================
-- Confirmation message
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE 'Workflow enums and constraints created successfully.';
END $$;
