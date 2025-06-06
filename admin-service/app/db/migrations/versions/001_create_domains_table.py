"""create domains table

Revision ID: 001
Revises: 
Create Date: 2023-11-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create domains table
    op.create_table(
        'domains',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('domain_name', sa.String(length=100), nullable=False),
        sa.Column('domain_code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Boolean(), nullable=True, server_default=sa.sql.expression.true()),
        sa.Column('action', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    # Create indexes
    op.create_index(op.f('ix_domains_id'), 'domains', ['id'], unique=False)
    op.create_index(op.f('ix_domains_domain_name'), 'domains', ['domain_name'], unique=True)
    op.create_index(op.f('ix_domains_domain_code'), 'domains', ['domain_code'], unique=True)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_domains_domain_code'), table_name='domains')
    op.drop_index(op.f('ix_domains_domain_name'), table_name='domains')
    op.drop_index(op.f('ix_domains_id'), table_name='domains')
    # Drop table
    op.drop_table('domains')
