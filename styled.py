from textual.app import App
from textual.widgets import Label, Static

class TextApp(App):
    CSS_PATH = "styled.tcss"
    
    def compose(self):
        yield Static("Static widget")
        yield Static("Using ID", id="static_with_id")
        yield Static("first class", classes="static_cl1")
        yield Static("Another class", classes="static_cl1 static_cl2")

    def on_key (self, event): 
        match event.key:
            case "q":
                exit()
                
if __name__ == "__main__":
    app = TextApp()
    app.run()    