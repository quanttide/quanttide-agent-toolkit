"""Cost tracking: Usage tokens and cost calculation.

>>> u = Usage(input_tokens=10, output_tokens=5, total_tokens=15)
>>> u.total_tokens
15
"""

from __future__ import annotations

from pydantic import BaseModel


class Usage(BaseModel):
    """Token usage and cost information."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
