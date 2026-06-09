use serde::{Deserialize, Serialize};
use serde_json::Value;

use crate::cost::Usage;
use crate::tool::ToolCall;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tool_call_id: Option<String>,
}

impl Message {
    pub fn new(role: &str, content: &str) -> Self {
        Self {
            role: role.to_string(),
            content: content.to_string(),
            tool_call_id: None,
        }
    }

    pub fn to_dict(&self) -> Value {
        let mut map = serde_json::Map::new();
        map.insert("role".to_string(), Value::String(self.role.clone()));
        map.insert("content".to_string(), Value::String(self.content.clone()));
        if let Some(ref id) = self.tool_call_id {
            map.insert("tool_call_id".to_string(), Value::String(id.clone()));
        }
        Value::Object(map)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatResponse {
    pub content: String,
    pub model: String,
    #[serde(default = "default_finish_reason")]
    pub finish_reason: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub reasoning_content: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tool_calls: Option<Vec<ToolCall>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub usage: Option<Usage>,
}

fn default_finish_reason() -> String {
    "stop".to_string()
}
