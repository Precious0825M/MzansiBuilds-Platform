from pydantic import BaseModel
from datetime import datetime


class CelebrationResponse(BaseModel):
    proj_id: int
    title: str
    description: str | None
    updated_at: datetime
    user_id: int
    name: str

    class Config:
        from_attributes = True