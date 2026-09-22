"""add_lecturer_fine_columns

Revision ID: ec99d3e8dd82
Revises: 0c19773151e6
Create Date: 2026-09-22 10:07:38.161419

"""
from alembic import op
import sqlalchemy as sa


revision = 'ec99d3e8dd82'
down_revision = '0c19773151e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "LibraryConfig",
        sa.Column(
            "overdue_fine_vnd_per_day_lecturer",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("5000"),
        ),
    )
    op.create_check_constraint(
        "ck_library_config_fine_lecturer",
        "LibraryConfig",
        "overdue_fine_vnd_per_day_lecturer >= 0",
    )

    op.add_column(
        "FineHistory",
        sa.Column(
            "so_tien",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.create_check_constraint(
        "ck_fine_history_amount",
        "FineHistory",
        "so_tien >= 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_library_config_fine_lecturer", "LibraryConfig", type_="check")
    op.execute(
        """
        DECLARE @c1 sysname = (
            SELECT dc.name
            FROM sys.default_constraints dc
            JOIN sys.columns c
              ON dc.parent_object_id = c.object_id
             AND dc.parent_column_id = c.column_id
            WHERE dc.parent_object_id = OBJECT_ID('LibraryConfig')
              AND c.name = 'overdue_fine_vnd_per_day_lecturer'
        );
        IF @c1 IS NOT NULL
            EXEC('ALTER TABLE [LibraryConfig] DROP CONSTRAINT [' + @c1 + ']');
        """
    )
    op.drop_column("LibraryConfig", "overdue_fine_vnd_per_day_lecturer")

    op.drop_constraint("ck_fine_history_amount", "FineHistory", type_="check")
    op.execute(
        """
        DECLARE @c2 sysname = (
            SELECT dc.name
            FROM sys.default_constraints dc
            JOIN sys.columns c
              ON dc.parent_object_id = c.object_id
             AND dc.parent_column_id = c.column_id
            WHERE dc.parent_object_id = OBJECT_ID('FineHistory')
              AND c.name = 'so_tien'
        );
        IF @c2 IS NOT NULL
            EXEC('ALTER TABLE [FineHistory] DROP CONSTRAINT [' + @c2 + ']');
        """
    )
    op.drop_column("FineHistory", "so_tien")

