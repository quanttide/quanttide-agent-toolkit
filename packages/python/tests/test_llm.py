from __future__ import annotations

import copy
import json

import httpx
import pytest

from quanttide_agent import ChatResponse, LLM, ToolCall, Usage
from quanttide_agent.llm import LLMError

MOCK_CHAT_RESPONSE = {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1712345678,
    "model": "deepseek-v4-pro",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "Hello! How can I help?"},
            "finish_reason": "stop",
        }
    ],
    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
}


def _make_llm(mock_response: dict | None = None) -> tuple[LLM, list[httpx.Request]]:
    requests: list[httpx.Request] = []
    response = copy.deepcopy(mock_response) if mock_response is not None else copy.deepcopy(MOCK_CHAT_RESPONSE)

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json=response)

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, base_url="http://test")
    return LLM(model="deepseek-v4-pro", api_key="sk-test", _http_client=client), requests


def _body(req: httpx.Request) -> dict:
    return json.loads(req.read())


class TestLLMInit:
    def test_default_base_url(self):
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json=MOCK_CHAT_RESPONSE))
        llm = LLM(model="test", api_key="sk-test", _http_client=httpx.Client(transport=transport, base_url="http://test"))
        assert llm.model == "test"

    def test_custom_base_url(self):
        transport = httpx.MockTransport(lambda r: httpx.Response(200, json=MOCK_CHAT_RESPONSE))
        llm = LLM(model="test", base_url="https://custom.example.com/v1", api_key="sk-test", _http_client=httpx.Client(transport=transport))
        assert llm.model == "test"


class TestChatStringInput:
    def test_returns_chat_response(self):
        llm, reqs = _make_llm()
        resp = llm.chat("Hello")
        assert isinstance(resp, ChatResponse)

    def test_content(self):
        llm, reqs = _make_llm()
        resp = llm.chat("Hello")
        assert resp.content == "Hello! How can I help?"

    def test_sends_correct_body(self):
        llm, reqs = _make_llm()
        llm.chat("Hello")
        body = _body(reqs[0])
        assert body["model"] == "deepseek-v4-pro"
        assert body["messages"][0]["role"] == "user"
        assert body["messages"][0]["content"] == "Hello"


class TestChatListInput:
    def test_with_messages(self):
        llm, reqs = _make_llm()
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
        ]
        resp = llm.chat(messages)
        assert resp.content == "Hello! How can I help?"

    def test_sends_messages_in_body(self):
        llm, reqs = _make_llm()
        llm.chat([{"role": "user", "content": "test"}])
        body = _body(reqs[0])
        assert len(body["messages"]) == 1
        assert body["messages"][0]["role"] == "user"
        assert body["messages"][0]["content"] == "test"


class TestChatParameters:
    def test_temperature(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", temperature=0.7)
        assert _body(reqs[0])["temperature"] == 0.7

    def test_max_tokens(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", max_tokens=100)
        assert _body(reqs[0])["max_tokens"] == 100

    def test_top_p(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", top_p=0.9)
        assert _body(reqs[0])["top_p"] == 0.9

    def test_stop_string(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", stop="\n")
        assert _body(reqs[0])["stop"] == "\n"

    def test_stop_list(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", stop=["\n", "END"])
        assert _body(reqs[0])["stop"] == ["\n", "END"]

    def test_frequency_penalty(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", frequency_penalty=0.5)
        assert _body(reqs[0])["frequency_penalty"] == 0.5

    def test_presence_penalty(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", presence_penalty=0.5)
        assert _body(reqs[0])["presence_penalty"] == 0.5

    def test_model_override(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", model="deepseek-chat")
        assert _body(reqs[0])["model"] == "deepseek-chat"

    def test_tools(self):
        llm, reqs = _make_llm()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather",
                    "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]},
                },
            }
        ]
        llm.chat("Weather?", tools=tools)
        assert "tools" in _body(reqs[0])

    def test_tool_choice(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", tool_choice="auto")
        assert _body(reqs[0])["tool_choice"] == "auto"

    def test_response_format(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", response_format={"type": "json_object"})
        assert _body(reqs[0])["response_format"] == {"type": "json_object"}


class TestThinkingMode:
    def test_thinking_enabled(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", thinking=True)
        assert _body(reqs[0])["thinking"] == {"type": "enabled"}

    def test_thinking_disabled(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", thinking=False)
        assert _body(reqs[0])["thinking"] == {"type": "disabled"}

    def test_reasoning_effort(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", reasoning_effort="high")
        assert _body(reqs[0])["reasoning_effort"] == "high"

    def test_parses_reasoning_content(self):
        mock = copy.deepcopy(MOCK_CHAT_RESPONSE)
        mock["choices"][0]["message"]["reasoning_content"] = "I need to think..."
        llm, reqs = _make_llm(mock)
        resp = llm.chat("Hi", thinking=True)
        assert resp.reasoning_content == "I need to think..."

    def test_no_reasoning_content_by_default(self):
        llm, reqs = _make_llm()
        resp = llm.chat("Hi")
        assert resp.reasoning_content is None


class TestToolCalls:
    def test_parses_tool_calls(self):
        mock = copy.deepcopy(MOCK_CHAT_RESPONSE)
        mock["choices"][0]["message"]["tool_calls"] = [
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": "get_weather", "arguments": '{"location": "Hangzhou"}'},
            }
        ]
        mock["choices"][0]["message"]["content"] = None
        llm, reqs = _make_llm(mock)
        resp = llm.chat("Weather?")
        assert resp.tool_calls is not None
        assert len(resp.tool_calls) == 1
        assert resp.tool_calls[0].name == "get_weather"
        assert resp.tool_calls[0].arguments == '{"location": "Hangzhou"}'

    def test_no_tool_calls_by_default(self):
        llm, reqs = _make_llm()
        resp = llm.chat("Hi")
        assert resp.tool_calls is None


class TestUsage:
    def test_parses_usage(self):
        llm, reqs = _make_llm()
        resp = llm.chat("Hi")
        assert resp.usage is not None
        assert resp.usage.input_tokens == 10
        assert resp.usage.output_tokens == 5
        assert resp.usage.total_tokens == 15

    def test_finish_reason(self):
        llm, reqs = _make_llm()
        resp = llm.chat("Hi")
        assert resp.finish_reason == "stop"

    def test_no_usage(self):
        mock = copy.deepcopy(MOCK_CHAT_RESPONSE)
        del mock["usage"]
        llm, reqs = _make_llm(mock)
        resp = llm.chat("Hi")
        assert resp.usage is None

    def test_partial_usage(self):
        mock = copy.deepcopy(MOCK_CHAT_RESPONSE)
        mock["usage"] = {"prompt_tokens": 10}
        llm, reqs = _make_llm(mock)
        resp = llm.chat("Hi")
        assert resp.usage is not None
        assert resp.usage.input_tokens == 10
        assert resp.usage.output_tokens == 0
        assert resp.usage.total_tokens == 0


class TestModel:
    def test_model_in_response(self):
        mock = copy.deepcopy(MOCK_CHAT_RESPONSE)
        mock["model"] = "deepseek-chat"
        llm, reqs = _make_llm(mock)
        resp = llm.chat("Hi")
        assert resp.model == "deepseek-chat"

    def test_model_fallback_to_constructor(self):
        mock = copy.deepcopy(MOCK_CHAT_RESPONSE)
        del mock["model"]
        llm, reqs = _make_llm(mock)
        resp = llm.chat("Hi")
        assert resp.model == "deepseek-v4-pro"


class TestRetry:
    def test_no_retry_on_success(self):
        llm, reqs = _make_llm()
        llm.chat("Hi", retry=2)
        assert len(reqs) == 1

    def test_retry_then_success(self):
        requests: list[httpx.Request] = []
        attempts = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal attempts
            requests.append(request)
            attempts += 1
            if attempts < 3:
                return httpx.Response(500)
            return httpx.Response(200, json=copy.deepcopy(MOCK_CHAT_RESPONSE))

        transport = httpx.MockTransport(handler)
        client = httpx.Client(transport=transport, base_url="http://test")
        llm = LLM(model="deepseek-v4-pro", api_key="sk-test", _http_client=client)
        resp = llm.chat("Hi", retry=3)
        assert resp.content == "Hello! How can I help?"
        assert len(requests) == 3

    def test_retry_all_fail(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500)

        transport = httpx.MockTransport(handler)
        client = httpx.Client(transport=transport, base_url="http://test")
        llm = LLM(model="deepseek-v4-pro", api_key="sk-test", _http_client=client)
        with pytest.raises(LLMError, match="chat failed after retries"):
            llm.chat("Hi", retry=2)

    def test_zero_retry_fails_once(self):
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(500)

        transport = httpx.MockTransport(handler)
        client = httpx.Client(transport=transport, base_url="http://test")
        llm = LLM(model="deepseek-v4-pro", api_key="sk-test", _http_client=client)
        with pytest.raises(LLMError):
            llm.chat("Hi", retry=0)
        assert len(requests) == 1


class TestExceptions:
    def test_llm_error_is_exception(self):
        assert issubclass(LLMError, Exception)


class TestDataclasses:
    def test_tool_call(self):
        tc = ToolCall(id="c1", name="get_weather", arguments="{}")
        assert tc.id == "c1"
        assert tc.name == "get_weather"
        assert tc.arguments == "{}"

    def test_usage_defaults(self):
        u = Usage()
        assert u.input_tokens == 0
        assert u.output_tokens == 0
        assert u.total_tokens == 0

    def test_chat_response_defaults(self):
        resp = ChatResponse(content="hi", model="m")
        assert resp.finish_reason == "stop"
        assert resp.reasoning_content is None
        assert resp.tool_calls is None
        assert resp.usage is None


class TestAPIConnection:
    def test_endpoint_path(self):
        requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json=MOCK_CHAT_RESPONSE)

        transport = httpx.MockTransport(handler)
        client = httpx.Client(transport=transport, base_url="http://test")
        llm = LLM(model="m", api_key="k", _http_client=client)
        llm.chat("Hi")
        assert requests[0].url.path == "/chat/completions"


class TestEdgeCases:
    def test_empty_content_in_response(self):
        mock = copy.deepcopy(MOCK_CHAT_RESPONSE)
        mock["choices"][0]["message"]["content"] = ""
        llm, reqs = _make_llm(mock)
        resp = llm.chat("Hi")
        assert resp.content == ""

    def test_none_content_in_response(self):
        mock = copy.deepcopy(MOCK_CHAT_RESPONSE)
        mock["choices"][0]["message"]["content"] = None
        llm, reqs = _make_llm(mock)
        resp = llm.chat("Hi")
        assert resp.content == ""
