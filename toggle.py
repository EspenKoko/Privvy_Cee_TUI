from textual.app import App, ComposeResult
from textual.widgets import Button

class ToggleButton(Button):
    def __init__(self, labels: dict[int, str], border: tuple[str, str] = ("double", "gold"),
                  default_label=str, variant = "default", *,
                 name = None, id = None, classes = None, disabled = False, tooltip=None):
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self.toggled = False
        self.label = default_label
        self.labels = labels
        self.border = border
        self.variant = variant
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if not self.toggled:
            event.button.styles.border = self.border
        else:
            event.button.styles.border = None
            
        self.toggled = not self.toggled
        event.button.label = self.labels[self.toggled]
        
class TestToggle(App):
    
    def compose(self) -> ComposeResult:
        yield ToggleButton(
            labels={ 1: "on", 0: "off"},
            default_label="off"
        )
        
        
        
if __name__ == "__main__":
    app = TestToggle()
    app.run()