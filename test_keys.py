from textual.app import App
from textual.widgets import Input
from textual import events

class KeyLogger(App):
    def compose(self):
        yield Input(placeholder="Press keys here...")

    def on_key(self, event: events.Key):
        self.notify(f"Key pressed: {event.key}")

if __name__ == "__main__":
    app = KeyLogger()
    app.run(headless=True)
