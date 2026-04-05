from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CommentCreate(BaseModel):
    update_id: int
    content: str


class CommentResponse(BaseModel):
    com_id: int
    update_id: int
    user_id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True