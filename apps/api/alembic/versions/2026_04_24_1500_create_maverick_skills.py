"""Create maverick_skills table for skill proficiency tracking

Revision ID: create_maverick_skills
Revises: add_ai_resume_data
Create Date: 2026-04-24 15:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_maverick_skills'
down_revision = 'add_ai_resume_data'
branch_labels = None
depends_on = None


def upgrade():
    # Create maverick_skills table
    op.create_table(
        'maverick_skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('maverick_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('mavericks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('proficiency_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('proficiency_level', sa.String(50), nullable=True),
        sa.Column('assessment_score', sa.Float(), nullable=True),
        sa.Column('training_completion', sa.Float(), nullable=True),
        sa.Column('self_declared', sa.Float(), nullable=True),
        sa.Column('ai_analyzed', sa.Float(), nullable=True),
        sa.Column('assessment_count', sa.Integer(), server_default='0'),
        sa.Column('training_count', sa.Integer(), server_default='0'),
        sa.Column('last_assessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_trained_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('improvement_suggestions', postgresql.JSONB, nullable=True),
        sa.Column('radar_data', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create index for faster lookups
    op.create_index('idx_maverick_skills_maverick_id', 'maverick_skills', ['maverick_id'])
    op.create_index('idx_maverick_skills_skill_name', 'maverick_skills', ['skill_name'])
    
    # Create unique constraint to prevent duplicate skills per maverick
    op.create_unique_constraint('uq_maverick_skill', 'maverick_skills', ['maverick_id', 'skill_name'])


def downgrade():
    op.drop_constraint('uq_maverick_skill', 'maverick_skills', type_='unique')
    op.drop_index('idx_maverick_skills_skill_name')
    op.drop_index('idx_maverick_skills_maverick_id')
    op.drop_table('maverick_skills')
