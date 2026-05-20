# ROADMAP

## v0.1.x 目标

### Message 模型

当前 `chat()` 接受 `list[dict]` 作为消息格式，缺少类型化的 Message 模型。

- 添加 `Message` Pydantic 模型，`role` 用 `Literal` 约束
- 向后兼容：`chat()` 继续接受 `list[dict]` 和 `str`
- 计划版本：v0.1.1

## v0.2.0 目标

### ToolDef → ToolSchema 重命名

`ToolDef` 本质是 schema（`name` + `description` + `parameters`），不是可执行的 Tool。`ToolSchema` 更准确。

- `ToolDef` → `ToolSchema`
- `Tool` 留给未来的可执行工具概念
- 不改变 `ToolCall` / `Usage` / `ChatResponse` 等现有模型
- 破坏性变更，作为 v0.2.0 统一发布

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
