"""Create AI usage logs table

Revision ID: create_ai_usage_logs
Revises: add_deployment_status_mavericks
Create Date: 2026-04-23 12:30:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_ai_usage_logs'
down_revision = 'add_deployment_status_mavericks'
branch_labels = None
depends_on = None


def upgrade():
    # Create ai_usage_logs table
    op.create_table(
        'ai_usage_logs',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('feature', sa.String(100), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('input_tokens', sa.Integer(), nullable=False),
        sa.Column('output_tokens', sa.Integer(), nullable=False),
        sa.Column('total_tokens', sa.Integer(), nullable=False),
        sa.Column('cost_usd', sa.Numeric(10, 6), nullable=False),
        sa.Column('request_duration_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Create indexes for better query performance
    op.create_index('idx_ai_usage_logs_feature', 'ai_usage_logs', ['feature'])
    op.create_index('idx_ai_usage_logs_created_at', 'ai_usage_logs', ['created_at'])
    op.create_index('idx_ai_usage_logs_success', 'ai_usage_logs', ['success'])


def downgrade():
    op.drop_index('idx_ai_usage_logs_success', 'ai_usage_logs')
    op.drop_index('idx_ai_usage_logs_created_at', 'ai_usage_logs')
    op.drop_index('idx_ai_usage_logs_feature', 'ai_usage_logs')
    op.drop_table('ai_usage_logs')
