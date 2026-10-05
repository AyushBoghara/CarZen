"""
Main Entry point for the CarZen App or Api 
Run the file to start the FastAPI server

usage:
    python run.py
    or 
    uvicorn run:app --reload
"""

import sys
from pathlib import Path
import uvicorn

# Ensure the backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.connection.conn import Base, engine
from app import models
from app.main import app 

if __name__ == "__main__":
    print("Ensuring all database tables exist in MySQL...")
    Base.metadata.create_all(bind=engine)
    print("Database tables verified.")

    uvicorn.run(
        "run:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        app_dir=str(backend_dir)
    )