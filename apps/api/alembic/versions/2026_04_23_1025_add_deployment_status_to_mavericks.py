"""Add deployment_status to mavericks table

Revision ID: add_deployment_status_mavericks
Revises: update_deployment_tables
Create Date: 2026-04-23 10:25:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_deployment_status_mavericks'
down_revision = 'update_deployment_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum type for maverick deployment status
    op.execute("DROP TYPE IF EXISTS maverickdeploymentstatus CASCADE")
    op.execute("CREATE TYPE maverickdeploymentstatus AS ENUM ('AVAILABLE', 'DEPLOYED', 'ON_LEAVE', 'TERMINATED')")
    
    # Add deployment_status column
    op.add_column('mavericks', sa.Column('deployment_status', sa.String(50), nullable=True))
    
    # Set default value for existing records
    op.execute("UPDATE mavericks SET deployment_status = 'AVAILABLE' WHERE deployment_status IS NULL")
    
    # Convert to enum type
    op.execute("ALTER TABLE mavericks ALTER COLUMN deployment_status TYPE maverickdeploymentstatus USING deployment_status::maverickdeploymentstatus")
    
    # Set default and not null
    op.execute("ALTER TABLE mavericks ALTER COLUMN deployment_status SET DEFAULT 'AVAILABLE'")
    op.alter_column('mavericks', 'deployment_status', nullable=False)


def downgrade():
    op.drop_column('mavericks', 'deployment_status')
    op.execute("DROP TYPE IF EXISTS maverickdeploymentstatus CASCADE")
