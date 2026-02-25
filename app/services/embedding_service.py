import time
from uuid import UUID
from typing import List
import uuid
from app.repositories.embedding_repository import EmbeddingRepository
from app.models.embedding_model import Embedding
from app.clients.llm_clients.llm_manager import get_cohere_client
from app.utils.chunking import chunk_text

class EmbeddingService:
    def __init__(self, repo: EmbeddingRepository):
        self.repo = repo

    def embed_and_store(self, text: str, user_id: UUID) -> List[Embedding]:
        start = time.time()

        client = get_cohere_client()
        chunks = chunk_text(text)
        total_chunks = len(chunks)

        embeddings_vectors = client.embed(texts=chunks)

        document_id = uuid.uuid4()

        records = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings_vectors)):
            record = Embedding(
                user_id=user_id,
                document_id=document_id,
                content=chunk,
                embedding=vector,
                chunk_index=i,
                total_chunks=total_chunks,
            )
            records.append(self.repo.create(record))

        processing_time_ms = (time.time() - start) * 1000
        return records, processing_time_ms