from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database Config
    DATABASE_URL: str

    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_DB_URL: str
    SUPABASE_BUCKET: str
    SUPABASE_IMG_BUCKET: str
    SUPABASE_SERVICE_ROLE_KEY: str

    # Controlling the model's context window and summarization behavior
    SUMMARIZE_THRESHOLD: int = 6
    KEEP_RECENT_MESSAGES: int = 3
    MIN_MESSAGES_TO_SUMMARIZE: int = 2

    #LLM Config
    COHERE_API_KEY: str
    DEFAULT_COHERE_MODEL: str = "command-r-plus-08-2024"
    SUMMARIZATION_MODEL: str = "command-r-08-2024"
    VISION_MODEL: str = "command-a-vision-07-2025"
    EMBEDDING_MODEL: str = "embed-v4.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    def has_cohere_config(self) -> bool:
        return self.COHERE_API_KEY is not None

settings = Settings()