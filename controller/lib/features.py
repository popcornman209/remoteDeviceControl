from textual.screen import Screen
from textual.app import ComposeResult
from textual.screen import Screen
from textual.binding import Binding
from textual import events, widgets
import hashlib, json, lib.ws, os, shutil, lib.features, pathlib, time

class FileExplorer(Screen):
    CSS_PATH = "../css/fileExplorer.tcss"
    BINDINGS = [
        Binding(key="󰌑 /󱁐", action="", description="Expand folder"),
        Binding(key="", action="", description="Open folder"),
        Binding(key="", action="", description="Parent folder"),
    ]

    def compose(self) -> ComposeResult:
        yield widgets.Header(show_clock=True)
        self.fileTree: widgets.Tree[str] = widgets.Tree("")
        yield self.fileTree
        yield widgets.Footer()

    def on_mount(self) -> None:
        self.title = "File Explorer"
    
    def on_screen_resume(self) -> None:
        self.fileTree.root.label = ""
        self.fileTree.root.expand()

    def fetchFolder(self, folder):
        if folder.is_root:
            path = str(folder.label)
        else:
            path = folder.globalPath
        result = self.app.websocket.sendClientCommand(self.app.clientID, "getFolder", {"folder": path})
        return result

    def on_tree_node_expanded(self, event: widgets.Tree.NodeExpanded) -> None:
        folder = event.node
        result = self.fetchFolder(folder)
        folder.remove_children()
        if folder.is_root: folder.label = result["folder"]
        for file in sorted(result["items"], key=lambda x: x["name"].lower()):
            if file["type"] == "folder":
                node = folder.add(file["name"])
            else:
                node = folder.add_leaf(file["name"])
            node.fileData = file
            node.globalPath = str(pathlib.Path(result["folder"]) / file["name"])
    
    async def on_key(self, event: events.Key) -> None:
        if event.key == "right":
            node = self.fileTree.cursor_node
            if not node.is_root and node.fileData["type"] == "folder":
                self.fileTree.root.label = node.globalPath
                self.fileTree.root.expand()
        elif event.key == "left":
            parentPath = str(pathlib.Path(str(self.fileTree.root.label)).parent)
            self.fileTree.root.label = parentPath
            self.fileTree.root.expand()


featureList = [
    {"screen": FileExplorer, "screenName": "fileExplorer", "command": "fileExplorer"},
]