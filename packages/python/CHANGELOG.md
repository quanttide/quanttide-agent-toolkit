# CHANGELOG

## [0.2.1] - 2026-05-20
## [0.2.3] - 2026-05-21

### Fixed

- 修复 Vault 密钥认证失败问题
- 修复 pydantic-settings 依赖版本冲突

## [0.2.2] - 2026-05-20

- Fix: ActionParser fallback to {} when LLM returns invalid JSON


- Fix: ReActAgent uses `role="user"` for tool results (DeepSeek API compat)
- Add `LLM.complete()` method, deprecate `chat()` (removed in v0.3.0)

## [0.2.0] - 2026-05-20

**Breaking changes:**

- `ToolDef` removed. Use `ToolSchema` instead. (`ToolDef` was an alias, now gone.)

**New features:**

- `config` module with `Settings` class using `pydantic-settings`, supporting env vars, `.env`, and Vault
- `LLM()` now accepts `None` for all params, falling back to global `settings`
- `Usage.from_api()` with standardized field names (`input_cached_tokens` / `input_uncached_tokens` / `reasoning_tokens`)
- `Tool` inherits `ToolSchema`, adds `executor` and `execute()` method

**Module restructuring:**

- `message.py` — `Message`, `ChatResponse`
- `tool.py` — `ToolSchema`, `ToolCall`, `Tool`
- `cost.py` — `Usage`
- `config.py` — `Settings`
- `llm.py` — `LLM`, `LLMError` (slimmed)
- `agent.py` — `Action`, `ActionParser`, `ReActAgent`

## [0.1.1] - 2026-05-20

- Add `Message` model with typed `role` and `to_dict()` serialization
- Add `Action` model and `ActionParser` for ReAct protocol parsing
- Add `ReActAgent` with configurable Thought → Action → Observation loop
- Add `Tool` model with schema + executor for Agent tool use

## [0.1.0] - 2026-05-20

- LLM class with unified `chat()` interface
- ToolDef / ToolCall / Usage / ChatResponse models
- Retry on HTTP errors
- Thinking mode support (DeepSeek)
- Only dependency: httpx + pydantic

## [0.1.0-alpha.1] - 2026-05-20

- Initial alpha release (same as v0.1.0)
