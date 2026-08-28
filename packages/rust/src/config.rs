use std::env;

pub struct Settings {
    pub llm_model: String,
    pub llm_base_url: String,
    pub llm_api_key: String,
    pub mimo_model: String,
    pub mimo_base_url: String,
    pub mimo_api_key: String,
    pub glm_model: String,
    pub glm_base_url: String,
    pub glm_api_key: String,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            llm_model: env::var("LLM_MODEL").unwrap_or_else(|_| "deepseek-v4-flash".to_string()),
            llm_base_url: env::var("LLM_BASE_URL")
                .unwrap_or_else(|_| "https://api.deepseek.com".to_string()),
            llm_api_key: env::var("LLM_API_KEY")
                .or_else(|_| env::var("DEEPSEEK_API_KEY"))
                .unwrap_or_default(),
            mimo_model: env::var("MIMO_MODEL").unwrap_or_else(|_| "mimo-v2.5".to_string()),
            mimo_base_url: env::var("MIMO_BASE_URL")
                .unwrap_or_else(|_| "https://api.xiaomimimo.com/v1".to_string()),
            mimo_api_key: env::var("MIMO_API_KEY").unwrap_or_default(),
            glm_model: env::var("GLM_MODEL").unwrap_or_else(|_| "glm-5.3".to_string()),
            glm_base_url: env::var("GLM_BASE_URL")
                .unwrap_or_else(|_| "https://open.bigmodel.cn/api/paas/v4".to_string()),
            glm_api_key: env::var("GLM_API_KEY")
                .or_else(|_| env::var("ZHIPUAI_API_KEY"))
                .or_else(|_| env::var("ZAI_API_KEY"))
                .unwrap_or_default(),
        }
    }
}

impl Settings {
    pub fn from_env() -> Self {
        Self::default()
    }
}
