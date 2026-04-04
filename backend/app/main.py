"""
MzansiBuilds API Application
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
import os
from app.db.database import DatabaseConfig
from app.schemas.user import UserCreate, UserRegisterResponse, UserLogin, UserUpdate, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.dependencies import get_current_user
from typing import Dict

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


# ============================================================================
# User Authentication and Profile Endpoints
# ============================================================================

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

    # Hash the password using PBKDF2 with SHA-256
    hashed_password = hash_password(user_data.password)

    # Insert new user
    success = db.execute_update(
        """
        INSERT INTO users (name, email, password_hash, bio)
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
    

@app.post("/api/auth/login")
async def login_user(user_data: UserLogin):
    """login user"""
    # Fetch user by email
    user = db.execute_query(
        "SELECT user_id, name, email, password_hash FROM users WHERE email = %s",
        (user_data.email,)
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = user[0]  # since execute_query returns list of dicts
    
    # Verify password
    if not verify_password(user_data.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(
        data={"user_id": user["user_id"]}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get the current authenticated user's profile."""
    return current_user

