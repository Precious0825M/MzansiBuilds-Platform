from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    stage: Optional[str] = "Planning"
    support_needed: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[str] = None
    support_needed: Optional[str] = None


class ProjectResponse(BaseModel):
    proj_id: int
    user_id: int
    title: str
    description: Optional[str]
    stage: str
    support_needed: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True