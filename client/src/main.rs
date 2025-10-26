use tungstenite::{connect, Message, Error as WsError};
use std::{thread, time::Duration};
mod error_handler;
use serde::Deserialize;

#[derive(Deserialize, Debug)]
struct Config {
    discord_webhook: String,
    discord_ping: String,
    websocket_url: String,
}

mod test;
use test::test;

fn main() {
    let raw = std::env::var("APP_CONFIG").expect("APP_CONFIG missing");
    let json_str = raw.replace("\\n", "\n").replace("\\\"", "\"").replace("\\\\", "\\");
    
    let config: Config = serde_json::from_str(&json_str).expect("Invalid JSON in config");
    error_handler::init_panic_hook(config.discord_webhook, config.discord_ping); // catch panics

    loop {
        if let Err(e) = connect_to_ws(&config.websocket_url) {
            if error_handler::handle_tungstenite(e) {
                println!("Reconnecting in 30 seconds...");
                thread::sleep(Duration::from_secs(30));
                continue; // try again
            } else {
                println!("Unrecoverable error, exiting.");
                break;
            }
        }
    }
}

fn connect_to_ws(websocket_url: &str) -> Result<(), WsError> {
    match connect(websocket_url) {
        Ok((socket, response)) => {
            println!("Connected to the server");
            println!("Response HTTP code: {}", response.status());
            println!("Response contains the following headers:");
            for (ref header, _value) in response.headers() {
                println!("* {}", header);
            }

            main_loop(socket);

            Ok(())
        }
        Err(e) => {
            Err(e)
        }
    }
}

fn main_loop(mut socket: tungstenite::WebSocket<tungstenite::stream::MaybeTlsStream<std::net::TcpStream>>) {
    socket.send(Message::Text("Hello, Test!".into())).expect("failed to send message");
    test();
    loop {
        println!("Received: {}", socket.read().expect("failed to recieve message"));
    }
}