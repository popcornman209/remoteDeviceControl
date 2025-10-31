use std::fs;
use std::env;
use std::path::Path;

fn main() {
    println!("cargo:rerun-if-changed=config.json");
    println!("cargo:rerun-if-changed=configRelease.json");
    println!("cargo:rerun-if-changed=config.default.json");

    let config_path = if Ok("release".to_owned()) == env::var("PROFILE") {
        Path::new("configRelease.json")
    } else {
        Path::new("config.json")
    };
    let default_path = Path::new("config.default.json");

    if !config_path.exists() {
        if let Err(e) = fs::copy(default_path, config_path) {
            panic!("Failed to create config.json from default: {}", e);
        }
    }

    let contents = fs::read_to_string(config_path)
        .or_else(|_| fs::read_to_string("config.default.json"))
        .expect("Missing both config.json and config.default.json");

    // Escape newlines and quotes for embedding
    let escaped = contents.replace('\\', "\\\\").replace('"', "\\\"").replace('\n', "\\n");
    println!("cargo:rustc-env=APP_CONFIG={}", escaped);
    println!("cargo:rustc-env=BUILD_RELEASE={}", Ok("release".to_owned()) == env::var("PROFILE"));
}
