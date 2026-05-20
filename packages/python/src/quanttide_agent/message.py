"""Message and response models for conversation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

from .cost import Usage
from .tool import ToolCall


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


class ChatResponse(BaseModel):
    """Response from an LLM chat call.

    >>> resp = ChatResponse(content="Hello!", model="deepseek-v4-pro")
    >>> resp.content
    'Hello!'
    """

    content: str
    model: str
    finish_reason: str = "stop"
    reasoning_content: str | None = None
    tool_calls: list[ToolCall] | None = None
    usage: Usage | None = None
