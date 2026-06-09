use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolSchema {
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub parameters: Option<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolCall {
    pub id: String,
    pub name: String,
    pub arguments: String,
}

pub trait Executor: Send + Sync {
    fn execute(&self, input: &Value) -> String;
}

pub struct Tool {
    pub schema: ToolSchema,
    pub executor: Option<Box<dyn Executor>>,
}

impl Tool {
    pub fn new(name: &str, description: &str) -> Self {
        Self {
            schema: ToolSchema {
                name: name.to_string(),
                description: description.to_string(),
                parameters: None,
            },
            executor: None,
        }
    }

    pub fn execute(&self, input: &Value) -> String {
        match &self.executor {
            Some(f) => f.execute(input),
            None => format!("未知工具: {}", self.schema.name),
        }
    }
}
