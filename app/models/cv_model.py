from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.clients.database_clients import Base


class CV(Base):
    __tablename__ = "cvs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    details = relationship("CVDetails", back_populates="cv", uselist=False, cascade="all, delete-orphan")


class CVDetails(Base):
    __tablename__ = "cv_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)
    cv_id = Column(UUID(as_uuid=True), ForeignKey("cvs.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary = Column(Text, nullable=True)
    title = Column(String, nullable=True)
    education = Column(JSONB, nullable=True)
    experience = Column(JSONB, nullable=True)
    technical_skills = Column(ARRAY(String), nullable=True)

    cv = relationship("CV", back_populates="details")