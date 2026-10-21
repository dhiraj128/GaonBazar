from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Database path: backend/gaonbazar.db
BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'gaonbazar.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_integrity() -> bool:
    """
    Executes PRAGMA integrity_check on gaonbazar.db to ensure
    the SQLite database is intact and not corrupted before accepting orders.
    Returns True if healthy; raises RuntimeError if corruption is detected.
    """
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA integrity_check")).fetchall()
        rows = [row[0] for row in result]
        if rows == ["ok"]:
            return True
        else:
            error_details = "; ".join(rows)
            raise RuntimeError(f"Database integrity check failed: {error_details}")


def ensure_schema_migrations():
    """
    Safely adds any missing columns to existing SQLite tables
    (e.g. stores onboarding and KYC columns) without data loss.
    """
    from sqlalchemy import text
    with engine.connect() as conn:
        # Check stores columns
        res = conn.execute(text("PRAGMA table_info(stores)")).fetchall()
        existing_cols = {r[1] for r in res}

        new_cols = [
            ("status", "VARCHAR(30) DEFAULT 'approved'"),
            ("owner_name", "VARCHAR(100) DEFAULT 'Ramesh Sharma'"),
            ("id_type", "VARCHAR(20) DEFAULT 'Aadhar'"),
            ("id_number", "VARCHAR(50) DEFAULT 'XXXX-XXXX-8921'"),
            ("photo_url", "TEXT DEFAULT ''"),
            ("payout_upi", "VARCHAR(100) DEFAULT 'sharma.kirana@okaxis'"),
            ("created_at", "DATETIME")
        ]

        for col_name, col_type in new_cols:
            if col_name not in existing_cols:
                try:
                    conn.execute(text(f"ALTER TABLE stores ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    print(f"Notice adding column {col_name}: {e}")


