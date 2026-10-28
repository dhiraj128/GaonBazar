"""Safe database-selection regression checks. No remote credentials required."""
import os
import subprocess
import sys

def run_with(env_updates, snippet):
    env = os.environ.copy()
    env.pop("DATABASE_URL", None)
    env.pop("GAONBAZAR_REQUIRE_POSTGRES", None)
    env.update(env_updates)
    return subprocess.run([sys.executable, "-c", snippet], env=env, text=True, capture_output=True)

def test_local_sqlite_remains_supported():
    out = run_with({}, "from backend.database import IS_SQLITE, IS_POSTGRES; assert IS_SQLITE and not IS_POSTGRES")
    assert out.returncode == 0, out.stderr

def test_prod_guard_rejects_missing_url():
    out = run_with({"GAONBAZAR_REQUIRE_POSTGRES": "1"}, "from backend import database")
    assert out.returncode != 0
    assert "DATABASE_URL is missing" in out.stderr

def test_rejects_unknown_database_scheme():
    out = run_with({"DATABASE_URL": "mysql://localhost/fake"}, "from backend import database")
    assert out.returncode != 0
    assert "PostgreSQL or SQLite" in out.stderr

def test_postgres_url_detection_without_connection():
    # Engine instantiation doesn't connect; no Supabase credentials necessary.
    out = run_with(
        {"DATABASE_URL": "postgres://demo:demo@localhost:5432/demo"},
        "from backend.database import DATABASE_URL, IS_POSTGRES; assert IS_POSTGRES and DATABASE_URL.startswith('postgresql://')",
    )
    assert out.returncode == 0, out.stderr

if __name__ == "__main__":
    test_local_sqlite_remains_supported()
    test_prod_guard_rejects_missing_url()
    test_rejects_unknown_database_scheme()
    test_postgres_url_detection_without_connection()
    print("4 database configuration checks passed")
