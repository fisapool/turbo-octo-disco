"""
Main FastAPI Application

This module initializes and configures the FastAPI application with security features.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from typing import Dict, List
import logging
import os
from dotenv import load_dotenv
from .core.database import engine, Base
from .routes import auth, feedback
from datetime import datetime

from app.security.security_manager import SecurityManager
from app.middleware.security_middleware import SecurityMiddleware

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="HR Analytics API",
    description="API for HR analytics and monitoring",
    version="1.0.0"
)

# Initialize security components
security_manager = SecurityManager()
security_middleware = SecurityMiddleware(security_manager)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_manager.config["api_security"]["cors"]["allowed_origins"],
    allow_credentials=True,
    allow_methods=security_manager.config["api_security"]["cors"]["allowed_methods"],
    allow_headers=security_manager.config["api_security"]["cors"]["allowed_headers"]
)

# Add security middleware
app.middleware("http")(security_middleware)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Import and include routers
from app.routers import auth, users, analytics, monitoring

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(analytics.router)
app.include_router(monitoring.router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to HR Analytics API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/security/config")
@security_middleware.require_permission("read")
async def get_security_config(
    current_user: Dict = Depends(security_middleware.get_current_user)
):
    """Get security configuration (admin only)."""
    if "admin" not in current_user["roles"]:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return security_manager.config

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile="config/ssl/key.pem",
        ssl_certfile="config/ssl/cert.pem"
    ) 