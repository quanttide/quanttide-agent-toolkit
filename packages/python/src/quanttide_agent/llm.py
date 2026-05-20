from __future__ import annotations

import json
import re
from collections.abc import Callable
from typing import Any, Literal

import httpx
from pydantic import BaseModel


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


class Action(BaseModel):
    """An action instruction parsed from LLM output.

    >>> a = Action(name="validate", args={"domain": "test"})
    >>> a.name
    'validate'
    """

    name: str
    args: dict = {}


class ActionParser:
    """Parser that extracts Action from LLM text replies.

    >>> parser = ActionParser()
    >>> result = parser.parse("Action name: validate\\nAction args: {}")
    >>> result.name
    'validate'
    """

    def __init__(self, key_action_name: str = "Action name", key_action_args: str = "Action args", pattern: str | None = None):
        self.key_action_name = key_action_name
        self.key_action_args = key_action_args
        self._pattern = pattern or rf"{key_action_name}:\s*(.+)\n{key_action_args}:\s*(.+)"

    def parse(self, text: str) -> Action | None:
        m = re.search(self._pattern, text)
        if not m:
            return None
        name = m.group(1).strip()
        raw = m.group(2).strip()
        try:
            inp = json.loads(raw)
        except json.JSONDecodeError:
            inp = raw
        return Action(name=name, args=inp)


class Tool(BaseModel):
    """Tool definition with optional executor for Agent use.

    >>> t = Tool(name="validate", description="Check domain structure")
    >>> t.name
    'validate'
    """

    name: str
    description: str = ""
    parameters: dict | None = None
    executor: Callable | None = None

    def execute(self, inp: dict) -> str:
        if not self.executor:
            return f"未知工具: {self.name}"
        try:
            return str(self.executor(inp))
        except Exception as e:
            return f"执行错误: {e}"


class ReActAgent:
    """Thought → Action → Observation loop using a ReAct protocol.

    Usage::

        llm = LLM(model="deepseek-v4-pro", api_key="sk-...")
        tools = [Tool(name="search", description="Search", executor=search_fn)]
        agent = ReActAgent(llm, tools)
        result = agent.run([
            Message(role="system", content=ReActAgent.system_prompt("Tools:\\n- search")),
            Message(role="user", content="Find something"),
        ])
    """

    def __init__(self, llm: LLM, tools: list[Tool], *, parser: ActionParser | None = None, max_steps: int = 10):
        self.llm = llm
        self._tools = {t.name: t for t in tools}
        self._parser = parser or ActionParser()
        self.max_steps = max_steps

    def run(self, messages: list[Message]) -> str:
        messages = list(messages)
        for _ in range(self.max_steps):
            resp = self.llm.chat([m.to_dict() for m in messages])
            output = resp.content.strip()

            if "Final Answer:" in output:
                return output.split("Final Answer:", 1)[1].strip()

            action = self._parser.parse(output)
            messages.append(Message(role="assistant", content=output))
            if not action:
                messages.append(Message(role="user", content="无法解析指令，请使用正确的 ReAct 格式。"))
                continue

            tool = self._tools.get(action.name)
            result = tool.execute(action.args) if tool else f"未知工具: {action.name}"
            messages.append(Message(role="tool", tool_call_id=action.name, content=result))

        return "达到最大步数，未得到最终答案。"

    @staticmethod
    def system_prompt(tool_descriptions: str, parser: ActionParser | None = None) -> str:
        p = parser or ActionParser()
        return f"""你可以使用以下工具：

{tool_descriptions}

每次回复按以下格式：

Thought: 你当前的思考
{p.key_action_name}: 工具名称
{p.key_action_args}: 给工具的参数（JSON 格式）

当得到最终答案时：

Thought: 我得到答案了
Final Answer: 你的最终回复
"""


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
        tools: list[ToolDef] | None = None,
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
