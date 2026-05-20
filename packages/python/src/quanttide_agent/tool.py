"""Tool models: ToolSchema, ToolCall, Tool."""

from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel


class ToolSchema(BaseModel):
    """Definition of a tool that the LLM can call.

    >>> ts = ToolSchema(name="get_weather", description="Get weather", parameters={"type": "object", "properties": {"location": {"type": "string"}}})
    >>> ts.name
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


class Tool(ToolSchema):
    """Tool schema with optional executor for Agent use.

    >>> t = Tool(name="validate", description="Check domain")
    >>> t.name
    'validate'
    """

    executor: Callable | None = None

    def execute(self, inp: dict) -> str:
        if not self.executor:
            return f"未知工具: {self.name}"
        try:
            return str(self.executor(inp))
        except Exception as e:
            return f"执行错误: {e}"
