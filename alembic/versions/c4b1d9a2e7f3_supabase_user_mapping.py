"""Supabase user mapping

Revision ID: c4b1d9a2e7f3
Revises: a30f6a48f116
Create Date: 2026-03-03

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4b1d9a2e7f3"
down_revision: Union[str, None] = "a30f6a48f116"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("supabase_user_id", sa.String(length=36), nullable=True),
    )
    op.create_index(
        op.f("ix_users_supabase_user_id"),
        "users",
        ["supabase_user_id"],
        unique=True,
    )

    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.drop_index(op.f("ix_users_supabase_user_id"), table_name="users")
    op.drop_column("users", "supabase_user_id")
