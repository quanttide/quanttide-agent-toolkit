# ROADMAP

## v0.2.x 目标

- [ ] 确认 v0.2.0 在实际项目中的兼容性
- [ ] 收集使用反馈

## 待考察方向

以下问题暂不排期。

### Provider 特化参数

`chat()` 的 `thinking` / `reasoning_effort` 参数是 DeepSeek 特化的。

- 触发条件：需要支持 DeepSeek 以外的 Provider

### Streaming / Async

- 触发条件：有项目需要流式输出

### Retry 策略

当前对所有 4xx/5xx 统一重试。

- 触发条件：实际遇到重试误吞问题
