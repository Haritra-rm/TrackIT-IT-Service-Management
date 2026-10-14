from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CommentCreate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    user_id: int
    comment: str
    created_at: datetime
    user_name: Optional[str] = None
    user_role: Optional[str] = None
