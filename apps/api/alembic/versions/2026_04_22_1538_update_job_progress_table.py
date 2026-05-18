"""Update maverick_job_progress table

Revision ID: update_job_progress_table
Revises: update_batches_table
Create Date: 2026-04-22 15:38:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_job_progress_table'
down_revision = 'update_batches_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('maverick_job_progress', sa.Column('score', sa.Numeric(5, 2), nullable=True))
    op.add_column('maverick_job_progress', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('maverick_job_progress', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    
    # Update enum type for status
    # First convert to VARCHAR
    op.execute("ALTER TABLE maverick_job_progress ALTER COLUMN status TYPE VARCHAR(50)")
    
    # Update existing values to new enum values
    op.execute("UPDATE maverick_job_progress SET status = 'PENDING' WHERE status = 'not_started'")
    op.execute("UPDATE maverick_job_progress SET status = 'IN_PROGRESS' WHERE status = 'in_progress'")
    op.execute("UPDATE maverick_job_progress SET status = 'COMPLETED' WHERE status = 'completed'")
    op.execute("UPDATE maverick_job_progress SET status = 'SKIPPED' WHERE status = 'skipped'")
    op.execute("UPDATE maverick_job_progress SET status = 'FAILED' WHERE status = 'failed_assessment'")
    
    # Drop old enum and create new one
    op.execute("DROP TYPE IF EXISTS jobprogressstatus CASCADE")
    op.execute("CREATE TYPE progressstatus AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'SKIPPED')")
    
    # Convert column back to enum
    op.execute("ALTER TABLE maverick_job_progress ALTER COLUMN status TYPE progressstatus USING status::progressstatus")


def downgrade():
    op.drop_column('maverick_job_progress', 'updated_at')
    op.drop_column('maverick_job_progress', 'created_at')
    op.drop_column('maverick_job_progress', 'score')
    
    # Revert enum changes
    op.execute("ALTER TABLE maverick_job_progress ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE maverick_job_progress SET status = 'not_started' WHERE status = 'PENDING'")
    op.execute("UPDATE maverick_job_progress SET status = 'in_progress' WHERE status = 'IN_PROGRESS'")
    op.execute("UPDATE maverick_job_progress SET status = 'completed' WHERE status = 'COMPLETED'")
    op.execute("UPDATE maverick_job_progress SET status = 'skipped' WHERE status = 'SKIPPED'")
    op.execute("UPDATE maverick_job_progress SET status = 'failed_assessment' WHERE status = 'FAILED'")
    op.execute("DROP TYPE IF EXISTS progressstatus CASCADE")
    op.execute("CREATE TYPE jobprogressstatus AS ENUM ('not_started', 'in_progress', 'completed', 'skipped', 'failed_assessment')")
    op.execute("ALTER TABLE maverick_job_progress ALTER COLUMN status TYPE jobprogressstatus USING status::jobprogressstatus")
