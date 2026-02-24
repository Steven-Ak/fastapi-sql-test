from typing import List

def chunk_text(
    text: str,
    chunk_size: int = 400,      
    overlap: int = 50,           
) -> List[str]:
    """
    Split text into chunks based on approximate token count.
    Uses character count as proxy (1 token ≈ 4 chars).
    """
    char_size = chunk_size * 4
    char_overlap = overlap * 4

    chunks = []
    start = 0

    while start < len(text):
        end = start + char_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += char_size - char_overlap

    return [c for c in chunks if c]  # filter empty chunks