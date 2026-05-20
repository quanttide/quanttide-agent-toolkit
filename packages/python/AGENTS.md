# AGENTS

## 规划

`quanttide-agent-toolkit` 提供 LLM 调用的统一封装。定位：轻量、无框架依赖、仅依赖 `httpx`。

## 参考来源

- **LiteLLM**：`completion()` 统一函数设计、`model="provider/name"` 命名规则、`fallbacks` 参数、`response_cost` 内置追踪
- **LangChain**：消息类型分层（SystemMessage / UserMessage / AIMessage / ToolMessage）、消息 → API 格式的序列化、工具定义 Schema
- **code-agent LlmClient**：httpx 实现基础、工具调用循环、token/cost 统计、run_loop 多步对话

## 设计原则

- 不引入 `litellm`、`langchain`、`pydantic-ai` 等外部框架
- 多提供商切换通过 `base_url` + `model` 配置实现，不做内部路由（兼容所有 OpenAI 格式 API：DeepSeek / vLLM / Ollama）
- 工具调用协议遵循 OpenAI Function Calling 标准
- 依赖仅限 `httpx`
