import asyncio
import random
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Digits

class HomelabMonitor(App):
    CSS = "Digits { text-align: center; margin: 1; background: $boost; padding: 1; }"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Digits("CPU Temp: --°C", id="cpu_temp")
        yield Digits("Server Status: OK", id="status")
        yield Footer()

    def on_mount(self) -> None:
        # Start a background loop when the app loads
        self.set_interval(2.0, self.update_stats)

    def update_stats(self) -> None:
        # Simulate gathering system data
        dummy_temp = random.randint(40, 75)
        
        # Update the UI components safely
        self.query_one("#cpu_temp", Digits).update(f"CPU Temp: {dummy_temp}°C")

if __name__ == "__main__":
    app = HomelabMonitor()
    app.run()
