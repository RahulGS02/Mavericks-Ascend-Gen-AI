"""Add AI resume data to mavericks

Revision ID: add_ai_resume_data
Revises: add_batch_category
Create Date: 2026-04-23 14:45:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_ai_resume_data'
down_revision = 'add_batch_category'
branch_labels = None
depends_on = None


def upgrade():
    # Add ai_resume_data column to store complete AI-parsed resume
    op.add_column('mavericks', sa.Column('ai_resume_data', postgresql.JSONB, nullable=True))


def downgrade():
    op.drop_column('mavericks', 'ai_resume_data')
