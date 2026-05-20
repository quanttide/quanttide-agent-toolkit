"""Configuration for quanttide-agent.

Supports env vars, .env files, and Vault via pydantic-settings + pydantic-settings-vault.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

try:
    from pydantic_vault import VaultSettingsSource

    _HAS_VAULT = True
except ImportError:
    VaultSettingsSource = None  # type: ignore
    _HAS_VAULT = False


class Settings(BaseSettings):
    """Global settings for quanttide-agent.

    Field names follow `llm_*` convention for env var mapping::

        LLM_MODEL=deepseek-v4-flash
        LLM_BASE_URL=https://api.deepseek.com
        LLM_API_KEY=sk-...

    Vault paths can be configured via ``json_schema_extra`` on each field.
    """

    llm_model: str = "deepseek-v4-flash"
    llm_base_url: str = "https://api.deepseek.com"

    llm_api_key: str = Field(
        default="",
        description="LLM API key",
        json_schema_extra=(
            {"vault_secret_path": "quanttide/deepseek", "vault_secret_key": "api_key"}
            if _HAS_VAULT
            else {}
        ),
    )

    model_config = {}

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        sources = (init_settings, env_settings, dotenv_settings)
        if _HAS_VAULT:
            sources += (VaultSettingsSource(settings_cls),)
        return sources + (file_secret_settings,)


settings = Settings()
