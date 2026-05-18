"""update deployment requests - add role fields

Revision ID: 2026_05_01_role_fields
Revises: 6a86398b933f
Create Date: 2026-05-01 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_05_01_role_fields'
down_revision = '6a86398b933f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make maverick_id nullable (assign later)
    op.alter_column('deployment_requests', 'maverick_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=True)
    
    # Add role_title (required!)
    op.add_column('deployment_requests', 
                  sa.Column('role_title', sa.String(length=255), nullable=True))
    
    # Add role_description
    op.add_column('deployment_requests', 
                  sa.Column('role_description', sa.Text(), nullable=True))
    
    # Add required_skills (stored as JSON text)
    op.add_column('deployment_requests', 
                  sa.Column('required_skills', sa.Text(), nullable=True))
    
    # Add preferred_skills (stored as JSON text)
    op.add_column('deployment_requests', 
                  sa.Column('preferred_skills', sa.Text(), nullable=True))
    
    # Update existing records to have a default role_title
    op.execute("UPDATE deployment_requests SET role_title = 'Deployment Requirement' WHERE role_title IS NULL")
    
    # Now make role_title required
    op.alter_column('deployment_requests', 'role_title',
                    existing_type=sa.String(length=255),
                    nullable=False)


def downgrade() -> None:
    # Remove new columns
    op.drop_column('deployment_requests', 'preferred_skills')
    op.drop_column('deployment_requests', 'required_skills')
    op.drop_column('deployment_requests', 'role_description')
    op.drop_column('deployment_requests', 'role_title')
    
    # Make maverick_id required again
    op.alter_column('deployment_requests', 'maverick_id',
                    existing_type=sa.dialects.postgresql.UUID(),
                    nullable=False)
