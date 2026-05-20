"""Agent layer: Message, Action, ActionParser, ReActAgent."""

from __future__ import annotations

import json
import re
from typing import Any, Literal

from pydantic import BaseModel

from .llm import LLM
from .tool import Tool


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
