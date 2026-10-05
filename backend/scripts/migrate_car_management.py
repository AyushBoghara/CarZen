"""Apply the additive Car Management lifecycle columns to an existing MySQL database."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import inspect, text

from app.database.connection.conn import engine


CAR_COLUMNS = {
    "approval_status": "ENUM('draft','pending_approval','approved','rejected','published','sold','inactive') NOT NULL DEFAULT 'pending_approval'",
    "rejection_reason": "TEXT NULL",
    "verified_at": "DATETIME NULL",
    "verified_by_id": "BIGINT NULL",
}

CAR_CONDITION_ENUM = "ENUM('excellent','good','poor','new','oldCar')"

def upgrade() -> None:
    inspector = inspect(engine)
    existing = {column["name"] for column in inspector.get_columns("cars")}
    with engine.begin() as connection:
        for name, definition in CAR_COLUMNS.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE cars ADD COLUMN {name} {definition}"))

        condition_type = connection.execute(
            text("SHOW COLUMNS FROM cars LIKE 'condition'")
        ).mappings().one()["Type"]
        if "'NEW'" not in condition_type or "'OLD'" not in condition_type:
            connection.execute(
                text(f"ALTER TABLE cars MODIFY COLUMN `condition` {CAR_CONDITION_ENUM} NULL")
            )

        foreign_keys = {key["name"] for key in inspector.get_foreign_keys("cars")}
        if "fk_cars_verified_by" not in foreign_keys:
            connection.execute(
                text(
                    "ALTER TABLE cars ADD CONSTRAINT fk_cars_verified_by "
                    "FOREIGN KEY (verified_by_id) REFERENCES users(id)"
                )
            )


if __name__ == "__main__":
    upgrade()
    print("Car Management migration completed.")
