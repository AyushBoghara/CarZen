from alembic import op
import sqlalchemy as sa


revision = "20260921_02"
down_revision = "20260917_01"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "transactions" in tables:
        columns = {c["name"] for c in inspector.get_columns("transactions")}
        if "order_id" not in columns:
            op.add_column(
                "transactions",
                sa.Column(
                    "order_id",
                    sa.BigInteger(),
                    nullable=True,
                ),
            )

        indexes = {idx["name"] for idx in inspector.get_indexes("transactions")}
        if "ix_transactions_order_id" not in indexes:
            op.create_index(
                "ix_transactions_order_id",
                "transactions",
                ["order_id"],
                unique=True,
            )

        fks = {fk.get("name") for fk in inspector.get_foreign_keys("transactions")}
        if "fk_transactions_order_id_orders" not in fks and "orders" in tables:
            try:
                op.create_foreign_key(
                    "fk_transactions_order_id_orders",
                    "transactions",
                    "orders",
                    ["order_id"],
                    ["id"],
                )
            except Exception:
                pass


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = inspector.get_table_names()

    if "transactions" in tables:
        fks = {fk.get("name") for fk in inspector.get_foreign_keys("transactions")}
        if "fk_transactions_order_id_orders" in fks:
            op.drop_constraint(
                "fk_transactions_order_id_orders",
                "transactions",
                type_="foreignkey",
            )

        indexes = {idx["name"] for idx in inspector.get_indexes("transactions")}
        if "ix_transactions_order_id" in indexes:
            op.drop_index(
                "ix_transactions_order_id",
                table_name="transactions",
            )

        columns = {c["name"] for c in inspector.get_columns("transactions")}
        if "order_id" in columns:
            op.drop_column(
                "transactions",
                "order_id",
            )