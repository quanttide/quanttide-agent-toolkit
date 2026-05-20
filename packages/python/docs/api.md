# API 设计风格

## 核心理念

```
LLM   = 大脑  → 文本生成/聊天（本项目）
Tool  = 器官  → 与外界交互的"手/眼/口"
Agent = 完整框架 → 大脑 + 器官 + 规划/记忆/多步推理
```

本项目只做 `LLM` 层。`Agent` 层由上层框架构建。

## 接口风格

### 一条方法

```python
llm.chat(messages, *, ...) → ChatResponse
```

不拆 Client / Service，不拆 `chat_once` / `complete` / `think`。

### 动词命名，不照搬 REST 协议

```python
# 不用的命名（REST 协议直译）
response = llm.completion(...)
response.choices[0].message.content

# 使用的命名（Python 风格）
response = llm.chat(...)
response.content
```

### 扁平响应

`ChatResponse.content` 直接可读，不需 `.choices[0].message.`。

### 消息模型

输入输出使用 plain dict（OpenAI 原生格式），不引入 LangChain 式的类继承体系：

```python
messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
]
```

## 参数设计

所有可选参数通过 keyword-only 传入：

```python
resp = llm.chat(messages, temperature=0.7, max_tokens=1024, tools=[...])
```

Provider 特有参数（如 DeepSeek 的 `thinking`）以命名参数暴露，避免需要 `extra_body` 透传。

## 依赖

仅 `httpx` + `pydantic`，零框架依赖。
