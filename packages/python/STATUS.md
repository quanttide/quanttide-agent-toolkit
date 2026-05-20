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

## 第三方评价要点

- LiteLLM 定位为 LLM **调用抽象层**（薄路由），适合做网关/代理
- LangChain 定位为 Agent **应用框架**（厚生态），适合做完整应用
- 本项目介于两者之间：取 LiteLLM 的统一接口风格，消息模型走自己的轻量路线，砍掉一切外部依赖

## 实际重构评价

2026-05-20，用量潮内部 9 个 Python 项目验证标准库的可替换性。

### 替换范围

| 项目 | 旧方式 | 替换代码量 | 结果 |
|------|--------|-----------|------|
| `code-agent` | 自写 LlmClient + ToolDef + dict | −92 行 | 完全替换 |
| `qtcloud-connect/provider` | requests.post + 手动解析 | −62 行 | 完全替换 |
| `qtcloud-think/cli` | openai SDK | −41 行 | 完全替换 |
| `qtcloud-think/provider` | openai SDK | −55 行 | 完全替换 |
| `qtcloud-write/provider` | openai SDK | −140 行 | 完全替换 |
| `qtcloud-think/examples` | urllib + Ollama /api/generate | −68 行 | 完全替换 |
| `qtcloud-asset/examples` | subprocess llm CLI | −26 行 | 完全替换 |
| `qtcloud-finance/cli` | requests + Ollama /api/generate | −45 行 | 完全替换 |
| 合计 | — | −529 行 | 零运行时问题 |

### 暴露的问题

| 问题 | 出现次数 | 处理 |
|------|---------|------|
| `chat_once(system, user)` 重复实现 | 3/6 项目 | 无需修复，`chat([dict])` 更统一 |
| `usage` 访问啰嗦 | 每个项目 | 无需修复，`resp.usage or Usage()` 即可 |
| 默认 base_url 不匹配 | 3/6 项目 | 已全部切 DeepSeek，默认值正确 |
| `thinking` / `extra_body` 不通用 | 跨 Provider | Qwen 已弃用，仅 DeepSeek 无需 extra_body |
