from __future__ import annotations

from typing import Any, Literal

import httpx
from pydantic import BaseModel

from .message import Message


class ToolDef(BaseModel):
    """Definition of a tool that the LLM can call.

    >>> td = ToolDef(name="get_weather", description="Get weather", parameters={"type": "object", "properties": {"location": {"type": "string"}}})
    >>> td.name
    'get_weather'
    """

    name: str
    description: str = ""
    parameters: dict | None = None


class ToolCall(BaseModel):
    """A tool call invoked by the LLM."""
    id: str
    name: str
    arguments: str


class Usage(BaseModel):
    """Token usage and cost information.

    >>> u = Usage(input_tokens=10, output_tokens=5, total_tokens=15)
    >>> u.total_tokens
    15
    """

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


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


class LLMError(Exception):
    """Raised when LLM chat fails after retries.

    >>> issubclass(LLMError, Exception)
    True
    """


class LLM:
    """A lightweight LLM client with a single chat interface.

    Usage::

        llm = LLM(model="deepseek-v4-pro", api_key="sk-...")
        resp = llm.chat("Hello")
        print(resp.content)
    """
    def __init__(
        self,
        model: str,
        base_url: str = "https://api.deepseek.com",
        api_key: str = "",
        *,
        _http_client: httpx.Client | None = None,
    ):
        self.model = model
        self._client = _http_client or httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=120,
        )

    def chat(
        self,
        messages: list[Message] | list[dict] | str,
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        stop: str | list[str] | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        thinking: bool | None = None,
        reasoning_effort: Literal["low", "medium", "high", "max"] | None = None,
        tools: list[ToolDef] | None = None,
        tool_choice: str | None = None,
        response_format: dict | None = None,
        retry: int = 0,
    ) -> ChatResponse:
        if isinstance(messages, str):
            body_messages: list[dict] = [{"role": "user", "content": messages}]
        elif messages and isinstance(messages[0], Message):
            body_messages = [m.to_dict() for m in messages]  # type: ignore
        else:
            body_messages = messages  # type: ignore

        body: dict[str, Any] = {"model": model or self.model, "messages": body_messages}

        if temperature is not None:
            body["temperature"] = temperature
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        if top_p is not None:
            body["top_p"] = top_p
        if stop is not None:
            body["stop"] = stop
        if frequency_penalty is not None:
            body["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            body["presence_penalty"] = presence_penalty
        if thinking is not None:
            body["thinking"] = {"type": "enabled" if thinking else "disabled"}
        if reasoning_effort is not None:
            body["reasoning_effort"] = reasoning_effort
        if tools is not None:
            body["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters or {"type": "object", "properties": {}},
                    },
                }
                for t in tools
            ]
        if tool_choice is not None:
            body["tool_choice"] = tool_choice
        if response_format is not None:
            body["response_format"] = response_format

        last_error: Exception | None = None
        for _ in range(max(retry + 1, 1)):
            try:
                resp = self._client.post("/chat/completions", json=body)
                resp.raise_for_status()
                data: dict = resp.json()
                break
            except httpx.HTTPStatusError as e:
                last_error = e
                continue
        else:
            assert last_error is not None
            raise LLMError("chat failed after retries") from last_error

        choice = data["choices"][0]
        msg = choice["message"]

        tool_calls = None
        if msg.get("tool_calls"):
            tool_calls = [
                ToolCall(id=tc["id"], name=tc["function"]["name"], arguments=tc["function"]["arguments"])
                for tc in msg["tool_calls"]
            ]

        usage_raw = data.get("usage")
        usage = None
        if usage_raw:
            input_tokens = usage_raw.get("prompt_tokens", 0)
            output_tokens = usage_raw.get("completion_tokens", 0)
            usage = Usage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=usage_raw.get("total_tokens", 0),
            )

        return ChatResponse(
            content=msg.get("content", "") or "",
            model=data.get("model", model or self.model),
            finish_reason=choice.get("finish_reason", "stop"),
            reasoning_content=msg.get("reasoning_content"),
            tool_calls=tool_calls,
            usage=usage,
        )
