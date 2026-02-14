from typing import List, Dict, Optional, Any
import cohere
from app.clients.llm_clients.llm_base_client import BaseLLMClient


class CohereClient(BaseLLMClient):
    """Cohere LLM client implementation"""
    
    def __init__(self, api_key: str, model: str = "command-r-08-2024"):
        super().__init__(api_key, model)
        self.client = cohere.Client(api_key)
        self._available_models = [
            "command-r-plus-08-2024",
            "command-r-08-2024",
        ]
    
    def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:

        
        # Convert messages format to Cohere's chat history format
        chat_history = []
        message = ""
        preamble = None
        
        for msg in messages:
            if msg["role"] == "system":
                preamble = msg["content"]
            elif msg["role"] == "user":
                message = msg["content"]
            elif msg["role"] == "assistant":
                chat_history.append({
                    "role": "CHATBOT",
                    "message": msg["content"]
                })
        
        # Make the API call
        response = self.client.chat(
            message=message,
            chat_history=chat_history if chat_history else None,
            preamble=preamble,
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Extract all available information
        result = {
            "text": response.text,
            "generation_id": getattr(response, 'generation_id', None),
            "finish_reason": getattr(response, 'finish_reason', None),
            "meta": {}
        }
        
        # Token usage
        if hasattr(response, 'meta') and response.meta:
            meta = response.meta
            
            # Billed units (Cohere's billing information)
            if hasattr(meta, 'billed_units') and meta.billed_units:
                billed = meta.billed_units
                result["billed_units"] = {
                    "input_tokens": getattr(billed, 'input_tokens', None),
                    "output_tokens": getattr(billed, 'output_tokens', None),
                    "search_units": getattr(billed, 'search_units', None),
                    "classifications": getattr(billed, 'classifications', None),
                }
            
            # Tokens (alternative token counting)
            if hasattr(meta, 'tokens') and meta.tokens:
                tokens = meta.tokens
                result["tokens"] = {
                    "input_tokens": getattr(tokens, 'input_tokens', None),
                    "output_tokens": getattr(tokens, 'output_tokens', None),
                }
            
            # API version
            if hasattr(meta, 'api_version') and meta.api_version:
                api_ver = meta.api_version
                result["meta"]["api_version"] = {
                    "version": getattr(api_ver, 'version', None),
                    "is_deprecated": getattr(api_ver, 'is_deprecated', None),
                    "is_experimental": getattr(api_ver, 'is_experimental', None),
                }
            
            # Warnings
            if hasattr(meta, 'warnings') and meta.warnings:
                result["meta"]["warnings"] = meta.warnings
        
        # Citations (if available)
        if hasattr(response, 'citations') and response.citations:
            result["meta"]["citations"] = [
                {
                    "start": c.start,
                    "end": c.end,
                    "text": c.text,
                    "document_ids": c.document_ids
                }
                for c in response.citations
            ]
        
        # Documents (if RAG was used)
        if hasattr(response, 'documents') and response.documents:
            result["meta"]["documents"] = response.documents
        
        # Search queries (if search was used)
        if hasattr(response, 'search_queries') and response.search_queries:
            result["meta"]["search_queries"] = [
                {
                    "text": q.text,
                    "generation_id": q.generation_id
                }
                for q in response.search_queries
            ]
        
        # Search results
        if hasattr(response, 'search_results') and response.search_results:
            result["meta"]["search_results"] = response.search_results
        
        return result
    
    def stream_chat(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs):
        """Streaming disabled for now"""
        raise NotImplementedError("Streaming is not implemented yet")
    
    @property
    def available_models(self) -> List[str]:
        return self._available_models