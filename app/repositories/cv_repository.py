from sqlalchemy.orm import Session, joinedload
from app.repositories.base_repository import BaseRepository
from app.models.cv_model import CV, CVDetails
from uuid import UUID


class CVRepository(BaseRepository[CV]):
    def __init__(self, db: Session):
        super().__init__(db, CV)

    def get_by_user_id(self, user_id: UUID):
        return self.db.query(CV).filter(
            CV.user_id == user_id
        ).options(joinedload(CV.details)).first()

    def delete_by_user_id(self, user_id: UUID):
        cv = self.get_by_user_id(user_id)
        if cv:
            self.delete(cv)
        return cv


class CVDetailsRepository(BaseRepository[CVDetails]):
    def __init__(self, db: Session):
        super().__init__(db, CVDetails)

    def get_by_cv_id(self, cv_id: UUID):
        return self.db.query(CVDetails).filter(
            CVDetails.cv_id == cv_id
        ).first()

    def update_details(self, cv_id: UUID, parsed: dict):
        details = self.get_by_cv_id(cv_id)
        if details:
            details.summary = parsed.get("summary")
            details.title = parsed.get("title")
            details.education = parsed.get("education")
            details.experience = parsed.get("experience")
            details.technical_skills = parsed.get("technical_skills")
            return self.update(details)
        return None