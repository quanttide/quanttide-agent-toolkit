from __future__ import annotations

from typing import Any, Literal

import anyio
import httpx

from .config import settings
from .cost import Usage
from .message import ChatResponse, Message
from .tool import ToolCall, ToolSchema


class LLMError(Exception):
    """Raised when LLM chat fails after retries.

    >>> issubclass(LLMError, Exception)
    True
    """


class BaseLLM:
    """Shared initialization and chat helpers for sync/async LLM clients."""

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        *,
        _client: httpx.Client | httpx.AsyncClient | None = None,
    ):
        self.model = model or settings.llm_model
        api_key = api_key or settings.llm_api_key
        base_url = (base_url or settings.llm_base_url).rstrip("/")
        self._client: httpx.Client | httpx.AsyncClient = _client

    @staticmethod
    def build_chat_body(
        messages: list[Message] | list[dict] | str,
        *,
        model: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        stop: str | list[str] | None = None,
        frequency_penalty: float | None = None,
        presence_penalty: float | None = None,
        thinking: bool | None = None,
        reasoning_effort: Literal["low", "medium", "high", "max"] | None = None,
        tools: list[ToolSchema] | None = None,
        tool_choice: str | None = None,
        response_format: dict | None = None,
    ) -> dict:
        if isinstance(messages, str):
            body_messages: list[dict] = [{"role": "user", "content": messages}]
        elif messages and isinstance(messages[0], Message):
            body_messages = [m.to_dict() for m in messages]
        else:
            body_messages = messages  # type: ignore

        body: dict[str, Any] = {"model": model, "messages": body_messages}

        _params: dict[str, Any] = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stop": stop,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "reasoning_effort": reasoning_effort,
            "tool_choice": tool_choice,
            "response_format": response_format,
        }
        body.update({k: v for k, v in _params.items() if v is not None})

        if thinking is not None:
            body["thinking"] = {"type": "enabled" if thinking else "disabled"}
        if tools is not None:
            body["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters
                        or {"type": "object", "properties": {}},
                    },
                }
                for t in tools
            ]

        return body

    @staticmethod
    def parse_chat_response(data: dict, model: str) -> ChatResponse:
        choice = data["choices"][0]
        msg = choice["message"]

        tool_calls = None
        if msg.get("tool_calls"):
            tool_calls = [
                ToolCall(
                    id=tc["id"],
                    name=tc["function"]["name"],
                    arguments=tc["function"]["arguments"],
                )
                for tc in msg["tool_calls"]
            ]

        usage_raw = data.get("usage")
        usage = Usage.from_api(usage_raw) if usage_raw else None

        return ChatResponse(
            content=msg.get("content", "") or "",
            model=data.get("model", model),
            finish_reason=choice.get("finish_reason", "stop"),
            reasoning_content=msg.get("reasoning_content"),
            tool_calls=tool_calls,
            usage=usage,
        )


class LLM(BaseLLM):
    """Sync LLM client.

    Usage::

        llm = LLM(model="deepseek-v4-pro", api_key="sk-...")
        resp = llm.complete("Hello")
        print(resp.content)
    """

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        *,
        _http_client: httpx.Client | None = None,
    ):
        api_key = api_key or settings.llm_api_key
        base_url = (base_url or settings.llm_base_url).rstrip("/")
        super().__init__(
            model=model,
            _client=_http_client
            or httpx.Client(
                base_url=base_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120,
            ),
        )

    def complete(
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
        tools: list[ToolSchema] | None = None,
        tool_choice: str | None = None,
        response_format: dict | None = None,
        retry: int = 0,
    ) -> ChatResponse:
        body = self.build_chat_body(
            messages,
            model=model or self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            thinking=thinking,
            reasoning_effort=reasoning_effort,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
        )

        last_error: Exception | None = None
        for _ in range(max(retry + 1, 1)):
            try:
                resp = self._client.post("/chat/completions", json=body)  # type: ignore[union-attr]
                resp.raise_for_status()
                data: dict = resp.json()
                break
            except httpx.HTTPStatusError as e:
                last_error = e
                continue
        else:
            assert last_error is not None
            raise LLMError("chat failed after retries") from last_error

        return self.parse_chat_response(data, model or self.model)


class AsyncLLM(BaseLLM):
    """Async LLM client.

    Usage::

        llm = AsyncLLM(model="deepseek-v4-pro", api_key="sk-...")
        resp = await llm.complete("Hello")
        print(resp.content)
    """

    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        *,
        _http_client: httpx.AsyncClient | None = None,
    ):
        api_key = api_key or settings.llm_api_key
        base_url = (base_url or settings.llm_base_url).rstrip("/")
        super().__init__(
            model=model,
            _client=_http_client
            or httpx.AsyncClient(
                base_url=base_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=120,
            ),
        )

    async def complete(
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
        tools: list[ToolSchema] | None = None,
        tool_choice: str | None = None,
        response_format: dict | None = None,
        retry: int = 0,
    ) -> ChatResponse:
        body = self.build_chat_body(
            messages,
            model=model or self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stop=stop,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            thinking=thinking,
            reasoning_effort=reasoning_effort,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
        )

        last_error: Exception | None = None
        for _ in range(max(retry + 1, 1)):
            try:
                resp = await self._client.post("/chat/completions", json=body)
                resp.raise_for_status()
                data: dict = resp.json()
                break
            except httpx.HTTPStatusError as e:
                last_error = e
                continue
        else:
            assert last_error is not None
            raise LLMError("chat failed after retries") from last_error

        return self.parse_chat_response(data, model or self.model)
