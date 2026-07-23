use std::env;

pub struct Settings {
    pub llm_model: String,
    pub llm_base_url: String,
    pub llm_api_key: String,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            llm_model: env::var("LLM_MODEL").unwrap_or_else(|_| "deepseek-v4-flash".to_string()),
            llm_base_url: env::var("LLM_BASE_URL").unwrap_or_else(|_| "https://api.deepseek.com".to_string()),
            llm_api_key: env::var("LLM_API_KEY")
                .or_else(|_| env::var("DEEPSEEK_API_KEY"))
                .unwrap_or_default(),
        }
    }
}

impl Settings {
    pub fn from_env() -> Self {
        Self::default()
    }
}
