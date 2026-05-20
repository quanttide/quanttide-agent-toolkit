# ROADMAP

## v0.2.x — 已完成

- [x] `LLM.complete()` 替换 `chat()`（chat 标记废弃，v0.3.0 移除）
- [x] `ReActAgent` + `ActionParser` + `Tool` 进入标准库
- [x] `config` 模块 with pydantic-settings + vault 支持
- [x] `Usage.from_api()` 标准化字段
- [x] 100% 测试覆盖率
- [x] 在 `qtcloud-knowl` 项目中实地验证通过

## v0.3.0 计划

- 移除 `LLM.chat()`（v0.2.1 标记废弃，按约定 v0.3.0 移除）

## 待考察

- Streaming / Async — 有需求时再实现
- Retry 策略细化 — 遇到重试误吞时再改
