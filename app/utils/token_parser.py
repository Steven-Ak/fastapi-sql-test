from typing import Dict, Any, Optional
from app.schemas.chat_schema import TokenUsage, BilletedUnits


def extract_token_usage(result: Dict[str, Any]) -> TokenUsage:
    """Extract token usage from an LLM response dict."""
    if "billed_units" in result and result["billed_units"]:
        billed = result["billed_units"]
        prompt_tokens = billed.get("input_tokens", 0) or 0
        completion_tokens = billed.get("output_tokens", 0) or 0
    elif "tokens" in result and result["tokens"]:
        tokens = result["tokens"]
        prompt_tokens = tokens.get("input_tokens", 0) or 0
        completion_tokens = tokens.get("output_tokens", 0) or 0
    else:
        prompt_tokens = 0
        completion_tokens = 0

    return TokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )


def extract_billed_units(result: Dict[str, Any]) -> Optional[BilletedUnits]:
    """Extract Cohere billing information from an LLM response dict."""
    if "billed_units" not in result or not result["billed_units"]:
        return None

    billed = result["billed_units"]
    return BilletedUnits(
        input_tokens=billed.get("input_tokens"),
        output_tokens=billed.get("output_tokens"),
        search_units=billed.get("search_units"),
        classifications=billed.get("classifications"),
    )
