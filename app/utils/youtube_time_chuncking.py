from youtube_transcript_api import YouTubeTranscriptApi
from pytubefix import YouTube
from typing import List, Dict, Any
from app.core.config import settings
from app.clients.llm_clients.llm_manager import get_cohere_client


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL"""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    raise ValueError(f"Could not extract video ID from URL: {url}")


def fetch_video_metadata(url: str) -> Dict[str, Any]:
    """Fetch video title and duration from YouTube"""
    yt = YouTube(url)
    return {
        "title": yt.title,
        "duration": yt.length,  # in seconds
    }


def fetch_transcript(url: str) -> List[Dict[str, Any]]:
    """Fetch transcript with timestamps from YouTube"""
    video_id = extract_video_id(url)
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id)
    return [{"text": entry.text, "start": entry.start, "duration": entry.duration} for entry in transcript]  # list of {"text": "...", "start": 0.0, "duration": 1.5}


def chunk_transcript(
    transcript: List[Dict[str, Any]],
    chunk_seconds: int = None,
) -> List[Dict[str, Any]]:
    if chunk_seconds is None:
        chunk_seconds = settings.VIDEO_CHUNK_SECONDS

    chunks = []
    current_chunk = []
    current_start = transcript[0]["start"] if transcript else 0

    for entry in transcript:
        current_chunk.append(entry["text"])
        current_end = entry["start"] + entry["duration"]

        # Check if we've reached the chunk size based on time elapsed
        if current_end - current_start >= chunk_seconds:
            chunks.append({
                "content": " ".join(current_chunk),
                "start_time": current_start,
                "end_time": current_end,
            })
            current_chunk = []
            current_start = current_end

    # Add remaining entries as last chunk
    if current_chunk:
        last = transcript[-1]
        chunks.append({
            "content": " ".join(current_chunk),
            "start_time": current_start,
            "end_time": last["start"] + last["duration"],
        })

    return chunks


def extract_topics(transcript_text: str) -> List[str]:
    """Use Cohere to extract topics from full transcript"""
    client = get_cohere_client()
    result = client.chat(
        messages=[
            {
                "role": "user",
                "content": f"""Extract the main topics from this video transcript. 
                Return only a JSON array of short topic strings, nothing else.
                Example: ["machine learning", "neural networks", "backpropagation"]
                
                Transcript:
                {transcript_text[:8000]}"""  
            }
        ],
        temperature=0.3,
        max_tokens=200,
    )

    import json
    try:
        # Strip any markdown fences if present
        text = result["text"].strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return []