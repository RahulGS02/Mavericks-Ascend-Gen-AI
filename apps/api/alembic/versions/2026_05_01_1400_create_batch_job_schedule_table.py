"""create_batch_job_schedule_table

Revision ID: 2026_05_01_batch_schedule
Revises: add_trainer_feedback
Create Date: 2026-05-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026_05_01_batch_schedule'
down_revision = 'add_trainer_feedback'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum for job schedule status (if not exists)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE jobschedulestatus AS ENUM (
                'NOT_SCHEDULED',
                'SCHEDULED',
                'IN_PROGRESS',
                'COMPLETED',
                'CANCELLED',
                'OVERDUE'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create batch_job_schedules table
    op.create_table('batch_job_schedules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pipeline_job_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Scheduling information
        sa.Column('scheduled_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_end_date', sa.DateTime(timezone=True), nullable=True),
        
        # Training session details
        sa.Column('meeting_link', sa.String(length=500), nullable=True),
        sa.Column('meeting_password', sa.String(length=100), nullable=True),
        sa.Column('attendance_required', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('attendance_count', sa.Integer(), nullable=True, server_default='0'),
        
        # Assessment link
        sa.Column('assessment_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Deployment link
        sa.Column('deployment_project_link', sa.String(length=500), nullable=True),
        
        # Status tracking
        sa.Column('status', postgresql.ENUM('NOT_SCHEDULED', 'SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'OVERDUE',
                                   name='jobschedulestatus', create_type=False),
                 nullable=False, server_default='NOT_SCHEDULED'),
        sa.Column('completion_percentage', sa.Integer(), nullable=True, server_default='0'),
        
        # Notes
        sa.Column('trainer_notes', sa.Text(), nullable=True),
        sa.Column('is_published', sa.Boolean(), nullable=True, server_default='false'),
        
        # Metadata
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        
        # Primary key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign keys
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['pipeline_job_id'], ['pipeline_jobs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'])
    )
    
    # Create indexes for better query performance
    op.create_index('ix_batch_job_schedules_batch_id', 'batch_job_schedules', ['batch_id'])
    op.create_index('ix_batch_job_schedules_pipeline_job_id', 'batch_job_schedules', ['pipeline_job_id'])
    op.create_index('ix_batch_job_schedules_assessment_id', 'batch_job_schedules', ['assessment_id'])
    op.create_index('ix_batch_job_schedules_status', 'batch_job_schedules', ['status'])
    
    # Create unique constraint to prevent duplicate schedules for same batch+job combo
    op.create_unique_constraint(
        'uq_batch_job_schedule',
        'batch_job_schedules',
        ['batch_id', 'pipeline_job_id']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_batch_job_schedules_status', table_name='batch_job_schedules')
    op.drop_index('ix_batch_job_schedules_assessment_id', table_name='batch_job_schedules')
    op.drop_index('ix_batch_job_schedules_pipeline_job_id', table_name='batch_job_schedules')
    op.drop_index('ix_batch_job_schedules_batch_id', table_name='batch_job_schedules')
    
    # Drop constraint
    op.drop_constraint('uq_batch_job_schedule', 'batch_job_schedules', type_='unique')
    
    # Drop table
    op.drop_table('batch_job_schedules')
    
    # Drop enum
    op.execute('DROP TYPE jobschedulestatus')
