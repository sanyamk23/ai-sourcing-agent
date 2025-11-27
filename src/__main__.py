"""
Main entry point for running the API server
Usage: python -m src
"""
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    workers = int(os.getenv("API_WORKERS", 1))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    uvicorn.run(
        "src.api_server:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        reload=False
    )
