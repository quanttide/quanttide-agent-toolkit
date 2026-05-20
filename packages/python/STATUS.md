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
| 消息模型 | 两者都不取 | 单 `Message` 模型 + `Literal` 约束 `role`，拒绝 Java 风格类分层 |
| 多提供商 | 两者都不取 | 通过 `base_url + model` 配置，不做内部路由 |
| 工具调用 | OpenAI 标准 | 遵循 OpenAI Function Calling |
| 依赖 | 两者都不取 | 仅 `httpx` + `pydantic`，零框架依赖 |

## 设计决策

### 消息模型：拒绝 Java 风格类分层

**结论**：不采用 LangChain 的 `SystemMessage` / `UserMessage` / `AIMessage` / `ToolMessage` 类继承体系。

**理由**：
- LangChain 的消息分层是 Java-style OO 设计，每个角色一个类 → 继承 → 多态，偏重
- Python 中可以用更轻量的方式同时获得类型安全和自文档：
  - 单 `Message` 模型 + `Literal["system", "user", "assistant", "tool"]` 约束 `role`
  - 或 TypedDict + TypeAlias
- 符合本项目的"轻量、零框架依赖"定位

**参考**：
- OpenAI API 原生格式（纯 dict `{"role": "user", "content": "..."}`）本身就很 Pythonic

### API 命名：拒绝 REST 协议直译

**结论**：不照搬 OpenAI/LiteLLM 的 REST 协议命名，以 Python 可读性优先。

**问题**：
- `completion()` — 是名词而非动词，源于端点 `/v1/chat/completions`，Python 中应使用动词 `complete()` 或领域词 `chat()`、`generate()`
- `response.choices[0].message.content` — HTTP JSON 结构 `response > choices[] > message > content` 的直译，两层索引（`choices[0]` + `.message.`）对 Python 调用者不友好
- `response.content` 或 `response.text` 更直接

**原则**：
- 动词作函数名（`complete()`, `chat()`），不用协议名词
- 扁平化响应：`.content` 直接可读，不需 `.choices[0].message.`

### 核心抽象：LLM 是大脑，Tool 是器官，Agent 是完整框架

**结论**：`LLM` 类负责核心文本生成；Tool 是 LLM 与外界交互的"器官"；Agent 是上层框架，组合 LLM + Tools + 规划/记忆/多步推理。

**理由**：
- pydantic-ai 的教训：把一个单次 LLM 调用包装成 `Agent` 类，稀释了"Agent"的概念
- Agent 应具备工具调用、多步推理、自主决策等能力，单一 LLM 调用不配叫 Agent
- 本项目核心抽象应如实反映其职责：LLM 文本生成/聊天
- `LLM` 是大脑，`Tool` 是器官（手/眼/口），`Agent` 是使用大脑+器官的完整框架——三层职责清晰

**最终命名**：`LLM`（见下节）

### Client/Service 封装：已定

**结论**：核心类名为 `LLM`，不拆 Client/Service。重试/回退等能力通过方法参数提供。

**理由**：
- `LLM.chat(retry=3, fallback=...)` 自然简洁，无需额外后缀
- `Client`/`Service` 是架构术语，对用户暴露这些分类是过度设计
- 参考 Instructor 的 `client.create()` 本质也是类，但叫 `LLM` 更直接

**最终命名**：`LLM` 类，含 `chat()` / `complete()` 等方法

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
