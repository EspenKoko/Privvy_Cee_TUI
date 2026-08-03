from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import Header, Footer, DataTable, Static


class Servers(App):
    CSS_PATH = "metrics.tcss"

    def compose(self) -> ComposeResult:
        yield Button
# if __name__ == "__main__":
#     Metrics().run()