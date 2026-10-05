"""
Database initialization script for CarZen.
Usage:
    python backend/init_db.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import pymysql

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Load .env
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

DB_USER = os.getenv("DATABASE_USER", "root")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD", "")
DB_HOST = os.getenv("DATABASE_HOST", "localhost")
DB_PORT = int(os.getenv("DATABASE_PORT", "3306"))
DB_NAME = os.getenv("DATABASE_NAME", "carzen_db")


def create_database_if_not_exists():
    print(f"Connecting to MySQL server at {DB_HOST}:{DB_PORT} as '{DB_USER}'...")
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        autocommit=True,
    )
    with conn.cursor() as cursor:
        print(f"Ensuring database '{DB_NAME}' exists...")
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
    conn.close()
    print(f"Database '{DB_NAME}' verified.")


def create_all_tables():
    from app.database.connection.conn import Base, engine
    from app import models
    from sqlalchemy import inspect

    print(f"Creating all ORM tables for database '{DB_NAME}'...")
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Successfully created/verified {len(tables)} tables:")
    for idx, table in enumerate(tables, start=1):
        print(f"  {idx}. {table}")


def stamp_alembic_head():
    try:
        from alembic.config import Config
        from alembic import command

        alembic_ini_path = backend_dir / "alembic.ini"
        if alembic_ini_path.exists():
            print("Stamping Alembic migrations to head...")
            alembic_cfg = Config(str(alembic_ini_path))
            alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))
            command.stamp(alembic_cfg, "head")
            print("Alembic migrations stamped to head successfully.")
    except Exception as e:
        print(f"Note: Could not stamp alembic (optional): {e}")


def main():
    print("=" * 60)
    print(" CarZen Database Initialization")
    print("=" * 60)
    create_database_if_not_exists()
    create_all_tables()
    stamp_alembic_head()
    print("=" * 60)
    print(" Database setup completed successfully! You can now run:")
    print("   python backend/run.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
