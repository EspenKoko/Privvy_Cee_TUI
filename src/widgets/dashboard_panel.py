from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Digits
import random
import time

from src.services.configuration import ConfigManager
from src.services.polling_rate import PollingRateService

class DashboardPanel(Vertical):
    CSS = """
    DashboardPanel {
        height: auto;
    }
    """
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._poll_interval = 5
        self._last_poll_time = 0.0

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

        self._poll_interval = self.set_polling_rate()
        self._last_poll_time = time.monotonic()
        self.set_interval(0.5, self._tick)

    def _tick(self) -> None:
        now = time.monotonic()
        interval = self.set_polling_rate()
        if interval != self._poll_interval:
            self._poll_interval = interval

        if now - self._last_poll_time >= self._poll_interval:
            self._last_poll_time = now
            # self.update_stats()
        
    def update_stats(self) -> None:
        # Simulate gathering system data
        dummy_temp = random.randint(40, 75)
        dummy_status = "Ok"
        
        # Update the UI components safely
        self.query_one("#cpu_temp", Digits).update(f"CPU Temp: {dummy_temp}°C")
        self.query_one("#status", Digits).update(f"Server Status: {dummy_status}")

    # Apparantly this way of getting config is more robust
    def set_polling_rate(self) -> int:
        cfg_mgr = getattr(self.app, "config_manager", None)
        return PollingRateService.get_polling_rate_seconds(cfg_mgr)
                