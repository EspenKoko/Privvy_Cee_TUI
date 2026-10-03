from pathlib import Path

from textual.app import App
from textual.binding import Binding
from src.screens.dashboard import DashboardScreen
from src.services.configuration import ConfigManager
from src.screens.setup_wizard import WelcomeScreen
from src.screens.settings import SettingsScreen
from src.screens.login import LoginScreen

class HomelabApp(App):
    """Main application."""
    
    CSS_PATH = str(Path(__file__).resolve().parent.joinpath("css", "dashboard.tcss"))

    TITLE = "Homelab Dashboard"
    SUB_TITLE = "Proxmox • Docker"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("d", "dashboard", "Dashboard"),
        Binding("t", "open_test", "Login"),
        Binding("r", "refresh", "Refresh"),
        Binding("?", "help", "Help"),
        Binding("ctrl+s", "open_settings", "Settings", tooltip="Shows Server config"),
    ]

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
    
    def on_mount(self) -> None:
        """Called when the application starts."""
        if self.config_manager.is_first_run():
            self.push_screen(WelcomeScreen())
        else:
            self.config_manager.load()
            self.push_screen(DashboardScreen())

    def action_open_settings(self) -> None:
        # from screens.settings import SettingsScreen
        self.push_screen(SettingsScreen())
        pass

    def action_dashboard(self) -> None:
        """Return to the dashboard."""
        while not isinstance(self.screen, DashboardScreen):
                if len(self.screen_stack) <= 1:
                    # safety net: nothing to pop back to, push a fresh one
                    self.push_screen(DashboardScreen())
                    break
                self.pop_screen()
            
    # def _on_key(self, event):
        #     match event.key:
        #             case "d":
        #                 self.push_screen(DashboardScreen())
            
    def action_refresh(self) -> None:
        """Refresh all data."""
        if isinstance(self.screen, DashboardScreen):
            self.screen.refresh_data() # uses the refresh_data() method defined on the active screen if there is one
        else:
            self.notify("Open the dashboard to refresh its data.")

    def action_help(self) -> None:
        self.notify("Help coming soon!")
        
    def action_open_test(self) -> None:
        self.push_screen(LoginScreen())
        pass