use quanttide_agent::{
    message::Message,
    tool::{ToolCall, ToolSchema},
    cost::Usage,
};

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
fn tool_schema_json() {
    let ts = ToolSchema {
        name: "get_weather".into(),
        description: "Get weather".into(),
        parameters: Some(serde_json::json!({"type": "object", "properties": {"location": {"type": "string"}}})),
    };
    let json = serde_json::to_string(&ts).unwrap();
    assert!(json.contains("get_weather"));
}

#[test]
fn tool_call_deserialize() {
    let json = r#"{"id":"call_1","name":"get_weather","arguments":"{\"location\":\"Beijing\"}"}"#;
    let tc: ToolCall = serde_json::from_str(json).unwrap();
    assert_eq!(tc.id, "call_1");
    assert_eq!(tc.name, "get_weather");
}

#[test]
fn usage_from_api() {
    let data = serde_json::json!({
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30,
        "prompt_cache_hit_tokens": 5,
        "completion_tokens_details": {"reasoning_tokens": 8}
    });
    let u = Usage::from_api(&data).unwrap();
    assert_eq!(u.input_tokens, 10);
    assert_eq!(u.output_tokens, 20);
    assert_eq!(u.total_tokens, 30);
    assert_eq!(u.input_cached_tokens, 5);
    assert_eq!(u.reasoning_tokens, 8);
}

#[test]
fn usage_from_api_none_on_empty() {
    let data = serde_json::Value::Null;
    assert!(Usage::from_api(&data).is_none());
}
