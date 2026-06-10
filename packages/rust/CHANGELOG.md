# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0-rc.1] - 2026-06-10

### Changed

- API 冻结，进入候选发布阶段
- 版本号从 `0.1.0-alpha.2` 升为 `0.1.0-rc.1`

## [0.1.0-alpha.2] - 2026-06-09

### Added

- parse_structured_output: extract JSON from LLM response text

## [0.1.0-alpha.1] - 2026-06-09

### Added

- LLM client with `ureq` HTTP transport and mock support
- Message types: Message (role/content/tool_call_id), ChatResponse
- Tool types: ToolSchema, ToolCall, Tool with Executor trait
- Usage tracking: token counts with `from_api()` parser
- Config: Settings from env vars (LLM_MODEL, LLM_BASE_URL, LLM_API_KEY)
