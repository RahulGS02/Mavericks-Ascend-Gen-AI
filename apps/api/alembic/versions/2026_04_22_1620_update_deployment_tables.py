"""Update deployment and deployment_requests tables

Revision ID: update_deployment_tables
Revises: create_assessments_table
Create Date: 2026-04-22 16:20:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_deployment_tables'
down_revision = 'create_assessments_table'
branch_labels = None
depends_on = None


def upgrade():
    # Update deployments table
    # Add new columns
    op.add_column('deployments', sa.Column('role', sa.String(255), nullable=True))
    op.add_column('deployments', sa.Column('manager_name', sa.String(255), nullable=True))
    op.add_column('deployments', sa.Column('location', sa.String(255), nullable=True))
    op.add_column('deployments', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('deployments', sa.Column('end_date', sa.Date(), nullable=True))
    op.add_column('deployments', sa.Column('status', sa.String(50), nullable=True))
    op.add_column('deployments', sa.Column('deployed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('deployments', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('deployments', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')))
    
    # Migrate existing data
    op.execute("UPDATE deployments SET start_date = deployment_date WHERE start_date IS NULL")
    op.execute("UPDATE deployments SET status = 'ACTIVE' WHERE status IS NULL")
    op.execute("UPDATE deployments SET role = role_title WHERE role IS NULL")
    op.execute("UPDATE deployments SET notes = remarks WHERE notes IS NULL")
    
    # Make batch_id nullable
    op.alter_column('deployments', 'batch_id', nullable=True)
    
    # Drop old columns
    op.drop_column('deployments', 'deployment_date')
    op.drop_column('deployments', 'role_title')
    op.drop_column('deployments', 'remarks')
    
    # Create enum type for deployment status
    op.execute("DROP TYPE IF EXISTS deploymentstatus CASCADE")
    op.execute("CREATE TYPE deploymentstatus AS ENUM ('ACTIVE', 'COMPLETED', 'TERMINATED')")
    op.execute("ALTER TABLE deployments ALTER COLUMN status TYPE deploymentstatus USING status::deploymentstatus")
    
    # Update deployment_requests table
    # Add new columns
    op.add_column('deployment_requests', sa.Column('competency', sa.String(100), nullable=True))
    op.add_column('deployment_requests', sa.Column('approved_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('deployment_requests', sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('deployment_requests', sa.Column('rejection_reason', sa.Text(), nullable=True))
    op.add_column('deployment_requests', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')))
    
    # Make fields nullable
    op.alter_column('deployment_requests', 'project_name', nullable=True)
    op.alter_column('deployment_requests', 'vertical', nullable=True)
    op.alter_column('deployment_requests', 'justification', nullable=True)
    
    # Drop old columns
    op.drop_column('deployment_requests', 'role_title')
    op.drop_column('deployment_requests', 'required_start_date')
    op.drop_column('deployment_requests', 'reviewed_by')
    op.drop_column('deployment_requests', 'reviewed_at')
    op.drop_column('deployment_requests', 'review_notes')
    
    # Add foreign key for approved_by
    op.create_foreign_key('fk_deployment_requests_approved_by', 'deployment_requests', 'users', ['approved_by'], ['id'])
    
    # Update enum values for status
    op.execute("ALTER TABLE deployment_requests ALTER COLUMN status TYPE VARCHAR(50)")
    op.execute("UPDATE deployment_requests SET status = 'PENDING' WHERE status = 'pending'")
    op.execute("UPDATE deployment_requests SET status = 'APPROVED' WHERE status = 'approved'")
    op.execute("UPDATE deployment_requests SET status = 'REJECTED' WHERE status = 'rejected'")
    op.execute("DROP TYPE IF EXISTS deploymentrequeststatus CASCADE")
    op.execute("CREATE TYPE deploymentrequeststatus AS ENUM ('PENDING', 'APPROVED', 'REJECTED')")
    op.execute("ALTER TABLE deployment_requests ALTER COLUMN status TYPE deploymentrequeststatus USING status::deploymentrequeststatus")


def downgrade():
    # Revert deployment_requests
    op.drop_constraint('fk_deployment_requests_approved_by', 'deployment_requests', type_='foreignkey')
    op.add_column('deployment_requests', sa.Column('review_notes', sa.Text()))
    op.add_column('deployment_requests', sa.Column('reviewed_at', sa.DateTime(timezone=True)))
    op.add_column('deployment_requests', sa.Column('reviewed_by', sa.dialects.postgresql.UUID(as_uuid=True)))
    op.add_column('deployment_requests', sa.Column('required_start_date', sa.Date()))
    op.add_column('deployment_requests', sa.Column('role_title', sa.String(255)))
    op.drop_column('deployment_requests', 'updated_at')
    op.drop_column('deployment_requests', 'rejection_reason')
    op.drop_column('deployment_requests', 'approved_at')
    op.drop_column('deployment_requests', 'approved_by')
    op.drop_column('deployment_requests', 'competency')
    
    # Revert deployments
    op.add_column('deployments', sa.Column('remarks', sa.Text()))
    op.add_column('deployments', sa.Column('role_title', sa.String(255)))
    op.add_column('deployments', sa.Column('deployment_date', sa.Date()))
    op.drop_column('deployments', 'updated_at')
    op.drop_column('deployments', 'notes')
    op.drop_column('deployments', 'deployed_at')
    op.drop_column('deployments', 'status')
    op.drop_column('deployments', 'end_date')
    op.drop_column('deployments', 'start_date')
    op.drop_column('deployments', 'location')
    op.drop_column('deployments', 'manager_name')
    op.drop_column('deployments', 'role')
    
    op.alter_column('deployments', 'batch_id', nullable=False)
