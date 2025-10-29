use std::fs;
use dirs;
use serde_json::{Value, json};

pub fn run_command(message: &Value) -> Value {
    let command = message["command"].as_str().unwrap_or("");
    
    match command {
        "getFolder" => {
            let folder = message
                .get("args")
                .and_then(|a| a.get("folder"))
                .and_then(|f| f.as_str())
                .unwrap_or("")
                .to_string();
            println!("Getting folder: {}", folder);
            get_folder(&folder)
        }
        _ => {
            println!("Unknown command: {}", command);
            Value::Null
        }
    }
}

fn get_folder(folder: &str) -> Value {
    let folder = if folder.is_empty() {
        dirs::home_dir()
            .unwrap_or_else(|| "/".into())
            .to_str()
            .unwrap_or("/")
            .to_string()
    } else {
        folder.to_string()
    };
    match fs::read_dir(&folder) {
        Ok(entries) => {
            let items: Vec<Value> = entries
                .filter_map(|entry| entry.ok())
                .map(|e| {
                    let path = e.path();
                    let name = e.file_name().into_string().unwrap_or_default();
                    let is_dir = path.is_dir();
                    json!({
                        "name": name,
                        "type": if is_dir { "folder" } else { "file" }
                    })
                })
                .collect();

            json!({
                "command": "clientCommandResult",
                "error": "",
                "items": items,
                "folder": folder
            })
        }
        Err(err) => json!({
            "error": err.to_string()
        }),
    }
}