import uuid
from supabase import create_client, Client
from app.core.config import settings


class SupabaseStorage:
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.bucket = settings.SUPABASE_BUCKET

    def upload_pdf_and_get_signed_url(self, user_id, chat_id, file_bytes: bytes, original_name: str) -> str:
        ext = original_name.split(".")[-1]
        path = f"{user_id}/{chat_id}/{uuid.uuid4()}.{ext}"

        self.client.storage.from_(self.bucket).upload(
            path,
            file_bytes,
            {"content-type": "application/pdf"}
        )

        signed = self.client.storage.from_(self.bucket).create_signed_url(path, 60 * 60)

        return signed["signedURL"]

    def upload_image_and_get_signed_url(self, user_id, file_id, file_bytes: bytes, original_name: str) -> str:
        """Upload image to the images bucket and return signed URL"""
        ext = original_name.split(".")[-1].lower()
        path = f"{user_id}/{file_id}.{ext}"

        content_type_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        content_type = content_type_map.get(ext, "image/jpeg")

        self.client.storage.from_(settings.SUPABASE_IMG_BUCKET).upload(
            path,
            file_bytes,
            {"content-type": content_type}
        )

        signed = self.client.storage.from_(settings.SUPABASE_IMG_BUCKET).create_signed_url(path, 60 * 60)
        return signed["signedURL"]