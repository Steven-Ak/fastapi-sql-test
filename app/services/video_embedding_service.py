import time
from typing import List, Tuple
from uuid import UUID
from app.repositories.video_embedding_repository import VideoRepository, VideoChunkRepository, UserVideoRepository
from app.models.video_embedding_model import Video, VideoEmbeddingChunk, UserVideo
from app.clients.llm_clients.llm_manager import get_cohere_client
from app.utils.youtube_time_chuncking import fetch_transcript, fetch_video_metadata, chunk_transcript, extract_topics, extract_video_id
from app.core.exceptions import DuplicateException, NotFoundException
from app.schemas.base_schema import PaginatedResponse
from app.schemas.video_embedding_schema import VideoSummaryResponse, UserVideoResponse


class VideoEmbeddingService:
    def __init__(self, video_repo: VideoRepository, chunk_repo: VideoChunkRepository, user_video_repo: UserVideoRepository):
        self.video_repo = video_repo
        self.chunk_repo = chunk_repo
        self.user_video_repo = user_video_repo

    def embed_and_store(self, video_url: str, user_id: UUID) -> Tuple[Video, list, float]:
        start = time.time()

        # --- Step 1: Check if this video already exists globally ---
        yt_video_id = extract_video_id(video_url)
        video = self.video_repo.get_by_video_id_str(yt_video_id)

        if video:
            # Video already embedded globally — check if this user is already linked
            existing_link = self.user_video_repo.get_by_user_and_video(user_id, video.id)
            if existing_link:
                raise DuplicateException("Video", "video_id")
            # Reuse the existing global video — no re-embedding needed
            chunks = self.chunk_repo.get_by_video_id(video.id)
        else:
            # --- Step 2: Embed and store as a new global video ---
            metadata = fetch_video_metadata(video_url)
            transcript = fetch_transcript(video_url)

            full_text = " ".join([entry["text"] for entry in transcript])
            topics = extract_topics(full_text)

            video = Video(
                video_url=video_url,
                title=metadata["title"],
                duration=metadata["duration"],
                topics=topics,
            )
            video = self.video_repo.create(video)

            chunk_dicts = chunk_transcript(transcript)
            total_chunks = len(chunk_dicts)

            client = get_cohere_client()
            texts = [c["content"] for c in chunk_dicts]
            embeddings_vectors = client.embed(texts=texts)

            chunks = []
            for i, (chunk, vector) in enumerate(zip(chunk_dicts, embeddings_vectors)):
                record = VideoEmbeddingChunk(
                    video_id=video.id,
                    content=chunk["content"],
                    embedding=vector,
                    chunk_index=i,
                    total_chunks=total_chunks,
                    start_time=chunk["start_time"],
                    end_time=chunk["end_time"],
                )
                chunks.append(self.chunk_repo.create(record))

        # --- Step 3: Link this user to the video ---
        self.user_video_repo.create(UserVideo(user_id=user_id, video_id=video.id))

        processing_time_ms = (time.time() - start) * 1000
        return video, chunks, processing_time_ms

    def get_all_paginated(self, page: int, page_size: int) -> PaginatedResponse:
        skip = (page - 1) * page_size
        items, total = self.video_repo.get_all_paginated(skip=skip, limit=page_size)
        return PaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=-(-total // page_size),
            items=[VideoSummaryResponse.model_validate(item) for item in items],
        )

    def get_user_videos_paginated(self, user_id: UUID, page: int, page_size: int) -> PaginatedResponse:
        skip = (page - 1) * page_size
        items, total = self.user_video_repo.get_by_user_id_paginated(user_id=user_id, skip=skip, limit=page_size)
        return PaginatedResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=-(-total // page_size),
            items=[UserVideoResponse.model_validate(item) for item in items],
        )

    def get_by_video_id(self, video_id: UUID) -> List[VideoEmbeddingChunk]:
        return self.chunk_repo.get_by_video_id(video_id)

    def get_by_chunk_id(self, chunk_id: UUID) -> VideoEmbeddingChunk:
        chunk = self.chunk_repo.get_by_chunk_id(chunk_id)
        if not chunk:
            raise NotFoundException("Chunk not found")
        return chunk

    def answer_video_question(self, video_id: UUID, user_id: UUID, question: str):
        """Answer a question about a video's content using RAG (Retrieval-Augmented Generation)."""
        # 1. Verify user access
        link = self.user_video_repo.get_by_user_and_video(user_id, video_id)
        if not link:
            raise NotFoundException("User does not have access to this video.")

        # 2. Embed the question
        client = get_cohere_client()
        query_embedding = client.embed(texts=[question], input_type="search_query")[0]

        # 3. Retrieve similar chunks
        similar_chunks = self.chunk_repo.search_similar_chunks(video_id, query_embedding, limit=5)

        if not similar_chunks:
            return "I couldn't find any relevant information in the video transcript to answer that question.", []

        # 4. Construct context
        context_text = "\n\n".join([
            f"Chunk {c.chunk_index} ({c.start_time:.1f}s - {c.end_time:.1f}s):\n{c.content}"
            for c in similar_chunks
        ])

        # 5. Call LLM for answer
        prompt = [
            {
                "role": "system",
                "content": f"""You are a helpful video assistant. Answer the user's question based ONLY on the provided video transcript segments. 
                If the answer is not in the segments, say so clearly. 
                Be concise and accurate. Cite specific timestamps if helpful. 
                
                Transcript Segments:
                {context_text}"""
            },
            {"role": "user", "content": question}
        ]

        result = client.chat(messages=prompt, temperature=0.3)
        return result["text"], similar_chunks