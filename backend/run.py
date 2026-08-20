"""
Main Entry point for the SmartCarX App or Api 
Run the file to start the FastAPI server

usage:
    python run.py
    or 
    uvicorn run:app --reload
"""

import uvicorn
from app.main import app 


if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="127.0.0.1",
        port = 8000,
        reload=True,
        log_level="info"
    )