"""create applications table

Revision ID: 002
Revises: 001
Create Date: 2023-11-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_name', sa.String(length=100), nullable=False),
        sa.Column('application_code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Boolean(), nullable=True, server_default=sa.sql.expression.true()),
        sa.Column('action', sa.String(length=50), nullable=True),
        sa.Column('domain_name', sa.String(length=100), nullable=False),
        sa.Column('config', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['domain_name'], ['domains.domain_name'], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes
    op.create_index(op.f('ix_applications_id'), 'applications', ['id'], unique=False)
    op.create_index(op.f('ix_applications_application_name'), 'applications', ['application_name'], unique=False)
    op.create_index(op.f('ix_applications_application_code'), 'applications', ['application_code'], unique=True)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_applications_application_code'), table_name='applications')
    op.drop_index(op.f('ix_applications_application_name'), table_name='applications')
    op.drop_index(op.f('ix_applications_id'), table_name='applications')
    # Drop table
    op.drop_table('applications')
