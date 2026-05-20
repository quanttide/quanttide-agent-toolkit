# 设计调研状态

调研日期：2026-05-20

## 实际重构评价

用量潮内部 9 个 Python 项目验证标准库的可替换性，合计 −529 行，零运行时问题。

| 项目 | 旧方式 | 行变化 |
|------|--------|--------|
| `code-agent` | 自写 LlmClient + ToolDef + dict | −92 |
| `qtcloud-connect/provider` | requests.post + 手动解析 | −62 |
| `qtcloud-think/cli` | openai SDK | −41 |
| `qtcloud-think/provider` | openai SDK | −55 |
| `qtcloud-write/provider` | openai SDK | −140 |
| `qtcloud-think/examples` | urllib + Ollama /api/generate | −68 |
| `qtcloud-asset/examples` | subprocess llm CLI | −26 |
| `qtcloud-finance/cli` | requests + Ollama /api/generate | −45 |

### 暴露的问题

| 问题 | 处理 |
|------|------|
| `chat_once` 模式 | 无需修复，`chat([dict])` 更统一 |
| `usage` 访问啰嗦 | 无需修复，`resp.usage or Usage()` 即可 |
| 默认 base_url 不匹配 | 已全部切 DeepSeek，默认值正确 |
| `thinking` 不通用 | Qwen 已弃用，仅 DeepSeek 无需 extra_body |
