"""create tasks and task_status tables

Revision ID: 600c00ebfda1
Revises: 492eec39b72d
Create Date: 2023-12-13 19:13:00.277542

"""
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '600c00ebfda1'
down_revision = '492eec39b72d'
branch_labels = None
depends_on = None


def create_tasks_table():
    op.create_table(
        "tasks",
        sa.Column("id", UUID, primary_key=True, default=uuid4()),
        sa.Column("task_name", sa.String, unique=True, index=True, nullable=False),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_by", UUID, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", UUID, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

def create_task_status_table():
    op.create_table(
        "task_status",
        sa.Column("id", UUID, primary_key=True, default=uuid4()),
        sa.Column("status", sa.String, nullable=False),
        sa.Column("task_id", UUID, sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_by", UUID, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", UUID, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )

def upgrade() -> None:
    create_tasks_table()
    create_task_status_table()

def downgrade() -> None:
    op.drop_table("task_status")
    op.drop_table("tasks")
