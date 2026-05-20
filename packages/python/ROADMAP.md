# ROADMAP

## v0.1.x 目标

### Message 模型

- 添加 `Message` Pydantic 模型，`role` 用 `Literal` 约束
- 向后兼容：`chat()` 继续接受 `list[dict]` 和 `str`
- 计划版本：v0.1.1

### Action 模型 + ActionParser + ReActAgent

Agent ReAct 协议的完整组件，已在 knowl 项目中实验验证。

- `Action(name, args)` — 纯数据模型
- `ActionParser(key_name, key_args, pattern).parse(text)` — 可配置解析器
- `ReActAgent(llm, tools, parser).run(messages)` — ReAct 循环
- `ReActAgent.system_prompt(tool_desc, parser)` — 可选的协议格式说明

计划版本：v0.1.x（与 Message 同期）

## v0.2.0 目标

### ToolDef → ToolSchema + Tool

`ToolDef` 拆为两个概念：

- `ToolSchema` — 纯数据模型（`name` + `description` + `parameters`），可序列化，`LLM.chat(tools=...)` 使用
- `Tool` — `ToolSchema` + `executor: Callable`，Agent 层使用，`tool.execute(args)` 带错误处理

```python
# LLM 层 — 只需要 schema
resp = llm.chat(messages, tools=[ToolSchema(name="validate", ...)])

# Agent 层 — schema + executor 合一
tools = [Tool(name="validate", executor=fn)]
agent = ReActAgent(llm, tools)
resp = llm.chat(messages, tools=[t.model_dump(exclude={"executor"}) for t in tools])
```

## 待考察方向

以下问题暂不排期。

### Provider 特化参数

`chat()` 的 `thinking` / `reasoning_effort` 参数是 DeepSeek 特化的，对其他 Provider 不通用。

- 备选方案：增加 `extra_body` 透传，移除命名参数
- 触发条件：需要支持 DeepSeek 以外的 Provider

### Streaming / Async

当前只支持同步阻塞调用。无 streaming，无 async。

- 备选方案：`chat(stream=True)` 返回 Generator，新增 `async_chat()`
- 触发条件：有项目需要流式输出

### Retry 策略

当前对所有 4xx/5xx 统一重试，可能吞掉不该重试的错误（如 4xx 认证错误）。

- 备选方案：按状态码区分重试策略
- 触发条件：实际遇到重试误吞问题
