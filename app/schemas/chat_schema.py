from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from uuid import UUID

class LLMProvider(str, Enum):
    COHERE = "cohere"


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: MessageRole = MessageRole.USER
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    chat_id: Optional[UUID] = Field(default=None, description="Pass a chat_id to continue an existing conversation. Omit to start a new chat.")
    provider: LLMProvider = LLMProvider.COHERE
    model: Optional[str] = None  # If None, uses default for provider
    temperature: float = Field(default=0.7, ge=0, le=1)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"content": "What is Python?"}
                ],
                "chat_id": None,
                "provider": "cohere",
                "model": "command-r-plus-08-2024",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }


class TokenUsage(BaseModel):
    """Token usage information"""
    prompt_tokens: int = Field(description="Tokens in the input/prompt")
    completion_tokens: int = Field(description="Tokens in the response/completion")
    total_tokens: int = Field(description="Total tokens used (prompt + completion)")


class BilletedUnits(BaseModel):
    """Cohere-specific billing information"""
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    search_units: Optional[int] = None
    classifications: Optional[int] = None


class ApiVersion(BaseModel):
    """API version information"""
    version: Optional[str] = None
    is_deprecated: Optional[bool] = None
    is_experimental: Optional[bool] = None


class ChatResponse(BaseModel):
    """Comprehensive chat response with all metadata"""
    
    # Chat session
    chat_id: UUID = Field(description="The chat session UUID (new or existing)")
    
    # Core response
    response: str = Field(description="The actual text response from the LLM")
    
    # Model information
    provider: LLMProvider = Field(description="Which LLM provider was used")
    model: str = Field(description="Specific model that generated the response")
    
    # Token usage
    token_usage: TokenUsage = Field(description="Token consumption details")

    file_url: Optional[str] = None
    
    # Timing
    response_time_ms: Optional[float] = Field(
        default=None, 
        description="Time taken to generate response in milliseconds"
    )
    
    # Cohere-specific metadata (optional)
    generation_id: Optional[str] = Field(
        default=None,
        description="Unique ID for this generation (Cohere)"
    )
    billed_units: Optional[BilletedUnits] = Field(
        default=None,
        description="Billing information (Cohere)"
    )
    finish_reason: Optional[str] = Field(
        default=None,
        description="Why the generation stopped (e.g., 'COMPLETE', 'MAX_TOKENS')"
    )
    
    # Additional metadata
    meta: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional provider-specific metadata"
    )
    
    # Request parameters (for reference)
    request_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Parameters used in the request"
    )
    
    class Config:
        from_attributes = True


# ----- Chat session / history schemas -----

class ChatMessageOut(BaseModel):
    """A single message in the chat history"""
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    """Chat session metadata (for listing chats)"""
    id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    """Full chat history with all messages"""
    id: UUID
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageOut] = []

    class Config:
        from_attributes = True

class ImageDescribeResponse(BaseModel):
    description: str
    file_url: str
    model: str = Field(default="command-a-vision-07-2025")

class EmbedRequest(BaseModel):
    texts: List[str] = Field(..., description="List of texts to embed", min_length=1)
    input_type: str = Field(
        default="search_document",
        description="Cohere input type: search_document, search_query, classification, clustering"
    )

class EmbedResponse(BaseModel):
    embeddings: List[List[float]] = Field(description="List of embedding vectors")
    model: str = Field(description="Model used for embedding")
    input_type: str
    texts_count: int = Field(description="Number of texts embedded")
    embedding_dimension: int = Field(description="Dimension of each embedding vector")