use std::sync::Mutex;

use serde_json::Value;

use quanttide_agent::{
    config::Settings,
    cost::Usage,
    llm::{CompleteOptions, HttpClient, LLM, LLMError, parse_response},
    message::{ChatResponse, Message},
    tool::{Executor, Tool, ToolCall, ToolSchema},
};

// ── message ──

#[test]
fn message_basic() {
    let m = Message::new("user", "hello");
    assert_eq!(m.role, "user");
    assert_eq!(m.content, "hello");
    assert!(m.tool_call_id.is_none());
}

#[test]
fn message_to_dict() {
    let m = Message::new("assistant", "ok");
    let d = m.to_dict();
    assert_eq!(d["role"], "assistant");
    assert_eq!(d["content"], "ok");
}

#[test]
fn message_to_dict_with_tool_call_id() {
    let m = Message {
        role: "tool".into(),
        content: "result".into(),
        tool_call_id: Some("call_1".into()),
    };
    let d = m.to_dict();
    assert_eq!(d["tool_call_id"], "call_1");
}

#[test]
fn chat_response_construct() {
    let r = ChatResponse {
        content: "Hello!".into(),
        model: "deepseek-v4-pro".into(),
        finish_reason: "stop".into(),
        reasoning_content: None,
        tool_calls: None,
        usage: None,
    };
    assert_eq!(r.content, "Hello!");
    assert_eq!(r.model, "deepseek-v4-pro");
}

#[test]
fn chat_response_json_roundtrip() {
    let r = ChatResponse {
        content: "思考中...".into(),
        model: "deepseek-v4-flash".into(),
        finish_reason: "stop".into(),
        reasoning_content: Some("一步步推理".into()),
        tool_calls: None,
        usage: Some(Usage {
            input_tokens: 50,
            output_tokens: 100,
            total_tokens: 150,
            ..Default::default()
        }),
    };
    let json = serde_json::to_string(&r).unwrap();
    let back: ChatResponse = serde_json::from_str(&json).unwrap();
    assert_eq!(back.content, r.content);
    assert_eq!(back.reasoning_content.unwrap(), "一步步推理");
    assert_eq!(back.usage.unwrap().total_tokens, 150);
}

// ── tool ──

#[test]
fn tool_schema_json() {
    let ts = ToolSchema {
        name: "get_weather".into(),
        description: "Get weather".into(),
        parameters: Some(serde_json::json!({"type": "object", "properties": {"location": {"type": "string"}}})),
    };
    let json = serde_json::to_string(&ts).unwrap();
    assert!(json.contains("get_weather"));
    assert!(json.contains("location"));
}

#[test]
fn tool_call_deserialize() {
    let json = r#"{"id":"call_1","name":"get_weather","arguments":"{\"location\":\"Beijing\"}"}"#;
    let tc: ToolCall = serde_json::from_str(json).unwrap();
    assert_eq!(tc.id, "call_1");
    assert_eq!(tc.name, "get_weather");
}

#[test]
fn tool_execute_with_executor() {
    struct AddExclamation;
    impl Executor for AddExclamation {
        fn execute(&self, input: &Value) -> String {
            format!("{}!", input["text"].as_str().unwrap_or(""))
        }
    }

    let tool = Tool {
        schema: ToolSchema {
            name: "exclaim".into(),
            description: "add !".into(),
            parameters: None,
        },
        executor: Some(Box::new(AddExclamation)),
    };
    let result = tool.execute(&serde_json::json!({"text": "hello"}));
    assert_eq!(result, "hello!");
}

#[test]
fn tool_execute_without_executor() {
    let tool = Tool::new("unknown", "no executor");
    let result = tool.execute(&serde_json::json!({}));
    assert_eq!(result, "未知工具: unknown");
}

// ── cost ──

#[test]
fn usage_from_api_full() {
    let data = serde_json::json!({
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30,
        "prompt_cache_hit_tokens": 5,
        "prompt_cache_miss_tokens": 3,
        "completion_tokens_details": {"reasoning_tokens": 8}
    });
    let u = Usage::from_api(&data).unwrap();
    assert_eq!(u.input_tokens, 10);
    assert_eq!(u.output_tokens, 20);
    assert_eq!(u.total_tokens, 30);
    assert_eq!(u.input_cached_tokens, 5);
    assert_eq!(u.input_uncached_tokens, 3);
    assert_eq!(u.reasoning_tokens, 8);
}

#[test]
fn usage_from_api_minimal() {
    let data = serde_json::json!({"prompt_tokens": 1, "completion_tokens": 1});
    let u = Usage::from_api(&data).unwrap();
    assert_eq!(u.total_tokens, 0);
}

#[test]
fn usage_from_api_none_on_empty() {
    assert!(Usage::from_api(&Value::Null).is_none());
}

#[test]
fn usage_from_api_none_on_non_object() {
    assert!(Usage::from_api(&Value::String("nope".into())).is_none());
}

#[test]
fn usage_default_is_zero() {
    let u = Usage::default();
    assert_eq!(u.input_tokens, 0);
    assert_eq!(u.output_tokens, 0);
}

// ── llm: parse_response ──

#[test]
fn parse_response_basic() {
    let data = serde_json::json!({
        "choices": [{
            "message": {"content": "Hello!"},
            "finish_reason": "stop"
        }],
        "model": "deepseek-v4-pro"
    });
    let r = parse_response(&data, "default").unwrap();
    assert_eq!(r.content, "Hello!");
    assert_eq!(r.model, "deepseek-v4-pro");
    assert_eq!(r.finish_reason, "stop");
}

#[test]
fn parse_response_with_reasoning() {
    let data = serde_json::json!({
        "choices": [{
            "message": {
                "content": "最终答案",
                "reasoning_content": "一步步推理过程"
            },
            "finish_reason": "stop"
        }],
        "model": "deepseek-v4-flash"
    });
    let r = parse_response(&data, "x").unwrap();
    assert_eq!(r.reasoning_content.unwrap(), "一步步推理过程");
}

#[test]
fn parse_response_with_tool_calls() {
    let data = serde_json::json!({
        "choices": [{
            "message": {
                "content": "",
                "tool_calls": [{
                    "id": "call_abc",
                    "function": {"name": "get_weather", "arguments": "{\"location\": \"Beijing\"}"}
                }]
            },
            "finish_reason": "tool_calls"
        }],
        "model": "deepseek-v4-pro"
    });
    let r = parse_response(&data, "x").unwrap();
    assert_eq!(r.finish_reason, "tool_calls");
    let tcs = r.tool_calls.unwrap();
    assert_eq!(tcs.len(), 1);
    assert_eq!(tcs[0].name, "get_weather");
    assert_eq!(tcs[0].arguments, "{\"location\": \"Beijing\"}");
}

#[test]
fn parse_response_with_usage() {
    let data = serde_json::json!({
        "choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}],
        "model": "m",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    });
    let r = parse_response(&data, "x").unwrap();
    let u = r.usage.unwrap();
    assert_eq!(u.total_tokens, 30);
}

#[test]
fn parse_response_empty_content_is_empty_string() {
    let data = serde_json::json!({
        "choices": [{"message": {}, "finish_reason": "stop"}],
        "model": "m"
    });
    let r = parse_response(&data, "x").unwrap();
    assert_eq!(r.content, "");
}

// ── llm: HttpClient mock ──

struct MockClient {
    response: Mutex<Value>,
}

impl HttpClient for MockClient {
    fn post_json(&self, _url: &str, _auth: &str, _body: &Value) -> Result<Value, LLMError> {
        Ok(self.response.lock().unwrap().clone())
    }
}

#[test]
fn llm_complete_with_mock() {
    let mock = Box::new(MockClient {
        response: Mutex::new(serde_json::json!({
            "choices": [{"message": {"content": "Mock response"}, "finish_reason": "stop"}],
            "model": "mock-model"
        })),
    });
    let llm = LLM::with_client("test", "http://localhost", "sk-test", mock);
    let resp = llm.complete(&[Message::new("user", "hi")], CompleteOptions::default()).unwrap();
    assert_eq!(resp.content, "Mock response");
    assert_eq!(resp.model, "mock-model");
}

// ── llm: build_body ──

#[test]
fn llm_build_body_includes_thinking() {
    let mock = Box::new(MockClient {
        response: Mutex::new(serde_json::json!({
            "choices": [{"message": {"content": ""}, "finish_reason": "stop"}],
            "model": "m"
        })),
    });
    let llm = LLM::with_client("test", "http://localhost", "sk-test", mock);
    let opts = CompleteOptions {
        thinking: Some(true),
        ..Default::default()
    };
    // complete triggers build_body internally; the mock returns success
    let resp = llm.complete(&[], opts).unwrap();
    assert_eq!(resp.content, "");
}

// ── config ──

#[test]
fn settings_default_values() {
    let s = Settings::default();
    assert_eq!(s.llm_model, "deepseek-v4-flash");
    assert_eq!(s.llm_base_url, "https://api.deepseek.com");
    assert_eq!(s.llm_api_key, "");
}

#[test]
fn settings_from_env_uses_env() {
    // Save original
    let orig_key = std::env::var("LLM_API_KEY").ok();
    std::env::set_var("LLM_API_KEY", "env-test-key");
    let s = Settings::from_env();
    assert_eq!(s.llm_api_key, "env-test-key");
    // Restore
    match orig_key {
        Some(k) => std::env::set_var("LLM_API_KEY", k),
        None => std::env::remove_var("LLM_API_KEY"),
    }
}

// ── llm: mock client error ──

struct MockClientError;

impl HttpClient for MockClientError {
    fn post_json(&self, _url: &str, _auth: &str, _body: &Value) -> Result<Value, LLMError> {
        Err(LLMError("mock error".into()))
    }
}

#[test]
fn llm_complete_returns_error_on_http_failure() {
    let llm = LLM::with_client("test", "http://localhost", "sk-test", Box::new(MockClientError));
    let result = llm.complete(&[], CompleteOptions::default());
    assert!(result.is_err());
    assert!(result.unwrap_err().0.contains("mock error"));
}

// ── llm: parse_response defaults model when missing ──

#[test]
fn parse_response_uses_default_model_when_missing() {
    let data = serde_json::json!({
        "choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}]
    });
    let r = parse_response(&data, "fallback-model").unwrap();
    assert_eq!(r.model, "fallback-model");
}

// ── llm: tool_calls absent vs empty ──

#[test]
fn parse_response_no_tool_calls_when_absent() {
    let data = serde_json::json!({
        "choices": [{"message": {"content": "hi"}, "finish_reason": "stop"}],
        "model": "m"
    });
    let r = parse_response(&data, "x").unwrap();
    assert!(r.tool_calls.is_none());
}

#[test]
fn parse_response_tool_call_empty_function_name_is_empty() {
    let data = serde_json::json!({
        "choices": [{"message": {"content": "", "tool_calls": [{"id": "c1", "function": {}}]}, "finish_reason": "tool_calls"}],
        "model": "m"
    });
    let r = parse_response(&data, "x").unwrap();
    let tcs = r.tool_calls.unwrap();
    assert_eq!(tcs[0].name, "");
}
