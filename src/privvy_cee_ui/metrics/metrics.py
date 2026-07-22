import os
from pathlib import Path
import random

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Button, Digits, Footer, Header, Label, Static

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

class ToggleMetrics(Button):
    """This defines the metrics returned from the servers."""

# class Banner(Label):
#     CSS = """
#     Banner {
#         background: yellow;
#         color: black;
#         width: 100%;
#         text-align: center;
#         padding: 0 1;
#     }
#     """
    
#     def __init__(self, content = "", *, variant = None, expand = False, shrink = False, markup = True, name = None, id = None, classes = None, disabled = False):
#         super().__init__(content, variant=variant, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes, disabled=disabled)
#         self.content = "Stuff"
#         self.id = "title-label"


class Metrics(App):
    CSS = """
    Container {
        layout: vertical;
        align: left top;
        height: 100%;
        padding: 1 2;
    }

    ToggleMetrics {
        width: auto;
        margin-top: 2;
        align: left middle;
    }

    Digits {
        text-align: center;
        margin: 1;
        background: $boost;
        padding: 1;
    }
    """
    def __init__(self) -> None:
        super().__init__()
        self.label=os.getenv("METRICS_LABEL", "Temps and stuff")
        self.api_url = os.getenv("METRICS_API_URL", "https://dummyjson.com/products")
        self.refresh_seconds = int(os.getenv("METRICS_REFRESH_SECONDS", "6"))

    BINDINGS = [("q", "quit", "Quit"), ("r", "refresh", "Refresh"), ("f1", "show_help", "Help")] #Automatically picked up by the footer through the app lifecycle

    def compose(self) -> ComposeResult:
        with Container():
            yield Header(show_clock=True)
            # yield Banner()
            # yield ToggleMetrics()
            yield Digits("CPU Temp: --°C", id="cpu_temp")
            yield Digits("Server Status: OK", id="status")
            yield Footer()

    def on_mount(self) -> None:
        # self.query_one("#title-label", Banner).styles.margin_top = 0
        # self.query_one("#title-label", Banner).styles.width = "100%"
        # self.query_one("#title-label", Banner).styles.text_align = "center"
        # Start a background loop when the app loads
        self.set_interval(2.0, self.update_stats)
        
    def update_stats(self) -> None:
        # Simulate gathering system data
        dummy_temp = random.randint(40, 75)
        dummy_status = "Ok"
        
        # Update the UI components safely
        self.query_one("#cpu_temp", Digits).update(f"CPU Temp: {dummy_temp}°C")
        self.query_one("#status", Digits).update(f"Server Status: {dummy_status}")
        
    def on_key(self, event):
        message = f"Fetching {self.label} from {self.api_url} every {self.refresh_seconds}s"
        
        match event.key:
            case "q":
                self.exit()
            case "r":
                self.update_stats()
            case "h":
                self.app.notify(message)
                

def main() -> None:
    Metrics().run()