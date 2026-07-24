import os
from pathlib import Path
from dotenv import load_dotenv

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Button, Digits, Label, Static
import random

ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(ROOT_DIR / ".env")

class DashboardPanel(Vertical):
    CSS = """
    DashboardPanel {
        height: auto;
    }
    """
    
    def __init__(self) -> None:
        super().__init__()
        self.label=os.getenv("METRICS_LABEL", "Temps and stuff")
        self.api_url = os.getenv("METRICS_API_URL", "https://dummyjson.com/products")
        self.refresh_seconds = int(os.getenv("METRICS_REFRESH_SECONDS", "6"))

    def compose(self) -> ComposeResult:
        with Container():
            yield Digits("CPU Temp: --°C", id="cpu_temp")
            yield Digits("Server Status: OK", id="status")
            
    def on_mount(self) -> None:
        # self.styles.padding = (1, 2)
        # self.styles.height = "auto"

        container = self.query_one(Container)
        container.styles.layout = "vertical"
        container.styles.align = ("left", "top")
        container.styles.padding = (1, 2)

        for widget_id in ("cpu_temp", "status"):
            digit = self.query_one(f"#{widget_id}", Digits)
            digit.styles.text_align = "center"
            digit.styles.margin = (1, 0)
            digit.styles.background = "gray"
            digit.styles.color = "white"
            digit.styles.padding = (1, 1)

        self.set_interval(2.0, self.update_stats)
        
    def update_stats(self) -> None:
        # Simulate gathering system data
        dummy_temp = random.randint(40, 75)
        dummy_status = "Ok"
        
        # Update the UI components safely
        self.query_one("#cpu_temp", Digits).update(f"CPU Temp: {dummy_temp}°C")
        self.query_one("#status", Digits).update(f"Server Status: {dummy_status}")