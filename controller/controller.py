from textual.app import App, ComposeResult
from textual.widgets import Input, Label, Button
from textual.screen import Screen


class LoginScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Label("Enter Password (sha256 encrypted):")
        self.input = Input(password=True)
        yield self.input
        yield Button("Submit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        password = self.input.value
        # Normally you'd check the password here
        self.app.push_screen("welcome")


class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Label("Welcome! You have successfully logged in.")


class MainApp(App):
    def on_mount(self) -> None:
        self.install_screen(LoginScreen(), name="login")
        self.install_screen(WelcomeScreen(), name="welcome")
        self.push_screen("login")


if __name__ == "__main__":
    MainApp().run()
