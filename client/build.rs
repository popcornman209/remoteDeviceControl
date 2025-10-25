use std::fs;

fn main() {
    println!("cargo:rerun-if-changed=config.json");
    println!("cargo:rerun-if-changed=config.default.json");

    let contents = fs::read_to_string("config.json")
        .or_else(|_| fs::read_to_string("config.default.json"))
        .expect("Missing both config.json and config.default.json");

    // Escape newlines and quotes for embedding
    let escaped = contents.replace('\\', "\\\\").replace('"', "\\\"").replace('\n', "\\n");
    println!("cargo:rustc-env=APP_CONFIG={}", escaped);
}
