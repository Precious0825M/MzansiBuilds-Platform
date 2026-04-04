"""
MzansiBuilds API Application
"""

from fastapi import FastAPI, HTTPException
import hmac
import hashlib
import os

from app.db.database import DatabaseConfig
from app.schemas.user import UserCreate, UserRegisterResponse

app = FastAPI(title="MzansiBuilds API", version="1.0.0")

db = DatabaseConfig()

@app.on_event("startup")
async def startup_event():
    """Initialize database schema on startup."""
    db.create_database_schema()

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Check API and database health."""
    db = DatabaseConfig()
    try:
        # Simple query to check database connectivity
        result = db.execute_query("SELECT 1 as health_check")
        if result and result[0].get('health_check') == 1:
            return {"status": "ok", "database": "connected"}
        else:
            return {"status": "error", "database": "query_failed"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "error": str(e)}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "MzansiBuilds API is running"}


def hash_password(password: str) -> str:
    """Hash password using HS256 (HMAC SHA-256) with SECRET_KEY."""
    secret_key = os.getenv('SECRET_KEY', 'default_secret')
    return hmac.new(
        secret_key.encode('utf-8'),
        password.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


@app.post("/api/auth/register", response_model=UserRegisterResponse)
async def register_user(user_data: UserCreate):
    """Register a new user with hashed password."""
    # Check if email already exists
    existing_user = db.execute_query(
        "SELECT user_id FROM users WHERE email = %s",
        (user_data.email,)
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password using HS256
    hashed_password = hash_password(user_data.password)

    # Insert new user
    success = db.execute_update(
        """
        INSERT INTO users (name, email, password, bio)
        VALUES (%s, %s, %s, %s)
        """,
        (user_data.name, user_data.email, hashed_password, user_data.bio)
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to create user")

    # Get the new user ID
    user_id = db.get_last_insert_id()
    if user_id is None:
        raise HTTPException(status_code=500, detail="Failed to retrieve user ID")

    return UserRegisterResponse(
        message="User registered successfully",
        user_id=user_id
    )