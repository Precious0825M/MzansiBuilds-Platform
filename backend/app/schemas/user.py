from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Request model for Register
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    bio: Optional[str] = None

# Response model for Register
class UserRegisterResponse(BaseModel):
    message: str
    user_id: int

# Response model for Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Response model for Update user profile
class UserUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None


# Response (API return) model for User
class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    bio: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True



