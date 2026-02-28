from abc import ABC, abstractmethod


class BaseStorageClient(ABC):
    """Abstract base class for storage clients."""

    @abstractmethod
    def upload_pdf_and_get_signed_url(
        self, user_id, chat_id, file_bytes: bytes, original_name: str
    ) -> str:
        """Upload a PDF and return a signed URL."""
        pass

    @abstractmethod
    def upload_image_and_get_signed_url(
        self, user_id, file_id, file_bytes: bytes, original_name: str
    ) -> str:
        """Upload an image and return a signed URL."""
        pass

    @abstractmethod
    def upload_cv_and_get_path(
        self, user_id, file_bytes: bytes, original_name: str
    ) -> str:
        """Upload a CV file and return the storage path."""
        pass

    @abstractmethod
    def get_cv_signed_url(self, user_id) -> str:
        """Return a signed URL for the user's CV."""
        pass

    @abstractmethod
    def delete_cv(self, user_id) -> None:
        """Delete the user's CV from storage."""
        pass
