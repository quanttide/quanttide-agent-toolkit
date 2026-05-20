# ROADMAP

## v0.1.x 目标

### Message 模型

当前 `chat()` 接受 `list[dict]` 作为消息格式，缺少类型化的 Message 模型。

- 添加 `Message` Pydantic 模型，`role` 用 `Literal` 约束
- 向后兼容：`chat()` 继续接受 `list[dict]` 和 `str`
- 计划版本：v0.1.1

## v0.2.0 目标

### ToolDef → Tool + execute

`ToolDef` 改为 `Tool`，增加可选 `execute: Callable | None` 字段，供 Agent 层直接调用。

- `ToolDef` → `Tool`
- 新增 `execute: Callable | None = None`
- `LLM.chat()` 序列化时自动忽略 `execute`（`model_dump(exclude_none=True)`）
- Agent 直接 `tool.execute(args)`，不再需要外部 executor 映射

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
