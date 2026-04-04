from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os

from app.db.database import get_db_connection

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db_connection)
):
    """Dependency to get the current authenticated user from the JWT token."""
    token = credentials.credentials

    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id = payload.get("sub") or payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT user_id, name, email, bio, created_at FROM users WHERE user_id = %s AND is_deleted = 0",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user