"""Add name and email fields to mavericks

Revision ID: add_maverick_fields
Revises: b7e70f5faafe
Create Date: 2026-04-22 11:57:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_maverick_fields'
down_revision = 'b7e70f5faafe'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to mavericks table
    op.add_column('mavericks', sa.Column('name', sa.String(255), nullable=True))
    op.add_column('mavericks', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('mavericks', sa.Column('branch', sa.String(255), nullable=True))
    op.add_column('mavericks', sa.Column('cgpa', sa.Float(), nullable=True))
    op.add_column('mavericks', sa.Column('github_url', sa.Text(), nullable=True))
    op.add_column('mavericks', sa.Column('linkedin_url', sa.Text(), nullable=True))
    op.add_column('mavericks', sa.Column('review_notes', sa.Text(), nullable=True))
    op.add_column('mavericks', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('mavericks', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    
    # Make user_id nullable
    op.alter_column('mavericks', 'user_id', nullable=True)
    
    # Drop old columns
    op.drop_column('mavericks', 'submitted_at')
    op.drop_column('mavericks', 'reviewed_at')
    
    # Create index on email
    op.create_index('ix_mavericks_email', 'mavericks', ['email'], unique=True)
    
    # Update enum values - use ALTER TYPE to add new values
    # For profilestatus: add 'pending' and 'approved' if they don't exist
    op.execute("ALTER TYPE profilestatus ADD VALUE IF NOT EXISTS 'pending'")
    op.execute("ALTER TYPE profilestatus ADD VALUE IF NOT EXISTS 'approved'")

    # Update existing data to use new values
    op.execute("""
        UPDATE mavericks
        SET profile_status = CASE
            WHEN profile_status::text = 'pending_review' THEN 'pending'::profilestatus
            WHEN profile_status::text = 'shortlisted' THEN 'approved'::profilestatus
            WHEN profile_status::text = 'assigned' THEN 'approved'::profilestatus
            ELSE profile_status
        END
    """)

    # For deploymentstatus: add new values
    op.execute("ALTER TYPE deploymentstatus ADD VALUE IF NOT EXISTS 'available'")
    op.execute("ALTER TYPE deploymentstatus ADD VALUE IF NOT EXISTS 'on_bench'")

    # Update existing data
    op.execute("""
        UPDATE mavericks
        SET deployment_status = CASE
            WHEN deployment_status::text = 'in_training' THEN 'available'::deploymentstatus
            WHEN deployment_status::text = 'ready_for_deployment' THEN 'available'::deploymentstatus
            ELSE deployment_status
        END
    """)


def downgrade():
    op.drop_index('ix_mavericks_email')
    op.add_column('mavericks', sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('mavericks', sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('mavericks', 'user_id', nullable=False)
    op.drop_column('mavericks', 'updated_at')
    op.drop_column('mavericks', 'created_at')
    op.drop_column('mavericks', 'review_notes')
    op.drop_column('mavericks', 'linkedin_url')
    op.drop_column('mavericks', 'github_url')
    op.drop_column('mavericks', 'cgpa')
    op.drop_column('mavericks', 'branch')
    op.drop_column('mavericks', 'email')
    op.drop_column('mavericks', 'name')
