"""create roles table

Revision ID: 6c1c5cd2d8fb
Revises: 3a63c42e4a10
Create Date: 2022-10-11 18:10:52.441019

"""
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "6c1c5cd2d8fb"
down_revision = "4d495ae5b0ff"
branch_labels = None
depends_on = None


def create_roles_table():
    op.create_table(
        "roles",
        sa.Column("id", UUID, primary_key=True, default=uuid4()),
        sa.Column("role", sa.Text, unique=True, index=True),
        sa.Column("permissions", sa.ARRAY(sa.String)),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_by", UUID, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", UUID, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def upgrade() -> None:
    create_roles_table()


def downgrade() -> None:
    op.drop_table("roles")
