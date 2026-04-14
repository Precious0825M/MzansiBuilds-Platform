from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CommentInfo(BaseModel):
    com_id: int
    content: str
    user_id: int
    author_name: str
    created_at: datetime


class CollaboratorInfo(BaseModel):
    user_id: int
    name: str


class CelebrationResponse(BaseModel):
    proj_id: int
    title: str
    description: str | None
    updated_at: datetime
    user_id: int
    name: str
    total_updates: int
    comments: list[CommentInfo] = []
    collaborators: list[CollaboratorInfo] = []

    class Config:
        from_attributes = True