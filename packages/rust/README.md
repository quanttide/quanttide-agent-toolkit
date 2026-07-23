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

| 变量 | 说明 | 默认值 |

|------|------|--------|

| `LLM_MODEL` | 模型名 | `deepseek-v4-flash` |

| `LLM_BASE_URL` | API 地址 | `https://api.deepseek.com` |

| `LLM_API_KEY` | API 密钥（优先） | — |

| `DEEPSEEK_API_KEY` | API 密钥（`LLM_API_KEY` 未设置时使用） | — |



优先级：`LLM_API_KEY` > `DEEPSEEK_API_KEY` > 空字符串。社区习惯用 `DEEPSEEK_API_KEY`，量潮项目建议两个都设（`LLM_API_KEY` 设为 `$DEEPSEEK_API_KEY` 的别名）。

## 许可

MIT
