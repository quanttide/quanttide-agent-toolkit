from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from quanttide_agent import ChatResponse

from quanttide_agent.agent import Action, ActionParser, ReActAgent
from quanttide_agent.message import Message
from quanttide_agent.tool import Tool


class TestMessage:
    def test_system(self):
        m = Message(role="system", content="你好")
        assert m.to_dict() == {"role": "system", "content": "你好"}

    def test_user(self):
        m = Message(role="user", content="hi")
        assert m.to_dict() == {"role": "user", "content": "hi"}

    def test_tool(self):
        m = Message(role="tool", content="result", tool_call_id="c1")
        assert m.to_dict() == {"role": "tool", "content": "result", "tool_call_id": "c1"}


class TestAction:
    def test_create(self):
        a = Action(name="test", args={"x": 1})
        assert a.name == "test"
        assert a.args == {"x": 1}

    def test_default_args(self):
        a = Action(name="test")
        assert a.args == {}


class TestActionParser:
    def setup_method(self):
        self.parser = ActionParser()

    def test_parse_valid(self):
        a = self.parser.parse("Thought: 思考\nAction name: validate\nAction args: {}")
        assert a is not None
        assert a.name == "validate"
        assert a.args == {}

    def test_parse_with_args(self):
        a = self.parser.parse('Action name: search\nAction args: {"q": "test"}')
        assert a.name == "search"
        assert a.args == {"q": "test"}

    def test_parse_none(self):
        assert self.parser.parse("随便说说") is None

    def test_parse_custom_keywords(self):
        p = ActionParser(key_action_name="Do", key_action_args="With")
        a = p.parse("Do: test\nWith: {}")
        assert a.name == "test"


class TestTool:
    def test_execute(self):
        calls = []

        def fn(args):
            calls.append(args)
            return "ok"

        t = Tool(name="t", executor=fn)
        assert t.execute({"x": 1}) == "ok"
        assert calls == [{"x": 1}]

    def test_execute_no_executor(self):
        t = Tool(name="t")
        assert "未知工具" in t.execute({})

    def test_execute_error(self):
        def fn(args):
            raise ValueError("bad")

        t = Tool(name="t", executor=fn)
        assert "执行错误" in t.execute({})


class TestReActAgent:
    def test_direct_answer(self):
        llm = MagicMock()
        llm.chat.return_value = ChatResponse(content="Final Answer: done", model="deepseek")
        agent = ReActAgent(llm, [], max_steps=5)
        result = agent.run([Message(role="user", content="hi")])
        assert result == "done"

    def test_tool_call_loop(self):
        llm = MagicMock()
        llm.chat.side_effect = [
            ChatResponse(content="Action name: test\nAction args: {}", model="deepseek"),
            ChatResponse(content="Final Answer: ok", model="deepseek"),
        ]
        calls = []
        t = Tool(name="test", executor=lambda args: calls.append(args) or "result")
        agent = ReActAgent(llm, [t])
        result = agent.run([Message(role="user", content="do it")])
        assert result == "ok"
        assert len(calls) == 1

    def test_max_steps(self):
        llm = MagicMock()
        llm.chat.return_value = ChatResponse(content="Action name: test\nAction args: {}", model="deepseek")
        t = Tool(name="test", executor=lambda args: "ok")
        agent = ReActAgent(llm, [t], max_steps=2)
        result = agent.run([Message(role="user", content="x")])
        assert "最大步数" in result

    def test_malformed_action(self):
        llm = MagicMock()
        llm.chat.side_effect = [
            ChatResponse(content="乱写", model="deepseek"),
            ChatResponse(content="Final Answer: fixed", model="deepseek"),
        ]
        agent = ReActAgent(llm, [], max_steps=5)
        result = agent.run([Message(role="user", content="x")])
        assert result == "fixed"


class TestSystemPrompt:
    def test_contains_keywords(self):
        prompt = ReActAgent.system_prompt("tool list")
        assert "Action name" in prompt
        assert "Action args" in prompt
        assert "tool list" in prompt

    def test_custom_parser(self):
        p = ActionParser(key_action_name="Do", key_action_args="With")
        prompt = ReActAgent.system_prompt("tools", p)
        assert "Do:" in prompt
        assert "With:" in prompt
