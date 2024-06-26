"""create users table

Revision ID: 492eec39b72d
Revises: 8e0c5b7e9066
Create Date: 2022-10-11 18:39:19.297356

"""
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "492eec39b72d"
down_revision = "6c1c5cd2d8fb"
branch_labels = None
depends_on = None


def create_users_table():
    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True, default=uuid4()),
        sa.Column("username", sa.String(40), unique=True, index=True, nullable=False),
        sa.Column("fullname", sa.Text, nullable=False),
        sa.Column("salt", sa.Text, nullable=False),
        sa.Column("password", sa.Text, nullable=False),
        sa.Column("email", sa.String(60), unique=True, index=True, nullable=False),
        sa.Column("is_superadmin", sa.Boolean, nullable=True, default=False),
        sa.Column("role_id", UUID, sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_by", UUID, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", UUID, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def upgrade() -> None:
    create_users_table()


def downgrade() -> None:
    op.drop_table("users")
