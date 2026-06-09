use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct Usage {
    #[serde(default)]
    pub input_tokens: u32,
    #[serde(default)]
    pub output_tokens: u32,
    #[serde(default)]
    pub total_tokens: u32,
    #[serde(default)]
    pub input_cached_tokens: u32,
    #[serde(default)]
    pub input_uncached_tokens: u32,
    #[serde(default)]
    pub reasoning_tokens: u32,
}

impl Usage {
    pub fn from_api(data: &serde_json::Value) -> Option<Self> {
        if !data.is_object() {
            return None;
        }
        let prompt = data.get("prompt_tokens").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        let completion = data.get("completion_tokens").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        let total = data.get("total_tokens").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        let cached = data.get("prompt_cache_hit_tokens").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        let uncached = data.get("prompt_cache_miss_tokens").and_then(|v| v.as_u64()).unwrap_or(0) as u32;
        let details = data.get("completion_tokens_details");
        let reasoning = details
            .and_then(|d| d.get("reasoning_tokens"))
            .and_then(|v| v.as_u64())
            .unwrap_or(0) as u32;

        Some(Self {
            input_tokens: prompt,
            output_tokens: completion,
            total_tokens: total,
            input_cached_tokens: cached,
            input_uncached_tokens: uncached,
            reasoning_tokens: reasoning,
        })
    }
}
