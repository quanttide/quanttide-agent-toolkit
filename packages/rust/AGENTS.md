# AGENTS.md

## Rust 包

单体包 `quanttide-agent-toolkit`，无外部 Rust 依赖。智能体相关类型自包含。

### 构建

```bash
cargo build
cargo test
```

### 更新

修改后先提交推送本仓，再更新主仓库的子模块指针。
