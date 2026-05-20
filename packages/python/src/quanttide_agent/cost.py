"""Cost tracking: Usage tokens.

Standardized naming across providers. Parsed from API response via `from_api`.
"""

from __future__ import annotations

from pydantic import BaseModel


class Usage(BaseModel):
    """Token usage and cost information.

    >>> u = Usage(input_tokens=10, output_tokens=5, total_tokens=15)
    >>> u.total_tokens
    15
    >>> u.input_cached_tokens
    0
    """

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    input_cached_tokens: int = 0
    input_uncached_tokens: int = 0
    reasoning_tokens: int = 0

    @classmethod
    def from_api(cls, data: dict) -> Usage | None:
        if not data:
            return None
        return cls(
            input_tokens=data.get("prompt_tokens", 0),
            output_tokens=data.get("completion_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
            input_cached_tokens=data.get("prompt_cache_hit_tokens", 0),
            input_uncached_tokens=data.get("prompt_cache_miss_tokens", 0),
            reasoning_tokens=data.get("completion_tokens_details", {}).get("reasoning_tokens", 0),
        )
