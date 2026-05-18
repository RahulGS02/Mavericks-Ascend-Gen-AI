"""add trainer feedback table

Revision ID: add_trainer_feedback
Revises: add_assessment_config_metadata
Create Date: 2026-04-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_trainer_feedback'
down_revision = 'add_assessment_config_metadata'
branch_labels = None
depends_on = None


def upgrade():
    # Create trainer_feedback table
    op.create_table(
        'trainer_feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('maverick_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('trainer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Enum('excellent', 'good', 'average', 'poor', 'very_poor', name='feedbackrating'), nullable=False),
        sa.Column('subject_knowledge', sa.Integer(), nullable=False),
        sa.Column('communication_skills', sa.Integer(), nullable=False),
        sa.Column('session_quality', sa.Integer(), nullable=False),
        sa.Column('doubt_resolution', sa.Integer(), nullable=False),
        sa.Column('positive_feedback', sa.Text(), nullable=True),
        sa.Column('areas_for_improvement', sa.Text(), nullable=True),
        sa.Column('additional_comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['maverick_id'], ['mavericks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['trainer_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index('ix_trainer_feedback_trainer_id', 'trainer_feedback', ['trainer_id'])
    op.create_index('ix_trainer_feedback_maverick_id', 'trainer_feedback', ['maverick_id'])
    op.create_index('ix_trainer_feedback_batch_id', 'trainer_feedback', ['batch_id'])
    op.create_index('ix_trainer_feedback_created_at', 'trainer_feedback', ['created_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_trainer_feedback_created_at', table_name='trainer_feedback')
    op.drop_index('ix_trainer_feedback_batch_id', table_name='trainer_feedback')
    op.drop_index('ix_trainer_feedback_maverick_id', table_name='trainer_feedback')
    op.drop_index('ix_trainer_feedback_trainer_id', table_name='trainer_feedback')
    
    # Drop table
    op.drop_table('trainer_feedback')
    
    # Drop enum
    op.execute('DROP TYPE feedbackrating')
