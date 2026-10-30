"""GaonBazaar database connection configuration.

Set DATABASE_URL in Render to a *separately provisioned and migrated* PostgreSQL
database. Existing SQLite data is NOT automatically transferred by this switch.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Dict, List

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
# Isolate preview data from committed and live databases when running in preview mode.
if os.getenv("GAONBAZAR_PREVIEW_MODE") == "1":
    _local_sqlite_url = "sqlite:////tmp/gaonbazar_staging_20261025.db"
else:
    _local_sqlite_url = f"sqlite:///{BASE_DIR / 'gaonbazar.db'}"
_supplied_url = (os.getenv("DATABASE_URL") or "").strip()
if _supplied_url.startswith("postgres://"):
    # Normalize legacy provider URLs for SQLAlchemy 2.x.
    DATABASE_URL = "postgresql://" + _supplied_url[len("postgres://"):]
else:
    DATABASE_URL = _supplied_url or _local_sqlite_url

if not DATABASE_URL.startswith(("sqlite:", "postgresql:")):
    raise RuntimeError("DATABASE_URL must be a PostgreSQL or SQLite SQLAlchemy URL")

IS_SQLITE = DATABASE_URL.startswith("sqlite:")
IS_POSTGRES = DATABASE_URL.startswith("postgresql:")
if os.getenv("GAONBAZAR_REQUIRE_POSTGRES") == "1" and not IS_POSTGRES:
    raise RuntimeError("GAONBAZAR_REQUIRE_POSTGRES=1, but PostgreSQL DATABASE_URL is missing")

if IS_SQLITE:
    # SQLite remains the zero-configuration local/test backend only.
    # Configured connection pool with generous limits and pre-ping to eliminate
    # "QueuePool limit of size 5 overflow 10 reached" during concurrent Playwright audits and background tasks.
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False, "timeout": 60.0},
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=40,
        pool_timeout=60,
        pool_recycle=1800,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()
else:
    # Persistent FastAPI service; pool configured for Supabase session pooler (5432) or direct PostgreSQL.
    # Generous pool sizing (10 pool + 15 overflow) prevents connection starvation under concurrent orders.
    # Secrets belong in Render environment variables, never client-side JS.
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=15,
        pool_recycle=1800,
        pool_timeout=30,
        connect_args={"connect_timeout": 15, "sslmode": "require"}
        if os.getenv("GAONBAZAR_DB_SSL", "require") == "require" else {"connect_timeout": 15},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

from contextlib import contextmanager

@contextmanager
def db_session():
    """
    Guaranteed session lifecycle context manager for background tasks, scripts, and startups:
    with db_session() as db:
        db.query(...)
    Guarantees session rollback on error and proper close() back to QueuePool upon exit.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database_integrity() -> bool:
    """
    Executes PRAGMA integrity_check on gaonbazar.db to ensure
    the SQLite database is intact and not corrupted before accepting orders.
    Returns True if healthy; raises RuntimeError if corruption is detected.
    """
    # Postgres has no SQLite PRAGMA. Validate that the configured DB responds.
    with engine.connect() as conn:
        if IS_POSTGRES:
            return conn.execute(text("SELECT 1")).scalar_one() == 1
        rows = [row[0] for row in conn.execute(text("PRAGMA integrity_check")).fetchall()]
        if rows != ["ok"]:
            raise RuntimeError("Database integrity check failed: " + "; ".join(rows))
        return True


def ensure_schema_migrations():
    """
    Safely adds any missing columns to existing SQLite tables
    (e.g. stores onboarding and KYC columns) without data loss.
    """
    # This legacy helper issues SQLite-only PRAGMAs/DDL.
    # PostgreSQL schema must be created/migrated using reviewed SQL migrations;
    # do not attempt automatic SQLite ALTER TABLE / financial backfills there.
    if IS_POSTGRES:
        return
    with engine.connect() as conn:
        # Ensure new tables (e.g. central_products) exist
        try:
            from .models import CentralProduct
            Base.metadata.create_all(bind=engine, tables=[CentralProduct.__table__])
        except Exception as e:
            print(f"Notice creating tables: {e}")

        # Check products columns for central product link & inventory
        res_prod = conn.execute(text("PRAGMA table_info(products)")).fetchall()
        existing_prod_cols = {r[1] for r in res_prod}
        prod_cols = [
            ("central_product_id", "VARCHAR(50)"),
            ("image_url", "TEXT"),
            ("stock_qty", "INTEGER DEFAULT 50"),
            ("is_available", "BOOLEAN DEFAULT 1")
        ]
        for col_name, col_type in prod_cols:
            if col_name not in existing_prod_cols:
                try:
                    conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    print(f"Notice adding column {col_name} to products: {e}")

        # Check stores columns
        res = conn.execute(text("PRAGMA table_info(stores)")).fetchall()
        existing_cols = {r[1] for r in res}

        new_cols = [
            ("store_type", "VARCHAR(50) DEFAULT 'kirana'"),
            ("status", "VARCHAR(30) DEFAULT 'approved'"),
            ("owner_name", "VARCHAR(100) DEFAULT 'Ramesh Sharma'"),
            ("id_type", "VARCHAR(20) DEFAULT 'Aadhar'"),
            ("id_number", "VARCHAR(50) DEFAULT 'XXXX-XXXX-8921'"),
            ("photo_url", "TEXT DEFAULT ''"),
            ("payout_upi", "VARCHAR(100) DEFAULT 'sharma.kirana@okaxis'"),
            ("bank_account_name", "VARCHAR(150)"),
            ("bank_account_number", "VARCHAR(50)"),
            ("bank_ifsc", "VARCHAR(20)"),
            ("bank_verification_status", "VARCHAR(20) DEFAULT 'pending'"),
            ("partner_code", "VARCHAR(50)"),
            ("village", "VARCHAR(100) DEFAULT 'Rampur'"),
            ("address", "TEXT"),
            ("emergency_contact", "VARCHAR(15)"),
            ("vehicle_reg_number", "VARCHAR(50)"),
            ("driving_licence_number", "VARCHAR(50)"),
            ("driving_licence_url", "TEXT"),
            ("kyc_status", "VARCHAR(30) DEFAULT 'approved'"),
            ("kyc_document_type", "VARCHAR(50) DEFAULT 'Aadhaar'"),
            ("kyc_document_number", "VARCHAR(100) DEFAULT 'XXXX-XXXX-4821'"),
            ("kyc_document_url", "TEXT"),
            ("kyc_rejection_reason", "TEXT"),
            ("kyc_submitted_at", "DATETIME"),
            ("kyc_reviewed_at", "DATETIME"),
            ("is_verified", "BOOLEAN DEFAULT 1"),
            ("primary_village", "VARCHAR(100) DEFAULT 'Rampur'"),
            ("service_radius_km", "FLOAT DEFAULT 5.0"),
            ("theme_preference", "VARCHAR(20) DEFAULT 'system'"),
            ("lang_preference", "VARCHAR(10) DEFAULT 'hi'"),
            ("lat", "FLOAT DEFAULT 29.1350"),
            ("lng", "FLOAT DEFAULT 77.0100"),
            ("created_at", "DATETIME"),
            ("store_code", "VARCHAR(50)"),
            ("village", "VARCHAR(100) DEFAULT 'Rampur'"),
            ("address", "TEXT"),
            ("landmark", "VARCHAR(150)"),
            ("pickup_location", "VARCHAR(150)"),
            ("opening_time", "VARCHAR(20) DEFAULT '07:00 AM'"),
            ("closing_time", "VARCHAR(20) DEFAULT '09:00 PM'"),
            ("weekly_schedule", "VARCHAR(50) DEFAULT 'All Days'"),
            ("kyc_status", "VARCHAR(30) DEFAULT 'approved'"),
            ("kyc_document_type", "VARCHAR(50) DEFAULT 'Aadhaar'"),
            ("kyc_document_number", "VARCHAR(100) DEFAULT 'XXXX-XXXX-8921'"),
            ("kyc_document_url", "TEXT"),
            ("kyc_rejection_reason", "TEXT"),
            ("kyc_submitted_at", "DATETIME"),
            ("kyc_reviewed_at", "DATETIME"),
            ("is_verified", "BOOLEAN DEFAULT 1"),
            ("theme_preference", "VARCHAR(20) DEFAULT 'system'"),
            ("lang_preference", "VARCHAR(10) DEFAULT 'hi'"),
        ]

        for col_name, col_type in new_cols:
            if col_name not in existing_cols:
                try:
                    conn.execute(text(f"ALTER TABLE stores ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    print(f"Notice adding column {col_name}: {e}")

        # Check runners columns for bank & payout onboarding
        res_runners = conn.execute(text("PRAGMA table_info(runners)")).fetchall()
        existing_runner_cols = {r[1] for r in res_runners}
        runner_cols = [
            ("bank_account_name", "VARCHAR(150)"),
            ("bank_account_number", "VARCHAR(50)"),
            ("bank_ifsc", "VARCHAR(20)"),
            ("bank_verification_status", "VARCHAR(20) DEFAULT 'pending'"),
            ("partner_code", "VARCHAR(50)"),
            ("village", "VARCHAR(100) DEFAULT 'Rampur'"),
            ("address", "TEXT"),
            ("emergency_contact", "VARCHAR(15)"),
            ("vehicle_reg_number", "VARCHAR(50)"),
            ("driving_licence_number", "VARCHAR(50)"),
            ("driving_licence_url", "TEXT"),
            ("kyc_status", "VARCHAR(30) DEFAULT 'approved'"),
            ("kyc_document_type", "VARCHAR(50) DEFAULT 'Aadhaar'"),
            ("kyc_document_number", "VARCHAR(100) DEFAULT 'XXXX-XXXX-4821'"),
            ("kyc_document_url", "TEXT"),
            ("kyc_rejection_reason", "TEXT"),
            ("kyc_submitted_at", "DATETIME"),
            ("kyc_reviewed_at", "DATETIME"),
            ("is_verified", "BOOLEAN DEFAULT 1"),
            ("primary_village", "VARCHAR(100) DEFAULT 'Rampur'"),
            ("service_radius_km", "FLOAT DEFAULT 5.0"),
            ("theme_preference", "VARCHAR(20) DEFAULT 'system'"),
            ("lang_preference", "VARCHAR(10) DEFAULT 'hi'"),
        ]
        for col_name, col_type in runner_cols:
            if col_name not in existing_runner_cols:
                try:
                    conn.execute(text(f"ALTER TABLE runners ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    print(f"Notice adding column {col_name} to runners: {e}")

        # Check orders columns for split-payment & dynamic revenue fields
        res_orders = conn.execute(text("PRAGMA table_info(orders)")).fetchall()
        existing_order_cols = {r[1] for r in res_orders}
        order_cols = [
            ("vendor_payout", "FLOAT DEFAULT 0.0"),
            ("runner_payout", "FLOAT DEFAULT 0.0"),
            ("admin_profit", "FLOAT DEFAULT 13.0"),
            ("distance_km", "FLOAT DEFAULT 1.5"),
            ("eta_mins", "VARCHAR(50) DEFAULT '30 Mins'"),
            ("refund_amount", "FLOAT DEFAULT 0.0"),
            ("refund_penalty", "FLOAT DEFAULT 0.0"),
            ("cancellation_reason", "VARCHAR(255)"),
            ("delivery_discount", "FLOAT DEFAULT 0.0"),
            ("base_delivery_fee", "FLOAT DEFAULT 0.0"),
            ("payment_status", "VARCHAR(30) DEFAULT 'PENDING'"),
            ("razorpay_order_id", "VARCHAR(100)"),
            ("razorpay_payment_id", "VARCHAR(100)"),
            ("razorpay_signature", "VARCHAR(255)"),
            ("split_payout_status", "VARCHAR(30) DEFAULT 'unprocessed'"),
            ("paid_at", "DATETIME"),
            ("customer_lat", "FLOAT"),
            ("customer_lng", "FLOAT"),
            ("runner_id", "VARCHAR(50)"),
            ("distance_type", "VARCHAR(50) DEFAULT 'road_routing_estimate'"),
            ("vendor_transfer_id", "VARCHAR(100)"),
            ("runner_transfer_id", "VARCHAR(100)"),
            ("district", "VARCHAR(100) DEFAULT 'Muzaffarpur'"),
            ("block", "VARCHAR(100) DEFAULT 'Minapur'")
        ]
        for col_name, col_type in order_cols:
            if col_name not in existing_order_cols:
                try:
                    conn.execute(text(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    print(f"Notice adding column {col_name} to orders: {e}")

        
        # Check payment_transactions columns
        res_pt = conn.execute(text("PRAGMA table_info(payment_transactions)")).fetchall()
        existing_pt_cols = {r[1] for r in res_pt}
        pt_cols = [
            ("vendor_transfer_id", "VARCHAR(100)"),
            ("runner_transfer_id", "VARCHAR(100)"),
            ("settlement_id", "VARCHAR(100)"),
            ("settled_at", "DATETIME"),
            ("failure_reason", "TEXT")
        ]
        for col_name, col_type in pt_cols:
            if col_name not in existing_pt_cols:
                try:
                    conn.execute(text(f"ALTER TABLE payment_transactions ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    print(f"Notice adding column {col_name} to payment_transactions: {e}")

        # Check users columns for 3-strike customer trust score
        res_users = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        existing_user_cols = {r[1] for r in res_users}
        user_cols = [
            ("consecutive_cancellations", "INTEGER DEFAULT 0"),
            ("cancelled_orders", "INTEGER DEFAULT 0"),
            ("is_cod_blocked", "BOOLEAN DEFAULT 0"),
            ("is_blacklisted", "BOOLEAN DEFAULT 0"),
            ("warning_alert", "VARCHAR(255)"),
            ("trust_score", "INTEGER DEFAULT 100")
        ]
        for col_name, col_type in user_cols:
            if col_name not in existing_user_cols:
                try:
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    print(f"Notice adding column {col_name} to users: {e}")

        # Check landmarks columns for open text address (district)
        res_landmarks = conn.execute(text("PRAGMA table_info(landmarks)")).fetchall()
        existing_landmark_cols = {r[1] for r in res_landmarks}
        if "district" not in existing_landmark_cols:
            try:
                conn.execute(text("ALTER TABLE landmarks ADD COLUMN district VARCHAR(100) DEFAULT 'Muzaffarpur'"))
                conn.commit()
            except Exception as e:
                print(f"Notice adding column district to landmarks: {e}")
        if "block" not in existing_landmark_cols:
            try:
                conn.execute(text("ALTER TABLE landmarks ADD COLUMN block VARCHAR(100) DEFAULT 'Minapur'"))
                conn.commit()
            except Exception as e:
                print(f"Notice adding column block to landmarks: {e}")

        # Check otp_records columns for attempts counter
        res_otp = conn.execute(text("PRAGMA table_info(otp_records)")).fetchall()
        existing_otp_cols = {r[1] for r in res_otp}
        if "attempts" not in existing_otp_cols:
            try:
                conn.execute(text("ALTER TABLE otp_records ADD COLUMN attempts INTEGER DEFAULT 0"))
                conn.commit()
            except Exception as e:
                print(f"Notice adding column attempts to otp_records: {e}")

        # Ensure audit_logs table exists
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action VARCHAR(100) NOT NULL,
                    actor_role VARCHAR(50) NOT NULL,
                    actor_id VARCHAR(100),
                    target_entity VARCHAR(50),
                    target_id VARCHAR(100),
                    details TEXT,
                    ip_address VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        except Exception as e:
            print(f"Notice creating audit_logs table: {e}")

        # Ensure support_tickets table exists
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id VARCHAR(50) NOT NULL,
                    user_phone VARCHAR(15) NOT NULL,
                    order_id VARCHAR(50),
                    category VARCHAR(50) DEFAULT 'general',
                    message TEXT NOT NULL,
                    status VARCHAR(20) DEFAULT 'open',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        except Exception as e:
            print(f"Notice creating support_tickets table: {e}")

        # Ensure store_categories table exists
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS store_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_type VARCHAR(50) NOT NULL,
                    category_id VARCHAR(50) NOT NULL,
                    name_en VARCHAR(100) NOT NULL,
                    name_hi VARCHAR(100) NOT NULL,
                    icon VARCHAR(50) DEFAULT 'category'
                )
            """))
            conn.commit()
        except Exception as e:
            print(f"Notice creating store_categories table: {e}")

        # Ensure saved_payment_methods table exists
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS saved_payment_methods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_phone VARCHAR(15) NOT NULL,
                    method_type VARCHAR(20) NOT NULL,
                    title VARCHAR(100) NOT NULL,
                    vpa_or_card VARCHAR(100) NOT NULL,
                    is_default BOOLEAN DEFAULT 0,
                    token_id VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        except Exception as e:
            print(f"Notice creating saved_payment_methods table: {e}")

        # Ensure payment_transactions table exists
        try:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payment_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id VARCHAR(50) NOT NULL,
                    razorpay_order_id VARCHAR(100),
                    razorpay_payment_id VARCHAR(100),
                    amount FLOAT NOT NULL,
                    amount_in_paise INTEGER NOT NULL,
                    currency VARCHAR(10) DEFAULT 'INR',
                    status VARCHAR(30) DEFAULT 'created',
                    payment_mode VARCHAR(30) DEFAULT 'ONLINE',
                    signature VARCHAR(255),
                    verified BOOLEAN DEFAULT 0,
                    verified_at DATETIME,
                    raw_payload TEXT,
                    vendor_split_amount FLOAT DEFAULT 0.0,
                    runner_split_amount FLOAT DEFAULT 0.0,
                    admin_platform_fee FLOAT DEFAULT 3.0,
                    admin_margin FLOAT DEFAULT 0.0,
                    route_transfer_status VARCHAR(30) DEFAULT 'prepared',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        except Exception as e:
            print(f"Notice creating payment_transactions table: {e}")

        # Ensure all existing orders have balanced distance-based ledger splits
        try:
            orders_to_backfill = conn.execute(text(
                "SELECT id, subtotal, distance_km, vendor_payout, runner_payout, admin_profit, total_amount FROM orders"
            )).fetchall()
            for row in orders_to_backfill:
                oid = row[0]
                sub = float(row[1] or 0.0)
                dist = float(row[2] or 1.2)
                vp = row[3]
                rp = row[4]
                ap = row[5]
                tot = float(row[6] or 0.0)
                
                # Check if recalculation needed
                if vp is None or rp is None or ap is None or abs((float(vp or 0) + float(rp or 0) + float(ap or 0)) - tot) > 0.01:
                    if dist > 5.0:
                        del_fee = 40.0
                        r_payout = 30.0
                        a_profit = 13.0
                        eta = "45-60 Mins"
                    elif dist > 2.0:
                        del_fee = 25.0
                        r_payout = 15.0
                        a_profit = 13.0
                        eta = "30 Mins"
                    else:
                        del_fee = 15.0
                        r_payout = 10.0
                        a_profit = 8.0
                        eta = "30 Mins"
                    
                    v_payout = sub
                    correct_total = round(sub + del_fee + 3.0, 2)
                    conn.execute(text("""
                        UPDATE orders SET
                            vendor_payout = :vp,
                            runner_payout = :rp,
                            admin_profit = :ap,
                            delivery_fee = :df,
                            platform_fee = 3.0,
                            total_amount = :tot,
                            distance_km = :dist,
                            eta_mins = :eta
                        WHERE id = :oid
                    """), {
                        "vp": v_payout,
                        "rp": r_payout,
                        "ap": a_profit,
                        "df": del_fee,
                        "tot": correct_total,
                        "dist": dist,
                        "eta": eta,
                        "oid": oid
                    })
            conn.commit()
        except Exception as bfe:
            print(f"Notice backfilling order splits: {bfe}")

        # Ensure all existing stores have a unique permanent Store ID (e.g. GB-S000001)
        try:
            stores = conn.execute(text("SELECT id, store_code FROM stores ORDER BY rowid")).fetchall()
            for idx, row in enumerate(stores, start=1):
                s_id, s_code = row[0], row[1]
                if not s_code:
                    code = f"GB-S{idx:06d}"
                    conn.execute(text("UPDATE stores SET store_code = :c WHERE id = :id"), {"c": code, "id": s_id})
            conn.commit()
        except Exception as se:
            print(f"Notice backfilling store codes: {se}")

        # Ensure all existing delivery partners have a unique permanent Partner ID (e.g. GB-DP000001)
        try:
            runners = conn.execute(text("SELECT id, partner_code FROM runners ORDER BY rowid")).fetchall()
            for idx, row in enumerate(runners, start=1):
                r_id, r_code = row[0], row[1]
                if not r_code:
                    code = f"GB-DP{idx:06d}"
                    conn.execute(text("UPDATE runners SET partner_code = :c WHERE id = :id"), {"c": code, "id": r_id})
            conn.commit()
        except Exception as re_err:
            print(f"Notice backfilling runner partner codes: {re_err}")

def record_audit_log(
    db,
    action: str,
    actor_role: str,
    actor_id: Optional[str] = None,
    target_entity: Optional[str] = None,
    target_id: Optional[str] = None,
    details: Any = None,
    ip_address: Optional[str] = None
):
    """
    Records an auditable event in the audit_logs table.
    Ensures end-to-end traceability for privileged admin decisions, KYC changes, and financial transfers.
    """
    try:
        from .models import AuditLog
        details_str = json.dumps(details, default=str) if isinstance(details, (dict, list)) else (str(details) if details else None)
        entry = AuditLog(
            action=action,
            actor_role=actor_role,
            actor_id=str(actor_id) if actor_id else None,
            target_entity=target_entity,
            target_id=str(target_id) if target_id else None,
            details=details_str,
            ip_address=ip_address,
            created_at=datetime.utcnow()
        )
        db.add(entry)
        db.commit()
    except Exception as e:
        print(f"Notice recording audit log: {e}")

