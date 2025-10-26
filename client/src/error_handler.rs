use tungstenite::Error as WsError;
use serde_json::json;
use reqwest::blocking::Client;
use whoami;
use std::panic;

pub fn handle_tungstenite(e: WsError) -> bool {  // returns true to reconnect
    match e {
        WsError::ConnectionClosed => {
            println!("Connection closed by server, reconnecting...");
            true
        }
        WsError::AlreadyClosed => {
            println!("Connection was already closed, reconnecting...");
            true
        }
        WsError::Url(url) => {
            println!("URL Error, {}", url);
            true
        }
        _ => {
            println!("Error: {}", e);
            false
        }
    }
}

pub fn init_panic_hook(discord_webhook: String, discord_ping: String) {
    panic::set_hook(Box::new(move |info| {
        let location = info.location().map_or_else(
            || "unknown".to_string(), // fallback if location is None
            |loc| format!("{}:{}", loc.file(), loc.line()),
        );

        let device = format!(
            "{}@{} (os: {})",
            whoami::username(),
            whoami::fallible::hostname().unwrap_or_else(|_| String::from("unknown")),
            whoami::platform()
        );

        let error_message = match info.payload().downcast_ref::<&str>() {
            Some(s) => *s,
            None => match info.payload().downcast_ref::<String>() {
                Some(s) => s.as_str(),
                None => "Box<Any>",
            },
        };

        let message = format!(
            "Error: {}\n\
             Location: {}\n\
             Device: {}",
            location, error_message, device
        );
        println!("===================== RUST PANIC DETECTED ====================\n{}\n=========================================================", message);
        
        if !discord_webhook.is_empty() {
            let _ = Client::new()
                .post(&discord_webhook)
                .json(&json!({ "content": format!("Rust panic !!!!! {}\n```{}```", discord_ping, message) }))
                .send();
        }

    }));
}

// Called for panics caught via `catch_unwind` or from a panic hook. "content": format!("Rust panic !!!!!\n```{}```"
// #[track_caller]
// pub fn handle_panic(msg: Option<&str>, discord_webhook: &str) {
//     unsafe {
//         std::env::set_var("RUST_BACKTRACE", "1"); // enable backtraces
//     }

//     // Get current timestamp
//     let ts = SystemTime::now()
//         .duration_since(UNIX_EPOCH)
//         .map(|d| d.as_secs())
//         .unwrap_or(0);

//     // Determine caller location
//     let location = Location::caller();
//     let file = location.file();
//     let line = location.line();
//     let column = location.column();

//     // Determine device identifier
//     let device = format!(
//         "{}@{} (os: {})",
//         whoami::username(),
//         whoami::fallible::hostname().unwrap_or_else(|_| String::from("unknown")),
//         whoami::platform()
//     );

//     // Build debug info
//     let debug_info = format!(
//         "Error: {}\nLocation: {}:{}:{}\nDevice: {}\nTimestamp: {}",
//         msg.unwrap_or("<no message>"),
//         file,
//         line,
//         column,
//         device,
//         ts
//     );

//     // Print locally
//     eprintln!("\n[!] PANIC DETECTED\n{}\n", debug_info);

//     // Sanitize and truncate for Discord (max 2000 chars)
//     let safe_debug = debug_info.replace('`', "'");
//     let trimmed_debug = if safe_debug.len() > 1900 {
//         format!("{}...\n[truncated]", &safe_debug[..1900])
//     } else {
//         safe_debug
//     };

//     // JSON payload
//     let payload = json!({
//         "content": format!("⚠️ **Rust Panic Detected** ⚠️\n```{}\n```", trimmed_debug)
//     });

//     let json_string = serde_json::to_string(&payload)
//         .unwrap_or_else(|e| {
//             eprintln!("Failed to serialize JSON: {}", e);
//             "{\"content\": \"Failed to format error message\"}".to_string()
//         });

//     // Send to webhook
//     if discord_webhook != "" {
//         match ureq::post(discord_webhook)
//             .header("Content-Type", "application/json")
//             .send(&json_string)
//         {
//             Ok(response) => {
//                 if response.status() != 200 && response.status() != 204 {
//                     eprintln!(
//                         "Webhook error: HTTP {}. Payload (first 2000 chars): {}",
//                         response.status(),
//                         &json_string[..json_string.len().min(2000)]
//                     );
//                 }
//             }
//             Err(e) => eprintln!("Failed to send to webhook: {}", e),
//         }
//     }
    
// }
