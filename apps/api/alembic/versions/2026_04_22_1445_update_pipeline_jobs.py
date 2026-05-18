"""Update pipeline_jobs table

Revision ID: update_pipeline_jobs
Revises: add_maverick_fields
Create Date: 2026-04-22 14:45:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_pipeline_jobs'
down_revision = 'add_maverick_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Rename job_name to name
    op.alter_column('pipeline_jobs', 'job_name', new_column_name='name')
    
    # Add new columns
    op.add_column('pipeline_jobs', sa.Column('prerequisites', sa.Text(), nullable=True))
    op.add_column('pipeline_jobs', sa.Column('status', sa.String(50), nullable=True))
    op.add_column('pipeline_jobs', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('pipeline_jobs', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    
    # Set default status for existing rows
    op.execute("UPDATE pipeline_jobs SET status = 'PENDING' WHERE status IS NULL")
    
    # Make status NOT NULL
    op.alter_column('pipeline_jobs', 'status', nullable=False)
    
    # Update pipelines table status column to use enum
    op.execute("ALTER TABLE pipelines ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE pipelines SET status = 'DRAFT' WHERE status = 'active'")
    op.execute("UPDATE pipelines SET status = 'ACTIVE' WHERE status = 'active'")


def downgrade():
    op.alter_column('pipeline_jobs', 'name', new_column_name='job_name')
    op.drop_column('pipeline_jobs', 'updated_at')
    op.drop_column('pipeline_jobs', 'created_at')
    op.drop_column('pipeline_jobs', 'status')
    op.drop_column('pipeline_jobs', 'prerequisites')
