from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional, Any


class EducationItem(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None


class ExperienceItem(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None


class CVDetailsResponse(BaseModel):
    id: UUID
    summary: Optional[str] = None
    title: Optional[str] = None
    education: Optional[List[EducationItem]] = None
    experience: Optional[List[ExperienceItem]] = None
    technical_skills: Optional[List[str]] = None

    class Config:
        from_attributes = True


class CVResponse(BaseModel):
    id: UUID
    user_id: UUID
    file_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    details: Optional[CVDetailsResponse] = None
    processing_time_ms: Optional[float] = None

    class Config:
        from_attributes = True