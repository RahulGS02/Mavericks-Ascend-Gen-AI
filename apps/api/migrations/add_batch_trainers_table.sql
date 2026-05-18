-- Migration: Add batch_trainers table for multiple trainers per batch
-- Date: 2026-05-11
-- Description: Enables assigning multiple trainers to a single batch

-- Create batch_trainers junction table
CREATE TABLE IF NOT EXISTS batch_trainers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
    trainer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_lead_trainer BOOLEAN NOT NULL DEFAULT FALSE,
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    assigned_by UUID REFERENCES users(id),
    
    -- Ensure a trainer is not assigned to the same batch multiple times
    UNIQUE(batch_id, trainer_id)
);

-- Add indexes for better query performance
CREATE INDEX idx_batch_trainers_batch_id ON batch_trainers(batch_id);
CREATE INDEX idx_batch_trainers_trainer_id ON batch_trainers(trainer_id);
CREATE INDEX idx_batch_trainers_lead ON batch_trainers(batch_id, is_lead_trainer);

-- Migrate existing single trainer assignments to the new table
INSERT INTO batch_trainers (batch_id, trainer_id, is_lead_trainer, assigned_at)
SELECT 
    id as batch_id,
    trainer_id,
    TRUE as is_lead_trainer,  -- Mark existing trainers as lead
    created_at as assigned_at
FROM batches
WHERE trainer_id IS NOT NULL;

-- Note: We keep the trainer_id column in batches table for backwards compatibility
-- but new code should use the batch_trainers relationship
COMMENT ON TABLE batch_trainers IS 'Junction table for many-to-many relationship between batches and trainers';
COMMENT ON COLUMN batch_trainers.is_lead_trainer IS 'Indicates the primary/lead trainer for the batch';
COMMENT ON COLUMN batch_trainers.assigned_by IS 'HR user who made the assignment';
