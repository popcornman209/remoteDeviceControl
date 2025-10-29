from textual.screen import Screen
import lib.ws
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual import events, widgets
import hashlib, json, lib.ws, os, shutil, lib.features, pathlib

class FileExplorer(Screen):
    #CSS_PATH = "css/fileExplorer.tcss"
    BINDINGS = [
        Binding(key="r", action="reload", description="Reload file list"),
        Binding(key="", action="move", description="Move cursor"),
        Binding(key="󰌑", action="select", description="Select a file or folder"),
        Binding(key="^q", action="quit", description="Quit the app"),
    ]

    def compose(self) -> ComposeResult:
        yield widgets.Header(show_clock=True)
        self.fileTree: widgets.Tree[str] = widgets.Tree("")
        yield self.fileTree
        yield widgets.Footer()

    def on_mount(self) -> None:
        self.title = "File Explorer"
    
    def on_screen_resume(self) -> None:
        self.fileTree.root.remove_children()
        self.fileTree.root.label = ""
        result = self.expandFolder(self.fileTree.root)

    def fetchFolder(self, folder):
        self.app.exit(str(folder.label))
        result = self.app.websocket.sendClientCommand(self.app.clientID, "getFolder", {"folder": folder.label})
        return result

    def expandFolder(self, folder) -> None:
        result = self.fetchFolder(folder)
        folder.remove_children()
        folder.label = result["folder"]
        for file in result["items"]:
            if file["type"] == "folder":
                node = folder.add(file["name"])
            else:
                node = folder.add_leaf(file["name"])
            node.fileData = file
            node.globalPath = result["folder"] + "/" + file["name"]
        return result
            