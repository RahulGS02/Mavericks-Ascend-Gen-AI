"""Add batch focus areas for AI suggestions

Revision ID: add_batch_focus_areas
Revises: create_ai_usage_logs
Create Date: 2026-04-23 14:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_batch_focus_areas'
down_revision = 'create_ai_usage_logs'
branch_labels = None
depends_on = None


def upgrade():
    # Add focus areas columns to batches table
    op.add_column('batches', sa.Column('focus_areas', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('batches', sa.Column('required_skills', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('batches', sa.Column('preferred_skills', postgresql.ARRAY(sa.String()), nullable=True))
    op.add_column('batches', sa.Column('target_role', sa.String(255), nullable=True))


def downgrade():
    op.drop_column('batches', 'target_role')
    op.drop_column('batches', 'preferred_skills')
    op.drop_column('batches', 'required_skills')
    op.drop_column('batches', 'focus_areas')
