from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import Literal


class CollaborationCreate(BaseModel):
    project_id: int
    message: Optional[str] = None


class CollaborationUpdate(BaseModel):
    status: Literal["Accepted", "Rejected"]


class CollaborationResponse(BaseModel):
    collab_id: int
    project_id: int
    user_id: int
    message: Optional[str]
    status: str
    created_at: datetime
    title: Optional[str] = None

    class Config:
        from_attributes = True