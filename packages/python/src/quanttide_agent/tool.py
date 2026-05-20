"""Tool definition with optional executor for Agent use.

>>> t = Tool(name="validate", description="Check domain")
>>> t.name
'validate'
"""

from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel


class Tool(BaseModel):
    """Tool definition with schema fields and optional executor."""

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
