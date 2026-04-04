from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

# Use PBKDF2 instead of bcrypt due to Windows compatibility issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def hash_password(password: str) -> str:
    """Hash the password using PBKDF2 with SHA-256."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """create token for user authentication."""
    to_encode = data.copy()
    if "user_id" in to_encode and "sub" not in to_encode:
        to_encode["sub"] = str(to_encode["user_id"])

    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))