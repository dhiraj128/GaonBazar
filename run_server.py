"""
GaonBazaar Local Server Launcher
Starts the FastAPI backend with SQLite database support.
Usage:
    python run_server.py [port] [--no-reload]
Default port is 8001 (to prevent collision with other local services on 8000).
"""

import os
import sys
import uvicorn

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    no_reload = "--no-reload" in sys.argv or os.getenv("CI") is not None or os.getenv("TEST_MODE") is not None
    port = int(args[0]) if len(args) > 0 else 8001
    print(f"===========================================================")
    print(f"  GaonBazaar Hyperlocal Rural Delivery - Backend API       ")
    print(f"  Host: http://127.0.0.1:{port}                            ")
    print(f"  Interactive Docs: http://127.0.0.1:{port}/docs           ")
    print(f"  Database: backend/gaonbazar.db (SQLite)                  ")
    print(f"  Reload Mode: {'Disabled' if no_reload else 'Enabled'}    ")
    print(f"===========================================================")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=port, reload=not no_reload)
