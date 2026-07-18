from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class UserProfileOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserPlanOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    plan_type: str
    is_active: bool
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UpdatePlanRequest(BaseModel):
    plan_type: str  # "free" or "studio"
