from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database Config
    DATABASE_URL: str

    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_DB_URL: str

    #LLM Config
    COHERE_API_KEY: str
    DEFAULT_COHERE_MODEL: str = "command-r-08-2024"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    def has_cohere_config(self) -> bool:
        return self.COHERE_API_KEY is not None

settings = Settings()