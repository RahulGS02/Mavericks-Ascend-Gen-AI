"""Update training_sessions table

Revision ID: update_training_sessions
Revises: update_job_progress_table
Create Date: 2026-04-22 15:45:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_training_sessions'
down_revision = 'update_job_progress_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('training_sessions', sa.Column('job_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('training_sessions', sa.Column('title', sa.String(255), nullable=True))
    op.add_column('training_sessions', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('training_sessions', sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('training_sessions', sa.Column('duration_minutes', sa.Integer(), nullable=True))
    op.add_column('training_sessions', sa.Column('location', sa.String(255), nullable=True))
    op.add_column('training_sessions', sa.Column('meeting_link', sa.Text(), nullable=True))
    op.add_column('training_sessions', sa.Column('status', sa.String(50), nullable=True))
    op.add_column('training_sessions', sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('training_sessions', sa.Column('completion_notes', sa.Text(), nullable=True))
    op.add_column('training_sessions', sa.Column('attendance_count', sa.Integer(), nullable=True))
    op.add_column('training_sessions', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    
    # Add foreign key for job_id
    op.create_foreign_key('fk_training_sessions_job_id', 'training_sessions', 'pipeline_jobs', ['job_id'], ['id'])
    
    # Migrate existing data
    op.execute("UPDATE training_sessions SET title = topic WHERE title IS NULL")
    op.execute("UPDATE training_sessions SET scheduled_date = session_date WHERE scheduled_date IS NULL")
    op.execute("UPDATE training_sessions SET duration_minutes = duration_hours * 60 WHERE duration_minutes IS NULL AND duration_hours IS NOT NULL")
    op.execute("UPDATE training_sessions SET status = 'SCHEDULED' WHERE status IS NULL")
    
    # Make nullable fields NOT NULL after migration
    op.alter_column('training_sessions', 'title', nullable=False)
    op.alter_column('training_sessions', 'scheduled_date', nullable=False)
    op.alter_column('training_sessions', 'duration_minutes', nullable=False)
    
    # Drop old columns
    op.drop_column('training_sessions', 'topic')
    op.drop_column('training_sessions', 'session_date')
    op.drop_column('training_sessions', 'duration_hours')
    op.drop_column('training_sessions', 'has_assessment')
    
    # Update trainer_id to be nullable
    op.alter_column('training_sessions', 'trainer_id', nullable=True)
    
    # Create enum type for status
    op.execute("DROP TYPE IF EXISTS sessionstatus CASCADE")
    op.execute("CREATE TYPE sessionstatus AS ENUM ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')")
    op.execute("ALTER TABLE training_sessions ALTER COLUMN status TYPE sessionstatus USING status::sessionstatus")


def downgrade():
    # Revert changes
    op.add_column('training_sessions', sa.Column('topic', sa.String(255), nullable=True))
    op.add_column('training_sessions', sa.Column('session_date', sa.Date(), nullable=True))
    op.add_column('training_sessions', sa.Column('duration_hours', sa.Integer(), nullable=True))
    op.add_column('training_sessions', sa.Column('has_assessment', sa.Boolean(), server_default='false'))
    
    op.execute("UPDATE training_sessions SET topic = title")
    op.execute("UPDATE training_sessions SET session_date = scheduled_date::date")
    op.execute("UPDATE training_sessions SET duration_hours = duration_minutes / 60")
    
    op.drop_constraint('fk_training_sessions_job_id', 'training_sessions', type_='foreignkey')
    op.drop_column('training_sessions', 'updated_at')
    op.drop_column('training_sessions', 'attendance_count')
    op.drop_column('training_sessions', 'completion_notes')
    op.drop_column('training_sessions', 'completed_at')
    op.drop_column('training_sessions', 'status')
    op.drop_column('training_sessions', 'meeting_link')
    op.drop_column('training_sessions', 'location')
    op.drop_column('training_sessions', 'duration_minutes')
    op.drop_column('training_sessions', 'scheduled_date')
    op.drop_column('training_sessions', 'description')
    op.drop_column('training_sessions', 'title')
    op.drop_column('training_sessions', 'job_id')
    
    op.alter_column('training_sessions', 'trainer_id', nullable=False)
