from __future__ import annotations

from quanttide_agent.config import Settings


def test_provider_defaults():
    settings = Settings(_env_file=None)

    assert settings.llm_model == "deepseek-v4-flash"
    assert settings.llm_base_url == "https://api.deepseek.com"
    assert settings.mimo_model == "mimo-v2.5"
    assert settings.mimo_base_url == "https://api.xiaomimimo.com/v1"
    assert settings.glm_model == "glm-5.3"
    assert settings.glm_base_url == "https://open.bigmodel.cn/api/paas/v4"


def test_mimo_settings_read_mimo_environment_variables(monkeypatch):
    monkeypatch.setenv("MIMO_MODEL", "mimo-test")
    monkeypatch.setenv("MIMO_BASE_URL", "https://mimo.example/v1")
    monkeypatch.setenv("MIMO_API_KEY", "mimo-key")

    settings = Settings(_env_file=None)

    assert settings.mimo_model == "mimo-test"
    assert settings.mimo_base_url == "https://mimo.example/v1"
    assert settings.mimo_api_key == "mimo-key"


def test_glm_settings_accept_zhipu_api_key_alias(monkeypatch):
    monkeypatch.delenv("GLM_API_KEY", raising=False)
    monkeypatch.setenv("ZHIPUAI_API_KEY", "zhipu-key")

    settings = Settings(_env_file=None)

    assert settings.glm_api_key == "zhipu-key"


def test_llm_settings_accept_deepseek_api_key_alias(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-key")

    settings = Settings(_env_file=None)

    assert settings.llm_api_key == "deepseek-key"
