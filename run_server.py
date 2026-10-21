"""
GaonBazaar Local Server Launcher
Starts the FastAPI backend with SQLite database support.
Usage:
    python run_server.py [port]
Default port is 8001 (to prevent collision with other local services on 8000).
"""

import sys
import uvicorn

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    print(f"===========================================================")
    print(f"  GaonBazaar Hyperlocal Rural Delivery - Backend API       ")
    print(f"  Host: http://127.0.0.1:{port}                            ")
    print(f"  Interactive Docs: http://127.0.0.1:{port}/docs           ")
    print(f"  Database: backend/gaonbazar.db (SQLite)                  ")
    print(f"===========================================================")
    uvicorn.run("backend.main:app", host="127.0.0.1", port=port, reload=True)
