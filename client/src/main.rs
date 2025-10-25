use tungstenite::{connect, Message, Error as WsError};
use std::{thread, time::Duration};
mod error;
use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct Config {
    discord_webhook: String,
}

mod test;
use test::test;

fn main_loop(mut socket: tungstenite::WebSocket<tungstenite::stream::MaybeTlsStream<std::net::TcpStream>>) -> Result<(), WsError> {
    socket.send(Message::Text("Hello, Test!".into()))?;
    test();
    loop {
        match socket.read() {
            Ok(msg) => println!("Received: {}", msg),
            Err(e) => return Err(e),
        }
    }
}

fn main() {
    let raw = std::env::var("APP_CONFIG").expect("APP_CONFIG missing");
    let json_str = raw.replace("\\n", "\n").replace("\\\"", "\"").replace("\\\\", "\\");
    
    let config: Config = serde_json::from_str(&json_str).expect("Invalid JSON in config");

    loop {  // Main reconnection loop
        println!("Attempting to connect...");
        
        match connect("ws://127.0.0.1:42069/websocket") {
            Ok((socket, response)) => {
                println!("Connected to the server");
                println!("Response HTTP code: {}", response.status());
                println!("Response contains the following headers:");
                for (ref header, _value) in response.headers() {
                    println!("* {}", header);
                }
                
                // Run main_loop and catch panics so we can handle them centrally.
                let run_res = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
                    main_loop(socket)
                }));

                match run_res {
                    // main_loop completed normally (Ok(Ok(_))) or returned an error (Ok(Err(e)))
                    Ok(Ok(_)) => {
                        // Normal exit - break or continue depending on desired behavior
                        break;
                    }
                    Ok(Err(e)) => {
                        // A tungstenite error occurred; handle it
                        error::handle_error(e);
                    }
                    Err(payload) => {
                        // A panic occurred inside main_loop or code it called (e.g. test.rs)
                        let msg = payload.downcast_ref::<&str>().map(|s| *s)
                            .or_else(|| payload.downcast_ref::<String>().map(|s| s.as_str()));
                        error::handle_panic_info(msg, &config.discord_webhook);
                    }
                }
            }
            Err(e) => {
                println!("Failed to connect: {}", e);
            }
        }
        
        println!("Waiting 30 seconds before reconnecting...");
        thread::sleep(Duration::from_secs(30));
    }
}