# import os
# from pathlib import Path

# from dotenv import load_dotenv
# from textual.widgets import Button

# ROOT_DIR = Path(__file__).resolve().parents[3]
# load_dotenv(ROOT_DIR / ".env")


# class Metrics(Button):
#     """This defines the metrics returned from the servers."""
    
#     api_url = os.getenv("METRICS_API_URL", "http://localhost:8000/api/metrics")
#     refresh_seconds = int(os.getenv("METRICS_REFRESH_SECONDS", "5"))
#     label = os.getenv("METRICS_LABEL", "Homelab Metrics")

#     def on_button_pressed(self) -> None:
#         print(f"Fetching {self.label} from {self.api_url} every {self.refresh_seconds}s")


from textual.app import App
from textual.widgets import Label, Static


class TextApp(App):
    def compose(self):
        self.static = Static("I am a [bold red]Static[/bold red] widget!")
        yield self.static
        self.label = Label("I am a [yellow italic]label[/] widget!")
        yield self.label

    def on_mount(self):
        self.static.styles.background = "blue"
        self.static.styles.border = ("solid", "white")
        self.static.styles.text_align = "center"
        self.static.styles.padding = 1, 1
        self.static.styles.margin = 4, 4

        self.label.styles.background = "darkgreen"
        self.label.styles.border = ("double", "red")
        self.label.styles.padding = 1, 1
        self.label.styles.margin = 2, 4

    def on_key(self, event):
        match event.key:
            case "q":
                self.exit()

def main():
    TextApp().run()