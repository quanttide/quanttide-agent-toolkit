# CHANGELOG

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
