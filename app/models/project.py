from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from app.db import Base

class MLType(str, enum.Enum):
    supervised = "supervised"
    unsupervised = "unsupervised"
    reinforcement = "reinforcement"
    ann = "ann"

class StudioProject(Base):
    __tablename__ = "studio_projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_name = Column(String)
    dataset_filename = Column(String)
    ml_type = Column(SQLEnum(MLType))
    algorithm = Column(String)
    prompt = Column(Text)
    status = Column(Boolean, default=False)
    results = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    generated_code = relationship("GeneratedCode", back_populates="project", cascade="all, delete-orphan")

class GeneratedCode(Base):
    __tablename__ = "generated_code"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("studio_projects.id", ondelete="CASCADE"), nullable=False)
    generated_code = Column(Text)
    execution_results = Column(JSONB)
    plots_data = Column(JSONB)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("StudioProject", back_populates="generated_code")
