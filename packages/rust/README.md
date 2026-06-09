# quanttide-agent

量潮智能体工具箱 Rust 包。提供 LLM 客户端与消息/工具调用数据模型。

## 用法

```toml
[dependencies]
quanttide-agent = "0.1.0-alpha.1"
```

```rust
use quanttide_agent::{
    message::Message,
    llm::{LLM, CompleteOptions},
};

let llm = LLM::default();
let resp = llm.complete(
    &[Message::new("user", "你好")],
    CompleteOptions::default(),
).unwrap();
println!("{}", resp.content);
```

## 模块

| 模块 | 说明 |
|------|------|
| `message` | Message (role/content/tool_call_id), ChatResponse |
| `tool` | ToolSchema, ToolCall, Tool + Executor trait |
| `cost` | Usage token统计，from_api() 解析器 |
| `config` | Settings 环境变量配置 |
| `llm` | LLM 客户端，CompleteOptions，HttpClient trait |

## 环境变量

- `LLM_MODEL`: 模型名（默认 `deepseek-v4-flash`）
- `LLM_BASE_URL`: API 地址（默认 `https://api.deepseek.com`）
- `LLM_API_KEY`: API 密钥

## 许可

MIT
