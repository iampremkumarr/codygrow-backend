from sqlalchemy import Column, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from app.db import Base

class PlanType(str, enum.Enum):
    free = "free"
    studio = "studio"
    pro = "pro"
    premium = "premium"

class UserPlan(Base):
    __tablename__ = "user_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    plan_type = Column(SQLEnum(PlanType), default=PlanType.free)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="plans")
