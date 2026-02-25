import uuid
import time
from uuid import UUID
from typing import List, Tuple
from app.repositories.video_embedding_repository import VideoEmbeddingRepository
from app.models.video_embedding_model import VideoEmbedding
from app.clients.llm_clients.llm_manager import get_cohere_client
from app.utils.youtube_time_chuncking import fetch_transcript, fetch_video_metadata, chunk_transcript, extract_topics
from app.core.exceptions import DuplicateException, NotFoundException
from app.schemas.base_schema import PaginatedResponse
from app.schemas.video_embedding_schema import VideoSummaryResponse


class VideoEmbeddingService:
    def __init__(self, repo: VideoEmbeddingRepository):
        self.repo = repo

    def embed_and_store(self, video_url: str, user_id: UUID) -> Tuple[List[VideoEmbedding], float]:
        start = time.time()

        # Duplicate check
        existing = self.repo.get_by_user_and_url(user_id, video_url)
        if existing:
            raise DuplicateException("Video", "url")

        # Fetch metadata and transcript
        metadata = fetch_video_metadata(video_url)
        transcript = fetch_transcript(video_url)

        # Extract topics from full transcript text
        full_text = " ".join([entry["text"] for entry in transcript])
        topics = extract_topics(full_text)

        # Chunk transcript by time window
        chunks = chunk_transcript(transcript)
        total_chunks = len(chunks)

        # Embed all chunks
        client = get_cohere_client()
        texts = [chunk["content"] for chunk in chunks]
        embeddings_vectors = client.embed(texts=texts)

        # Store all chunks
        video_id = uuid.uuid4()
        records = []
        for i, (chunk, vector) in enumerate(zip(chunks, embeddings_vectors)):
            record = VideoEmbedding(
                user_id=user_id,
                video_id=video_id,
                video_url=video_url,
                title=metadata["title"],
                duration=metadata["duration"],
                topics=topics,
                content=chunk["content"],
                embedding=vector,
                chunk_index=i,
                total_chunks=total_chunks,
                start_time=chunk["start_time"],
                end_time=chunk["end_time"],
            )
            records.append(self.repo.create(record))

        processing_time_ms = (time.time() - start) * 1000
        return records, processing_time_ms
    
    def get_all_paginated(self, page: int, page_size: int) -> PaginatedResponse:
        skip = (page - 1) * page_size
        items, total = self.repo.get_all_videos_paginated(skip=skip, limit=page_size)
        return PaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=-(-total // page_size),
            items=[VideoSummaryResponse(
                video_id=item.video_id,
                video_url=item.video_url,
                title=item.title,
                duration=item.duration,
                topics=item.topics,
                total_chunks=item.total_chunks,
                created_at=item.created_at,
            ) for item in items],
        )
    
    def get_user_videos_paginated(self, user_id: UUID, page: int, page_size: int) -> PaginatedResponse:
        skip = (page - 1) * page_size
        items, total = self.repo.get_user_videos_paginated(user_id=user_id, skip=skip, limit=page_size)
        return PaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=-(-total // page_size),
            items=[VideoSummaryResponse(
                video_id=item.video_id,
                video_url=item.video_url,
                title=item.title,
                duration=item.duration,
                topics=item.topics,
                total_chunks=item.total_chunks,
                created_at=item.created_at,
            ) for item in items],
        )
    
    def get_by_video_id(self, video_id: UUID) -> list:
        return self.repo.get_by_video_id(video_id)
    
    def get_by_chunk_id(self, chunk_id: UUID):
        chunk = self.repo.get_by_chunk_id(chunk_id)
        if not chunk:
            raise NotFoundException("Chunk not found")
        return chunk