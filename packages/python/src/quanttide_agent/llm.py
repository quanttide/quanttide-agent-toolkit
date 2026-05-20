from __future__ import annotations

from typing import Any, Literal

import httpx
from pydantic import BaseModel


class ToolCall(BaseModel):
    """A tool call returned by the LLM.

    >>> tc = ToolCall(id="call_1", name="get_weather", arguments='{}')
    >>> tc.name
    'get_weather'
    """

    id: str
    name: str
    arguments: str


class Usage(BaseModel):
    """Token usage information.

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
        messages: list[dict] | str,
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
        tools: list[dict] | None = None,
        tool_choice: str | None = None,
        response_format: dict | None = None,
        retry: int = 0,
    ) -> ChatResponse:
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        body: dict[str, Any] = {"model": model or self.model, "messages": messages}

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
            body["tools"] = tools
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
            usage = Usage(
                input_tokens=usage_raw.get("prompt_tokens", 0),
                output_tokens=usage_raw.get("completion_tokens", 0),
                total_tokens=usage_raw.get("total_tokens", 0),
            )

        return ChatResponse(
            content=msg.get("content", "") or "",
            model=data.get("model", model or self.model),
            reasoning_content=msg.get("reasoning_content"),
            tool_calls=tool_calls,
            usage=usage,
        )
