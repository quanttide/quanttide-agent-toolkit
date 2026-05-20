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

`thinking` / `reasoning_effort` 保留为 DeepSeek 原生命名参数。其他 Provider 有不同参数时，用调用方自行处理，库不增加 Provider 无关的抽象层。

- 原则：**DeepSeek 优先**，不提前做多 Provider 兼容

## 待考察

- Streaming / Async — 有需求时再实现
- Retry 策略细化 — 遇到重试误吞时再改
