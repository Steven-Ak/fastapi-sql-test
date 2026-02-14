from typing import Optional
from app.core.config import settings
from app.clients.llm_clients.cohere_client import CohereClient


# Initialize clients
cohere_client = None
if settings.has_cohere_config:
    cohere_client = CohereClient(
        api_key=settings.COHERE_API_KEY,
        model=settings.DEFAULT_COHERE_MODEL
    )


def get_cohere_client() -> CohereClient:
    """Get Cohere client"""
    if cohere_client is None:
        raise RuntimeError("Cohere is not configured. Please set COHERE_API_KEY.")
    return cohere_client