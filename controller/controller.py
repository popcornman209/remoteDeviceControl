from textual.app import App, ComposeResult
from textual.widgets import Input, Label


class main(App):
    def compose(self) -> ComposeResult:
        yield Label("\nEnter Password (sha256 encrypted):")
        yield Input(type="text", password=True)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.exit(event.value)

app = main()

if __name__ == "__main__":
    app.run()