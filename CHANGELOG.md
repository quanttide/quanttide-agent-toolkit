# CHANGELOG

## [python/0.4.0] - 2026-06-23

### Added

- `AsyncLLM` class 异步 `complete()` 接口
- `BaseLLM` 基类，公开 `build_chat_body()` 和 `parse_chat_response()` 方法
- 异步测试覆盖（pytest-asyncio）

### Changed

- `LLM` 重构为继承 `BaseLLM`，接口完全向后兼容
