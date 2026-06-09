use std::fmt;

use serde_json::Value;

use crate::config::Settings;
use crate::cost::Usage;
use crate::message::{ChatResponse, Message};
use crate::tool::{ToolCall, ToolSchema};

#[derive(Debug)]
pub struct LLMError(pub String);

impl fmt::Display for LLMError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "LLM error: {}", self.0)
    }
}

impl std::error::Error for LLMError {}

pub trait HttpClient: Send + Sync {
    fn post_json(&self, url: &str, auth: &str, body: &Value) -> Result<Value, LLMError>;
}

pub struct UreqClient;

impl HttpClient for UreqClient {
    fn post_json(&self, url: &str, auth: &str, body: &Value) -> Result<Value, LLMError> {
        let resp = ureq::post(url)
            .set("Authorization", auth)
            .set("Content-Type", "application/json")
            .send_json(body)
            .map_err(|e| LLMError(format!("request failed: {}", e)))?;
        resp.into_json()
            .map_err(|e| LLMError(format!("parse failed: {}", e)))
    }
}

pub struct LLM {
    model: String,
    base_url: String,
    api_key: String,
    client: Box<dyn HttpClient>,
}

impl Default for LLM {
    fn default() -> Self {
        let settings = Settings::from_env();
        Self::new(&settings.llm_model, &settings.llm_base_url, &settings.llm_api_key)
    }
}

impl LLM {
    pub fn new(model: &str, base_url: &str, api_key: &str) -> Self {
        Self {
            model: model.to_string(),
            base_url: base_url.trim_end_matches('/').to_string(),
            api_key: api_key.to_string(),
            client: Box::new(UreqClient),
        }
    }

    pub fn with_client(model: &str, base_url: &str, api_key: &str, client: Box<dyn HttpClient>) -> Self {
        Self {
            model: model.to_string(),
            base_url: base_url.trim_end_matches('/').to_string(),
            api_key: api_key.to_string(),
            client,
        }
    }

    pub fn complete(
        &self,
        messages: &[Message],
        options: CompleteOptions,
    ) -> Result<ChatResponse, LLMError> {
        let body = self.build_body(messages, &options);
        let url = format!("{}/chat/completions", self.base_url);
        let auth = format!("Bearer {}", self.api_key);
        let data = self.client.post_json(&url, &auth, &body)?;
        parse_response(&data, &self.model)
    }

    fn build_body(&self, messages: &[Message], options: &CompleteOptions) -> Value {
        let msg_list: Vec<Value> = messages.iter().map(|m| m.to_dict()).collect();

        let mut body = serde_json::Map::new();
        body.insert("model".to_string(), Value::String(options.model.clone().unwrap_or_else(|| self.model.clone())));
        body.insert("messages".to_string(), Value::Array(msg_list));

        if let Some(t) = options.temperature {
            body.insert("temperature".to_string(), Value::Number(serde_json::Number::from_f64(t).unwrap()));
        }
        if let Some(m) = options.max_tokens {
            body.insert("max_tokens".to_string(), Value::Number(m.into()));
        }
        if let Some(p) = options.top_p {
            body.insert("top_p".to_string(), Value::Number(serde_json::Number::from_f64(p).unwrap()));
        }
        if let Some(s) = &options.stop {
            match s {
                Stop::Single(st) => body.insert("stop".to_string(), Value::String(st.clone())),
                Stop::List(list) => body.insert("stop".to_string(), Value::Array(list.iter().map(|s| Value::String(s.clone())).collect())),
            };
        }
        if let Some(fp) = options.frequency_penalty {
            body.insert("frequency_penalty".to_string(), Value::Number(serde_json::Number::from_f64(fp).unwrap()));
        }
        if let Some(pp) = options.presence_penalty {
            body.insert("presence_penalty".to_string(), Value::Number(serde_json::Number::from_f64(pp).unwrap()));
        }
        if let Some(re) = &options.reasoning_effort {
            body.insert("reasoning_effort".to_string(), Value::String(re.clone()));
        }
        if let Some(tc) = &options.tool_choice {
            body.insert("tool_choice".to_string(), Value::String(tc.clone()));
        }
        if let Some(rf) = &options.response_format {
            body.insert("response_format".to_string(), rf.clone());
        }
        if let Some(thinking) = options.thinking {
            body.insert("thinking".to_string(), serde_json::json!({"type": if thinking { "enabled" } else { "disabled" }}));
        }
        if let Some(tools) = &options.tools {
            let tool_list: Vec<Value> = tools
                .iter()
                .map(|t| {
                    serde_json::json!({
                        "type": "function",
                        "function": {
                            "name": t.name,
                            "description": t.description,
                            "parameters": t.parameters.as_ref().unwrap_or(&serde_json::json!({"type": "object", "properties": {}})),
                        }
                    })
                })
                .collect();
            body.insert("tools".to_string(), Value::Array(tool_list));
        }

        Value::Object(body)
    }
}

pub fn parse_response(data: &Value, default_model: &str) -> Result<ChatResponse, LLMError> {
    let choice = data["choices"][0].clone();
    let msg = choice["message"].clone();

    let tool_calls = msg["tool_calls"].as_array().map(|arr| {
        arr.iter()
            .map(|tc| ToolCall {
                id: tc["id"].as_str().unwrap_or("").to_string(),
                name: tc["function"]["name"].as_str().unwrap_or("").to_string(),
                arguments: tc["function"]["arguments"].as_str().unwrap_or("").to_string(),
            })
            .collect()
    });

    let usage_raw = data.get("usage");
    let usage = usage_raw.and_then(Usage::from_api);

    Ok(ChatResponse {
        content: msg["content"].as_str().unwrap_or("").to_string(),
        model: data["model"].as_str().unwrap_or(default_model).to_string(),
        finish_reason: choice["finish_reason"].as_str().unwrap_or("stop").to_string(),
        reasoning_content: msg["reasoning_content"].as_str().map(String::from),
        tool_calls,
        usage,
    })
}

pub struct CompleteOptions {
    pub model: Option<String>,
    pub temperature: Option<f64>,
    pub max_tokens: Option<u32>,
    pub top_p: Option<f64>,
    pub stop: Option<Stop>,
    pub frequency_penalty: Option<f64>,
    pub presence_penalty: Option<f64>,
    pub thinking: Option<bool>,
    pub reasoning_effort: Option<String>,
    pub tools: Option<Vec<ToolSchema>>,
    pub tool_choice: Option<String>,
    pub response_format: Option<Value>,
}

impl Default for CompleteOptions {
    fn default() -> Self {
        Self {
            model: None,
            temperature: None,
            max_tokens: None,
            top_p: None,
            stop: None,
            frequency_penalty: None,
            presence_penalty: None,
            thinking: None,
            reasoning_effort: None,
            tools: None,
            tool_choice: None,
            response_format: None,
        }
    }
}

/// Parse structured output from LLM response text.
///
/// Handles markdown code blocks (` ```json `, ` ```yaml `),
/// raw JSON objects `{}`, and raw JSON arrays `[]`.
pub fn parse_structured_output(response: &str) -> Result<Value, String> {
    for marker in &["```json", "```JSON", "```yaml", "```YAML"] {
        if let Some(start) = response.find(marker) {
            let s = start + marker.len();
            let e = response[s..].find("```").map(|i| s + i).unwrap_or(response.len());
            let trimmed = response[s..e].trim();
            if let Ok(v) = serde_json::from_str(trimmed) {
                return Ok(v);
            }
        }
    }
    if let Some(start) = response.find('{') {
        let e = response.rfind('}').map(|i| i + 1).unwrap_or(response.len());
        let trimmed = response[start..e].trim();
        if let Ok(v) = serde_json::from_str(trimmed) {
            return Ok(v);
        }
    }
    if let Some(start) = response.find('[') {
        let e = response.rfind(']').map(|i| i + 1).unwrap_or(response.len());
        let trimmed = response[start..e].trim();
        if let Ok(v) = serde_json::from_str(trimmed) {
            return Ok(v);
        }
    }
    Err("No valid JSON found in response".to_string())
}

pub enum Stop {
    Single(String),
    List(Vec<String>),
}
