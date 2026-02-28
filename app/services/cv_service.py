import time
from uuid import UUID
from app.repositories.cv_repository import CVRepository, CVDetailsRepository
from app.models.cv_model import CV, CVDetails
from app.utils.cv_parser import extract_text_from_pdf, parse_cv_with_llm
from app.clients.storage_clients.storage_base_client import BaseStorageClient
from app.core.exceptions import NotFoundException


class CVService:
    def __init__(
        self,
        cv_repo: CVRepository,
        cv_details_repo: CVDetailsRepository,
        storage: BaseStorageClient,
    ):
        self.cv_repo = cv_repo
        self.cv_details_repo = cv_details_repo
        self.storage = storage

    def upload_and_parse(self, file_bytes: bytes, filename: str, user_id: UUID):
        start = time.time()

        cv_text = extract_text_from_pdf(file_bytes)
        parsed = parse_cv_with_llm(cv_text)

        existing_cv = self.cv_repo.get_by_user_id(user_id)

        if existing_cv:
            self.storage.upload_cv_and_get_path(user_id, file_bytes, filename)
            self.cv_details_repo.update_details(existing_cv.id, parsed)
            cv = self.cv_repo.get_by_user_id(user_id)
        else:
            self.storage.upload_cv_and_get_path(user_id, file_bytes, filename)
            cv = CV(user_id=user_id)
            cv = self.cv_repo.create(cv)
            details = CVDetails(
                cv_id=cv.id,
                summary=parsed.get("summary"),
                title=parsed.get("title"),
                education=parsed.get("education"),
                experience=parsed.get("experience"),
                technical_skills=parsed.get("technical_skills"),
            )
            self.cv_details_repo.create(details)
            cv = self.cv_repo.get_by_user_id(user_id)

        processing_time_ms = (time.time() - start) * 1000
        file_url = self.storage.get_cv_signed_url(user_id)
        return cv, file_url, processing_time_ms

    def get_cv(self, user_id: UUID):
        cv = self.cv_repo.get_by_user_id(user_id)
        if not cv:
            raise NotFoundException("CV not found")
        file_url = self.storage.get_cv_signed_url(user_id)
        return cv, file_url

    def delete_cv(self, user_id: UUID):
        cv = self.cv_repo.get_by_user_id(user_id)
        if not cv:
            raise NotFoundException("CV not found")
        self.storage.delete_cv(user_id)
        self.cv_repo.delete(cv)