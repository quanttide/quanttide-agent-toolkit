# `quanttide-agent`

量潮智能体标准Python工具箱

## 安装

```shell
pip install git+https://github.com/quanttide/quanttide-agent-toolkit.git
```

## 模型配置

默认配置使用 DeepSeek。MiMo 和 GLM 使用同一个 OpenAI 兼容客户端，只需要切换对应的配置：

```python
from quanttide_agent import LLM
from quanttide_agent.config import settings

mimo = LLM(
    model=settings.mimo_model,
    base_url=settings.mimo_base_url,
    api_key=settings.mimo_api_key,
)

glm = LLM(
    model=settings.glm_model,
    base_url=settings.glm_base_url,
    api_key=settings.glm_api_key,
)
```

可通过以下环境变量覆盖配置：

```shell
MIMO_API_KEY=...
MIMO_MODEL=mimo-v2.5
MIMO_BASE_URL=https://api.xiaomimimo.com/v1

GLM_API_KEY=...
GLM_MODEL=glm-5.3
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
```

`ZHIPUAI_API_KEY` 和 `ZAI_API_KEY` 也可作为 GLM API Key 的兼容别名。

## 贡献者

- 量潮成员：[@Guo-Zhang](https://github.com/Guo-Zhang)

## 许可证

[Apache 2.0](LICENSE)
