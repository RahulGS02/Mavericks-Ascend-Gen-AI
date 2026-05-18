"""Add config_metadata to assessments

Revision ID: add_assessment_config_metadata
Revises: create_maverick_skills
Create Date: 2026-04-24 19:35:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_assessment_config_metadata'
down_revision = 'create_maverick_skills'
branch_labels = None
depends_on = None


def upgrade():
    # Add config_metadata column to assessments table
    op.add_column('assessments', sa.Column('config_metadata', postgresql.JSONB, nullable=True))


def downgrade():
    op.drop_column('assessments', 'config_metadata')
