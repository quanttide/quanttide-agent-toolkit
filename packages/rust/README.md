# quanttide-agent

量潮智能体工具箱 Rust 包。提供 LLM 客户端与消息/工具调用数据模型。

## 用法

```toml
[dependencies]
quanttide-agent = "0.1.2"
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

| `MIMO_MODEL` | MiMo 模型名 | `mimo-v2.5` |

| `MIMO_BASE_URL` | MiMo API 地址 | `https://api.xiaomimimo.com/v1` |

| `MIMO_API_KEY` | MiMo API 密钥 | — |

| `GLM_MODEL` | GLM 模型名 | `glm-5.3` |

| `GLM_BASE_URL` | GLM API 地址 | `https://open.bigmodel.cn/api/paas/v4` |

| `GLM_API_KEY` | GLM API 密钥 | — |

| `ZHIPUAI_API_KEY` | GLM API 密钥兼容别名 | — |

| `ZAI_API_KEY` | GLM API 密钥兼容别名 | — |



优先级：`LLM_API_KEY` > `DEEPSEEK_API_KEY` > 空字符串。社区习惯用 `DEEPSEEK_API_KEY`，量潮项目建议两个都设（`LLM_API_KEY` 设为 `$DEEPSEEK_API_KEY` 的别名）。

使用 MiMo 或 GLM 时，将对应的 `model`、`base_url` 和 `api_key` 传给 `LLM::new()`：

```rust
use quanttide_agent::LLM;

let mimo = LLM::new(
    "mimo-v2.5",
    "https://api.xiaomimimo.com/v1",
    &std::env::var("MIMO_API_KEY").unwrap_or_default(),
);

let glm = LLM::new(
    "glm-5.3",
    "https://open.bigmodel.cn/api/paas/v4",
    &std::env::var("GLM_API_KEY").unwrap_or_default(),
);
```

## 许可

MIT
