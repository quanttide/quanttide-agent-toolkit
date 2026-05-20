# 设计调研状态

调研日期：2026-05-20

## LiteLLM vs LangChain API 设计对比

### LiteLLM 路线

参考来源：[官方文档](https://docs.litellm.ai/docs/)

| 特征 | 说明 |
|------|------|
| 统一入口 | 单函数 `completion(model="provider/name", messages=[...])` |
| 提供商命名 | `openai/gpt-4o`、`anthropic/claude-3`、`vertex_ai/gemini-1.5` 等前缀路由 |
| 输出一致 | 返回值统一为 OpenAI Chat Completions 格式 `ModelResponse` |
| 异常统一 | 各提供商错误映射为 OpenAI 异常体系 |
| 内置设施 | Router（fallback/重试/负载均衡）、`response_cost` 追踪、observability 回调 |
| 网关模式 | 额外提供 Proxy Server（LLM Gateway） |
| 依赖 | heavy——`litellm` 包自带 100+ 提供商映射和格式转换 |

### LangChain 路线

参考来源：[官方文档](https://python.langchain.com/docs/introduction/)

| 特征 | 说明 |
|------|------|
| Agent 抽象 | `create_agent(model="provider:name", tools=[...])` |
| 消息层次 | `SystemMessage` / `UserMessage` / `AIMessage` / `ToolMessage` 类型体系 |
| 提供商命名 | `openai:gpt-5.4`、`google_genai:gemini-2.5`、`claude-sonnet-4-6` |
| 底层框架 | 基于 LangGraph（低阶编排引擎），支持持久化执行、人工介入 |
| 生态绑定 | 深度集成 LangSmith（可观测性/评估/部署） |
| 集成包模式 | 每个提供商独立包：`langchain-openai`、`langchain-anthropic` 等 |
| 依赖 | heavy——核心 + 各 provider 包 + LangSmith SDK 组合 |

### 本项目取舍

由 `AGENTS.md` 定义的定位：轻量、无框架依赖、仅依赖 `httpx`。

| 维度 | 取自谁 | 方式 |
|------|--------|------|
| 接口风格 | LiteLLM | 统一 `completion()` 入口，不引入 litellm 包 |
| 消息模型 | LangChain | 分层消息类型，不用 chain 抽象 |
| 多提供商 | 两者都不取 | 通过 `base_url + model` 配置，不做内部路由 |
| 工具调用 | OpenAI 标准 | 遵循 OpenAI Function Calling |
| 依赖 | 两者都不取 | 仅 `httpx`，零框架依赖 |

### 第三方评价要点

- LiteLLM 定位为 LLM **调用抽象层**（薄路由），适合做网关/代理
- LangChain 定位为 Agent **应用框架**（厚生态），适合做完整应用
- 本项目介于两者之间：取 LiteLLM 的统一接口风格，取 LangChain 的消息分类方法，砍掉一切外部依赖
