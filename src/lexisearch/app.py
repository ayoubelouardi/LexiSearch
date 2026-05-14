"""LexiSearch TUI Application."""

import sqlite3
import sys
import time
from pathlib import Path
from typing import Dict, List

from rapidfuzz import fuzz, process
from textual import events, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, Header, Input, Markdown, OptionList, Static

# Database configuration: handle PyInstaller path if frozen
if getattr(sys, "frozen", False):
    # Running as compiled binary
    DB_PATH = Path(sys._MEIPASS) / "lexisearch" / "data" / "dictionary.db"  # type: ignore
else:
    # Running in normal Python environment
    DB_PATH = Path(__file__).parent / "data" / "dictionary.db"


class HelpScreen(ModalScreen):
    """Screen with a dialog to show help and shortcuts."""

    CSS = """
    HelpScreen {
        align: center middle;
        background: $background 80%;
    }

    #help_dialog {
        padding: 1 2;
        width: 60%;
        height: 80%;
        border: thick $primary;
        background: $surface;
    }
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
        ("?", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        help_markdown = """
# LexiSearch Shortcuts

| Key(s) | Action | Mode |
|---|---|---|
| `/` | Focus Search Bar | Any |
| `Escape` | Unfocus Search (Enter Normal Mode) | Any |
| `Ctrl+Backspace` | Clear Search Bar | Any |
| `Enter` | Select First Word | Search Focused |
| `?` | Toggle Help | Normal |
| `q` | Quit Application | Normal |
| `Ctrl+c` | Quit Application | Any |

## Normal Mode Navigation (Vim Style)
*(Press `Escape` to enter Normal Mode)*

| Key | Action |
|---|---|
| `j` | Move / Scroll Down |
| `k` | Move / Scroll Up |
| `h` | Focus Word List (Left) |
| `l` | Focus Definition (Right) |
| `gg` | Jump to Top |
| `G` | Jump to Bottom |
        """
        with Vertical(id="help_dialog"):
            yield Markdown(help_markdown)


class DictionaryTUI(App):
    """A high-performance dictionary search application."""

    CSS = """
    Screen {
        background: $surface;
    }

    #search_container {
        height: auto;
        padding: 1;
        background: $boost;
    }

    #main_container {
        height: 1fr;
    }

    #word_list {
        width: 30%;
        height: 1fr;
        border-right: tall $primary;
    }
    
    #word_list:focus {
        border-right: tall $accent;
    }

    #definition_panel {
        width: 70%;
        height: 1fr;
        padding: 1 2;
        overflow-y: scroll;
    }
    
    #definition_panel:focus {
        background: $surface-lighten-1;
    }

    .word-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    .word-type {
        color: $secondary;
        text-style: italic;
        margin-bottom: 1;
    }

    .definition-block {
        margin-bottom: 1;
        border-bottom: solid $surface-lighten-1;
        padding-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("escape", "unfocus_search", "Normal Mode", show=True),
        Binding("/", "focus_search", "Search"),
        Binding(
            "ctrl+h", "clear_search", "Clear"
        ),  # Ctrl+Backspace maps to ctrl+h in many terminals
        Binding("?", "show_help", "Help"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.words: List[str] = []
        self.db_conn = None
        self._search_cache: Dict[str, list] = {}
        self._last_g_press = 0

    def on_mount(self) -> None:
        """Initialize database connection and load word list."""
        self.load_words()
        self.query_one(Input).focus()

    def load_words(self) -> None:
        """Loads unique words from the database for fuzzy searching."""
        try:
            self.db_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            cursor = self.db_conn.cursor()
            # Fetch unique words to prevent repetition in the sidebar
            cursor.execute("SELECT DISTINCT word FROM entries ORDER BY word")
            self.words = [row[0] for row in cursor.fetchall() if row[0]]
            self.notify(f"Indexed {len(self.words):,} unique words", title="Success")
        except Exception as e:
            self.notify(f"Error loading database: {e}", severity="error")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Vertical(id="search_container"):
            yield Input(placeholder="Type to search (fuzzy)...", id="search_input")
        with Horizontal(id="main_container"):
            yield OptionList(id="word_list")
            def_panel = Static(id="definition_panel")
            def_panel.can_focus = True
            yield def_panel
        yield Footer()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one(Input).focus()

    def action_unfocus_search(self) -> None:
        """Drop focus from search to enter normal mode."""
        self.query_one(OptionList).focus()

    def action_clear_search(self) -> None:
        """Clear the search input."""
        inp = self.query_one(Input)
        inp.value = ""
        inp.focus()

    def action_show_help(self) -> None:
        """Show the help screen."""
        if not self.query_one(Input).has_focus:
            self.push_screen(HelpScreen())

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle live search as the user types."""
        search_term = event.value.strip().lower()
        if len(search_term) >= 1:
            self.perform_fuzzy_search(search_term)
        else:
            self.query_one(OptionList).clear_options()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in the search bar."""
        _ = event
        option_list = self.query_one(OptionList)
        if option_list.option_count > 0:
            option_list.focus()
            option_list.highlighted = 0

    def on_key(self, event: events.Key) -> None:
        """Handle Vim-style navigation in Normal mode."""
        if self.query_one(Input).has_focus:
            return  # Let the input handle its own keys

        key = event.character
        if not key:
            return

        word_list = self.query_one(OptionList)
        def_panel = self.query_one("#definition_panel")

        if key == "q":
            self.exit()
        elif key == "h":
            word_list.focus()
        elif key == "l":
            def_panel.focus()
        elif key == "j":
            if word_list.has_focus:
                word_list.action_cursor_down()
            elif def_panel.has_focus:
                def_panel.scroll_down(animate=False)
        elif key == "k":
            if word_list.has_focus:
                word_list.action_cursor_up()
            elif def_panel.has_focus:
                def_panel.scroll_up(animate=False)
        elif key == "G":
            if word_list.has_focus and word_list.option_count > 0:
                word_list.highlighted = word_list.option_count - 1
            elif def_panel.has_focus:
                def_panel.scroll_to(y=def_panel.max_scroll_y, animate=False)
        elif key == "g":
            current_time = time.time()
            if current_time - self._last_g_press < 0.5:
                # Double 'g' pressed
                if word_list.has_focus and word_list.option_count > 0:
                    word_list.highlighted = 0
                elif def_panel.has_focus:
                    def_panel.scroll_home(animate=False)
                self._last_g_press = 0
            else:
                self._last_g_press = current_time

    @work(exclusive=True, thread=True)
    async def perform_fuzzy_search(self, search_term: str) -> None:
        """Perform a tiered hybrid search for optimal relevance and speed."""
        if search_term in self._search_cache:
            matches = self._search_cache[search_term]
        else:
            limit = 40
            exact = []
            starts = []
            contains = []
            seen = set()

            # Tier 1 & 2 & 3: Basic string matching (extremely fast)
            for w in self.words:
                if w == search_term:
                    exact.append(w)
                    seen.add(w)
                elif w.startswith(search_term):
                    starts.append(w)
                    seen.add(w)
                elif search_term in w:
                    contains.append(w)
                    seen.add(w)

            # Sort prefix and contains matches by length so shorter words appear first
            starts.sort(key=lambda x: (len(x), x))
            contains.sort(key=lambda x: (len(x), x))

            combined = exact + starts + contains
            matches = combined[:limit]

            # Tier 4: Fallback to fuzzy search if we need more results (typographic errors)
            if len(matches) < limit:
                fuzzy_matches = process.extract(
                    search_term,
                    self.words,
                    scorer=fuzz.WRatio,
                    limit=limit,
                    score_cutoff=75,
                )
                for fw, _score, _idx in fuzzy_matches:
                    if fw not in seen:
                        matches.append(fw)
                        seen.add(fw)
                        if len(matches) >= limit:
                            break

            self._search_cache[search_term] = matches
            if len(self._search_cache) > 200:
                self._search_cache.clear()

        # Verify the search term hasn't changed before updating UI
        if self.query_one(Input).value.strip().lower() != search_term:
            return

        # Update UI in the main thread
        self.app.call_from_thread(self._update_word_list, matches)

    def _update_word_list(self, matches: list) -> None:
        option_list = self.query_one(OptionList)
        option_list.clear_options()
        for word in matches:
            option_list.add_option(word)

    async def on_option_list_option_highlighted(
        self, event: OptionList.OptionHighlighted
    ) -> None:
        """Fetch and display definition when a word is highlighted."""
        if event.option:
            word = str(event.option.prompt)
            self.display_definition(word)

    @work(exclusive=True, thread=True)
    async def display_definition(self, word: str) -> None:
        """Fetch all definitions for a word and group them."""
        if not self.db_conn:
            return

        cursor = self.db_conn.cursor()
        # Fetch all definitions for this word to avoid duplicates in matching but show all meanings
        cursor.execute(
            "SELECT word, wordtype, definition FROM entries WHERE word = ?", (word,)
        )
        results = cursor.fetchall()

        if results:
            content = f"[b underline $accent]{word.upper()}[/]\n\n"
            for i, (_w, t, d) in enumerate(results, 1):
                content += f"[b]{i}.[/] [i $secondary]{t}[/] {d}\n\n"

            self.app.call_from_thread(
                self.query_one("#definition_panel", Static).update, content
            )
        else:
            self.app.call_from_thread(
                self.query_one("#definition_panel", Static).update,
                "Definition not found.",
            )

    def on_unmount(self) -> None:
        """Close database connection on exit."""
        if self.db_conn:
            self.db_conn.close()


if __name__ == "__main__":
    app = DictionaryTUI()
    app.run()
