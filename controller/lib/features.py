from textual.screen import Screen
import lib.ws
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual import events, widgets
import hashlib, json, lib.ws, os, shutil, lib.features

class FileExplorer(Screen):
    CSS_PATH = "css/fileExplorer.tcss"
    BINDINGS = [
        Binding(key="r", action="reload", description="Reload file list"),
        Binding(key="", action="move", description="Move cursor"),
        Binding(key="󰌑", action="select", description="Select a file or folder"),
        Binding(key="^q", action="quit", description="Quit the app"),
    ]

    def compose(self) -> ComposeResult:
        yield widgets.Header(show_clock=True)
        self.tree = widgets.Tree("")
        yield self.tree
        yield widgets.Footer()

    def on_mount(self) -> None:
        self.title = "File Explorer"
    
    def on_screen_resumed(self) -> None:
        result = self.app.websocket.sendClientCommand(self.app.clientID, "getFolder", {"folder": ""})
        self.tree.children.clear()
        self.tree.label = result["folder"]
        for file in result["files"]:
            node = self.tree.root.add(file["name"], expand=file["type"] == "folder")
        lib.features.loadFileList(self.app.clientID, self.listView)