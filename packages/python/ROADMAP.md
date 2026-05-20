# ROADMAP

## v0.2.x — 已完成

- [x] `LLM.complete()` 替换 `chat()`（chat 标记废弃，v0.3.0 移除）
- [x] `ReActAgent` + `ActionParser` + `Tool` 进入标准库
- [x] `config` 模块 with pydantic-settings + vault 支持
- [x] `Usage.from_api()` 标准化字段
- [x] 100% 测试覆盖率
- [x] 在 `qtcloud-knowl` 项目中实地验证通过

## v0.3.0 计划

### 清理弃用接口

- 移除 `LLM.chat()` 方法
- 移除 `ToolDef` 别名（v0.2.0 起已改用 `ToolSchema`）

### Provider 特化参数

`chat()` / `complete()` 的 `thinking` / `reasoning_effort` 参数是 DeepSeek 特化的。

- 备选：用 `extra_body` 透传替代命名参数
- 触发条件：需要支持 DeepSeek 以外的 Provider

## 待考察

- Streaming / Async — 有需求时再实现
- Retry 策略细化 — 遇到重试误吞时再改
