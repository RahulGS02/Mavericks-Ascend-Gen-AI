"""Create assessments table and update assessment_attempts

Revision ID: create_assessments_table
Revises: update_training_sessions
Create Date: 2026-04-22 16:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_assessments_table'
down_revision = 'update_training_sessions'
branch_labels = None
depends_on = None


def upgrade():
    # Create assessments table
    op.create_table(
        'assessments',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('max_marks', sa.Numeric(5, 2), nullable=False),
        sa.Column('passing_marks', sa.Numeric(5, 2), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'))
    )
    
    # Add foreign keys for assessments table
    op.create_foreign_key('fk_assessments_job_id', 'assessments', 'pipeline_jobs', ['job_id'], ['id'])
    op.create_foreign_key('fk_assessments_batch_id', 'assessments', 'batches', ['batch_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_assessments_created_by', 'assessments', 'users', ['created_by'], ['id'])
    
    # Update assessment_attempts table
    # Add new columns
    op.add_column('assessment_attempts', sa.Column('assessment_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('assessment_attempts', sa.Column('feedback', sa.Text(), nullable=True))
    op.add_column('assessment_attempts', sa.Column('evaluated_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('assessment_attempts', sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=True))
    
    # Drop old columns
    op.drop_column('assessment_attempts', 'job_id')
    op.drop_column('assessment_attempts', 'attempt_number')
    op.drop_column('assessment_attempts', 'assessed_on')
    op.drop_column('assessment_attempts', 'assessed_by')
    op.drop_column('assessment_attempts', 'remarks')
    
    # Add foreign keys
    op.create_foreign_key('fk_assessment_attempts_assessment_id', 'assessment_attempts', 'assessments', ['assessment_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_assessment_attempts_evaluated_by', 'assessment_attempts', 'users', ['evaluated_by'], ['id'])
    
    # After data migration, make columns NOT NULL
    # For now leave as nullable since we don't have existing data


def downgrade():
    # Drop foreign keys
    op.drop_constraint('fk_assessment_attempts_evaluated_by', 'assessment_attempts', type_='foreignkey')
    op.drop_constraint('fk_assessment_attempts_assessment_id', 'assessment_attempts', type_='foreignkey')
    
    # Add back old columns
    op.add_column('assessment_attempts', sa.Column('job_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('assessment_attempts', sa.Column('attempt_number', sa.Integer(), server_default='1'))
    op.add_column('assessment_attempts', sa.Column('assessed_on', sa.Date(), nullable=True))
    op.add_column('assessment_attempts', sa.Column('assessed_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('assessment_attempts', sa.Column('remarks', sa.Text(), nullable=True))
    
    # Drop new columns
    op.drop_column('assessment_attempts', 'evaluated_at')
    op.drop_column('assessment_attempts', 'evaluated_by')
    op.drop_column('assessment_attempts', 'feedback')
    op.drop_column('assessment_attempts', 'assessment_id')
    
    # Drop assessments table
    op.drop_constraint('fk_assessments_created_by', 'assessments', type_='foreignkey')
    op.drop_constraint('fk_assessments_batch_id', 'assessments', type_='foreignkey')
    op.drop_constraint('fk_assessments_job_id', 'assessments', type_='foreignkey')
    op.drop_table('assessments')
