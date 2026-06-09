# AGENTS.md

## Rust 包

单体包 `quanttide-agent`，提供 LLM 客户端和数据模型（消息、工具调用、用量统计）。

### 构建

```bash
cargo build
cargo test
```

### 更新

修改后先提交推送本仓，再更新主仓库的子模块指针。
