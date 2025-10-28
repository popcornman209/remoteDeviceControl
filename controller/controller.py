from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual import events, widgets
import hashlib, json, lib.ws, os, shutil

if not os.path.exists("config.json"):
    shutil.copyfile("config.default.json", "config.json")
with open("config.json", "r") as f:
    config = json.load(f)

websocket = lib.ws.ws(config["websocket_url"])

class LoginScreen(Screen):
    CSS_PATH = "css/login.tcss"
    BINDINGS = [
        Binding(key="^q", action="quit", description="Quit the app"),
    ]

    def compose(self) -> ComposeResult:
        yield widgets.Header(show_clock=True)
        yield widgets.Label("\n\tEnter Password")
        yield widgets.Input(placeholder="password",password=True)
        yield widgets.Footer()
    
    def on_mount(self) -> None:
        self.title = "Login"

    def on_input_submitted(self, event: widgets.Input.Submitted) -> None:
        password = event.value
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if websocket.connect(hashed_password):
            self.app.push_screen("welcome")
        else:
            self.app.exit("Incorrect password.")

class ClientList(Screen):
    CSS_PATH = "css/clientList.tcss"
    BINDINGS = [
        Binding(key="r", action="reload", description="Reload client list"),
        Binding(key="", action="move", description="Move cursor"),
        Binding(key="󰌑", action="select", description="Select a client"),
        Binding(key="^q", action="quit", description="Quit the app"),
    ]

    def on_list_view_selected(self, event: widgets.ListView.Selected) -> None:
        selected_item = event.item
        self.app.clientID = selected_item.clientID
        self.app.push_screen("clientInfo")

    def compose(self) -> ComposeResult:
        yield widgets.Header(show_clock=True)
        yield widgets.Label("Connected clients:")
        self.listView = widgets.ListView()
        yield self.listView
        yield widgets.Footer()

    def on_mount(self) -> None:
        self.title = "Clients"

    def on_screen_resume(self) -> None:
        self.refresh_clients()

    def refresh_clients(self):
        self.listView.clear()
        clients = websocket.getClients()  # returns list of dicts
        for client in clients:
            item = widgets.ListItem(widgets.Label(f"{client['id']}: {client['name']} {client['ip'][0]}:{client['ip'][1]}"))
            item.clientID = client['id']
            self.listView.append(item)

    async def on_key(self, event: events.Key) -> None:
        if event.key == "r":
            self.refresh_clients()

class ClientInfo(Screen):
    CSS_PATH = "css/clientInfo.tcss"
    BINDINGS = [
        Binding(key="r", action="reload", description="Reload client list"),
        Binding(key="", action="move", description="Move cursor"),
        Binding(key="󰌑", action="select", description="Select a client"),
        Binding(key="Esc", action="back", description="Back to client list"),
        Binding(key="^q", action="quit", description="Quit the app"),
    ]

    def compose(self):
        yield widgets.Header(show_clock=True)
        self.infoLabel = widgets.Label("")
        yield self.infoLabel
        self.featuresList = widgets.ListView()
        yield self.featuresList
        yield widgets.Footer()

    def on_mount(self) -> None:
        self.title = "Client Info"

    def on_screen_resume(self) -> None:
        self.refresh_info()
    
    def refresh_info(self):
        self.featuresList.clear()
        client = websocket.getClient(self.app.clientID)  # returns dict
        self.infoLabel.update(f"ID: {self.app.clientID}\nName: {client['name']}\nHostname: {client['host']}\nIP: {client['ip'][0]}:{client['ip'][1]}")
        for feature in client['features']:
            item = widgets.ListItem(widgets.Label(f"{feature[0]}"))
            self.featuresList.append(item)

    def on_key(self, event: events.Key) -> None:
        if event.key == "r":
            self.refresh_info()
        if event.key == "escape":
            self.app.pop_screen()


class MainApp(App):
    def on_mount(self) -> None:
        self.theme = "catppuccin-mocha"
        self.install_screen(LoginScreen(), name="login")
        self.install_screen(ClientList(), name="welcome")
        self.install_screen(ClientInfo(), name="clientInfo")
        self.push_screen("login")


if __name__ == "__main__":
    message = MainApp().run()
    if message: print(message)
