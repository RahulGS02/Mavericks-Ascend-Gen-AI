"""Update batches table for batch management

Revision ID: update_batches_table
Revises: update_pipeline_jobs
Create Date: 2026-04-22 15:11:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_batches_table'
down_revision = 'update_pipeline_jobs'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('batches', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('batches', sa.Column('max_capacity', sa.Integer(), nullable=True))
    op.add_column('batches', sa.Column('current_enrollment', sa.Integer(), server_default='0', nullable=False))
    op.add_column('batches', sa.Column('created_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('batches', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))

    # Rename expected_end_date to end_date
    op.alter_column('batches', 'expected_end_date', new_column_name='end_date')

    # Add foreign key for created_by
    op.create_foreign_key('fk_batches_created_by', 'batches', 'users', ['created_by'], ['id'])

    # Convert status column to VARCHAR temporarily
    op.execute("ALTER TABLE batches ALTER COLUMN status TYPE VARCHAR(50)")

    # Update existing data values
    op.execute("UPDATE batches SET status = 'ACTIVE' WHERE status = 'active'")
    op.execute("UPDATE batches SET status = 'COMPLETED' WHERE status = 'completed'")
    op.execute("UPDATE batches SET status = 'ON_HOLD' WHERE status = 'on_hold'")
    op.execute("UPDATE batches SET status = 'ARCHIVED' WHERE status = 'archived'")

    # Drop and recreate the enum type with new values
    op.execute("DROP TYPE IF EXISTS batchstatus CASCADE")
    op.execute("CREATE TYPE batchstatus AS ENUM ('PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED', 'ON_HOLD', 'ARCHIVED')")

    # Convert column back to enum
    op.execute("ALTER TABLE batches ALTER COLUMN status TYPE batchstatus USING status::batchstatus")


def downgrade():
    op.drop_constraint('fk_batches_created_by', 'batches', type_='foreignkey')
    op.drop_column('batches', 'updated_at')
    op.drop_column('batches', 'created_by')
    op.drop_column('batches', 'current_enrollment')
    op.drop_column('batches', 'max_capacity')
    op.drop_column('batches', 'description')
    op.alter_column('batches', 'end_date', new_column_name='expected_end_date')
