-- ============================================================================
-- Migration: Requirement Card Workflow Tables
-- Description: Creates tables for candidate suggestions, interviews, and 
--              complete talent acquisition workflow
-- Date: 2026-05-16
-- ============================================================================

-- ============================================================================
-- 1. ALTER deployment_requests table (add workflow fields)
-- ============================================================================

ALTER TABLE deployment_requests 
ADD COLUMN IF NOT EXISTS positions_count INTEGER DEFAULT 1;

ALTER TABLE deployment_requests 
ADD COLUMN IF NOT EXISTS filled_count INTEGER DEFAULT 0;

ALTER TABLE deployment_requests 
ADD COLUMN IF NOT EXISTS workflow_stage VARCHAR(50) DEFAULT 'PENDING';

-- Add index for workflow_stage for faster queries
CREATE INDEX IF NOT EXISTS idx_deployment_requests_workflow_stage 
ON deployment_requests(workflow_stage);

-- ============================================================================
-- 2. CREATE requirement_candidates table
-- ============================================================================

CREATE TABLE IF NOT EXISTS requirement_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES deployment_requests(id) ON DELETE CASCADE,
    maverick_id UUID NOT NULL REFERENCES mavericks(id) ON DELETE CASCADE,
    suggested_by UUID REFERENCES users(id) ON DELETE SET NULL,
    suggestion_date TIMESTAMP DEFAULT NOW(),
    match_score DECIMAL(5,2),
    status VARCHAR(50) DEFAULT 'SUGGESTED',
    shortlist_notes TEXT,
    rejection_reason TEXT,
    manager_notes TEXT,
    hr_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_requirement_maverick UNIQUE (requirement_id, maverick_id)
);

-- Indexes for requirement_candidates
CREATE INDEX IF NOT EXISTS idx_requirement_candidates_requirement 
ON requirement_candidates(requirement_id);

CREATE INDEX IF NOT EXISTS idx_requirement_candidates_maverick 
ON requirement_candidates(maverick_id);

CREATE INDEX IF NOT EXISTS idx_requirement_candidates_status 
ON requirement_candidates(status);

-- ============================================================================
-- 3. CREATE requirement_interviews table
-- ============================================================================

CREATE TABLE IF NOT EXISTS requirement_interviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES deployment_requests(id) ON DELETE CASCADE,
    candidate_id UUID NOT NULL REFERENCES requirement_candidates(id) ON DELETE CASCADE,
    maverick_id UUID NOT NULL REFERENCES mavericks(id) ON DELETE CASCADE,
    interview_type VARCHAR(20) DEFAULT 'ONLINE',
    interview_mode VARCHAR(50) DEFAULT 'VIDEO_CALL',
    interview_date DATE NOT NULL,
    interview_time TIME NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    location TEXT,
    video_link TEXT,
    interviewer_panel JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'SCHEDULED',
    feedback TEXT,
    rating DECIMAL(2,1),
    technical_rating DECIMAL(2,1),
    communication_rating DECIMAL(2,1),
    cultural_fit_rating DECIMAL(2,1),
    scheduled_by UUID REFERENCES users(id) ON DELETE SET NULL,
    completed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for requirement_interviews
CREATE INDEX IF NOT EXISTS idx_requirement_interviews_requirement 
ON requirement_interviews(requirement_id);

CREATE INDEX IF NOT EXISTS idx_requirement_interviews_candidate 
ON requirement_interviews(candidate_id);

CREATE INDEX IF NOT EXISTS idx_requirement_interviews_maverick 
ON requirement_interviews(maverick_id);

CREATE INDEX IF NOT EXISTS idx_requirement_interviews_status 
ON requirement_interviews(status);

CREATE INDEX IF NOT EXISTS idx_requirement_interviews_date 
ON requirement_interviews(interview_date);

-- ============================================================================
-- 4. CREATE requirement_workflow_history table (audit trail)
-- ============================================================================

CREATE TABLE IF NOT EXISTS requirement_workflow_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES deployment_requests(id) ON DELETE CASCADE,
    from_stage VARCHAR(50),
    to_stage VARCHAR(50) NOT NULL,
    changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    change_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Index for workflow history
CREATE INDEX IF NOT EXISTS idx_requirement_workflow_history_requirement 
ON requirement_workflow_history(requirement_id);

-- ============================================================================
-- 5. CREATE requirement_notifications table
-- ============================================================================

CREATE TABLE IF NOT EXISTS requirement_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requirement_id UUID NOT NULL REFERENCES deployment_requests(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for notifications
CREATE INDEX IF NOT EXISTS idx_requirement_notifications_user 
ON requirement_notifications(user_id, is_read);

CREATE INDEX IF NOT EXISTS idx_requirement_notifications_requirement 
ON requirement_notifications(requirement_id);

-- ============================================================================
-- 6. Add comments for documentation
-- ============================================================================

COMMENT ON TABLE requirement_candidates IS 'Stores candidates suggested/shortlisted for requirement cards';
COMMENT ON TABLE requirement_interviews IS 'Stores interview schedules and feedback for candidates';
COMMENT ON TABLE requirement_workflow_history IS 'Audit trail for requirement card workflow changes';
COMMENT ON TABLE requirement_notifications IS 'Notifications for requirement card workflow events';

COMMENT ON COLUMN deployment_requests.positions_count IS 'Total number of positions to fill';
COMMENT ON COLUMN deployment_requests.filled_count IS 'Number of positions filled/deployed';
COMMENT ON COLUMN deployment_requests.workflow_stage IS 'Current stage in the workflow';
