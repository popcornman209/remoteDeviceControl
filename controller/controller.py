from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual import events, widgets
import hashlib, json, lib.ws, os, shutil, lib.features

featureList = lib.features.featureList
featureCommands = {f["command"]: f for f in featureList}

if not os.path.exists("config.json"):
    shutil.copyfile("config.default.json", "config.json")
with open("config.json", "r") as f:
    config = json.load(f)

class LoginScreen(Screen):
    CSS_PATH = "css/login.tcss"
    BINDINGS = [
        Binding(key="^q", action="quit", description="Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield widgets.Header(show_clock=True)
        yield widgets.Label("\n\tEnter Password")
        yield widgets.Input(placeholder="password",password=True)
        yield widgets.Footer()
    
    def on_mount(self) -> None:
        self.title = "Login"

    def on_input_submitted(self, event: widgets.Input.Submitted) -> None:
        password = config["passwordSalt"].format(event.value)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if self.app.websocket.connect(hashed_password):
            self.app.push_screen("welcome")
        else:
            self.app.exit("Incorrect password.")

class ClientList(Screen):
    CSS_PATH = "css/clientList.tcss"
    BINDINGS = [
        Binding(key="r", action="", description="Reload"),
        Binding(key="", action="", description="Move cursor"),
        Binding(key="󰌑", action="", description="Select client"),
        Binding(key="^q", action="", description="Quit"),
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
        self.notify("Connected to server.", timeout=2)

    def on_screen_resume(self) -> None:
        self.refresh_clients()

    def refresh_clients(self):
        self.listView.clear()
        clients = self.app.websocket.getClients()  # returns list of dicts
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
        Binding(key="r", action="", description="Reload"),
        Binding(key="", action="", description="Move cursor"),
        Binding(key="󰌑", action="", description="Select client"),
        Binding(key="Esc", action="", description="Back"),
        Binding(key="^q", action="", description="Quit"),
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
        self.clientDict = self.app.websocket.getClient(self.app.clientID)  # returns dict
        self.infoLabel.update(f"""
            ID: {self.app.clientID}
            Name: {self.clientDict['name']}
            Hostname: {self.clientDict['host']}
            IP: {self.clientDict['ip'][0]}:{self.clientDict['ip'][1]}
            Busy: {self.clientDict['busy']}
        """)
        for feature in self.clientDict['features']:
            item = widgets.ListItem(widgets.Label(f"{"[Unknown?] " if feature[1] not in featureCommands else ""}{feature[0]}"))
            item.feature = feature
            self.featuresList.append(item)
    
    def on_list_view_selected(self, event: widgets.ListView.Selected) -> None:
        selected_item = event.item
        self.refresh_info()
        if self.clientDict["busy"]:
            self.notify("Client is busy!", severity="error", timeout=5)
        else:
            if selected_item.feature[1] in featureCommands:
                self.app.push_screen(featureCommands[selected_item.feature[1]]["screenName"])
            else:
                self.notify("Feature not implemented in controller.", severity="error", timeout=10)

    def on_key(self, event: events.Key) -> None:
        if event.key == "r":
            self.refresh_info()
        if event.key == "escape":
            self.app.pop_screen()


class MainApp(App):
    def on_mount(self) -> None:
        self.websocket = lib.ws.ws(config["websocket_url"])
        self.theme = "catppuccin-mocha"
        self.install_screen(LoginScreen(), name="login")
        self.install_screen(ClientList(), name="welcome")
        self.install_screen(ClientInfo(), name="clientInfo")

        for feature in featureList:
            self.install_screen(feature["screen"], name=feature["screenName"])

        self.push_screen("login")


if __name__ == "__main__":
    message = MainApp().run()
    if message: print(message)
