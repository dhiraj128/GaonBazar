from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Database path: backend/gaonbazar.db
BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'gaonbazar.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30.0}
)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()

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
            ("lat", "FLOAT DEFAULT 29.1350"),
            ("lng", "FLOAT DEFAULT 77.0100"),
            ("created_at", "DATETIME")
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
            ("bank_verification_status", "VARCHAR(20) DEFAULT 'pending'")
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
            ("paid_at", "DATETIME")
        ]
        for col_name, col_type in order_cols:
            if col_name not in existing_order_cols:
                try:
                    conn.execute(text(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                except Exception as e:
                    print(f"Notice adding column {col_name} to orders: {e}")

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
                conn.execute(text("ALTER TABLE landmarks ADD COLUMN district VARCHAR(100)"))
                conn.commit()
            except Exception as e:
                print(f"Notice adding column district to landmarks: {e}")

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


