"""add_assessment_link_column

Revision ID: 6a86398b933f
Revises: 2026_05_01_batch_schedule
Create Date: 2026-05-01 12:29:24.762668+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a86398b933f'
down_revision = '2026_05_01_batch_schedule'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add assessment_link column to assessments table
    op.add_column('assessments', sa.Column('assessment_link', sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove assessment_link column from assessments table
    op.drop_column('assessments', 'assessment_link')
