from pathlib import Path

from textual.screen import Screen
from textual.containers import Container
from textual.widgets import (
    Header,
    Footer,
    Button,
    Static,
)
from textual.app import ComposeResult
from textual import on

from src.screens.setup_wizard import AddHostScreen


class WelcomeScreen(Screen):
    """First screen shown on a fresh install."""

    CSS_PATH = str(Path(__file__).resolve().parents[1] / "css" / "welcome_screen.tcss")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="card"):
            yield Static("👋 Welcome to Privvy_Cee_TUI", id="welcome-title")
            yield Static(
                "Looks like this is your first run. Let's set up your environment "
            )
            yield Button("Get Started", id="start-btn", variant="success")
        yield Footer()

    @on(Button.Pressed, "#start-btn")
    def start_setup(self) -> None:
        self.app.push_screen(AddHostScreen())

