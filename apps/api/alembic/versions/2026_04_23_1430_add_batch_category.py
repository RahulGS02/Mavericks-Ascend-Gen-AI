"""Add batch category for AI matching

Revision ID: add_batch_category
Revises: add_batch_focus_areas
Create Date: 2026-04-23 14:30:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_batch_category'
down_revision = 'add_batch_focus_areas'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum type
    batch_category_enum = sa.Enum(
        'TECH_DEVELOPMENT',
        'TECH_DEVOPS',
        'TECH_TESTING',
        'TECH_DATA_SCIENCE',
        'TECH_CYBER_SECURITY',
        'SOFT_SKILLS',
        name='batchcategory'
    )
    batch_category_enum.create(op.get_bind(), checkfirst=True)
    
    # Add category column
    op.add_column('batches', sa.Column('category', batch_category_enum, nullable=True))


def downgrade():
    op.drop_column('batches', 'category')
    sa.Enum(name='batchcategory').drop(op.get_bind(), checkfirst=True)
