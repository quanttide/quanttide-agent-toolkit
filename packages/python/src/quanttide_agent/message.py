"""Message model for conversation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class Message(BaseModel):
    """A message in a conversation.

    >>> m = Message(role="user", content="hello")
    >>> m.to_dict()
    {'role': 'user', 'content': 'hello'}
    """

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_call_id: str | None = None

    def to_dict(self) -> dict:
        d: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        return d
