import sqlite3
import functools
from pathlib import Path
from typing import List, Tuple, Dict

from rapidfuzz import process, fuzz
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Input, Static, OptionList, Footer

# Database configuration
DB_PATH = Path(__file__).parent / "data" / "dictionary.db"

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

    #definition_panel {
        width: 70%;
        height: 1fr;
        padding: 1 2;
        overflow-y: scroll;
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
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("escape", "focus_search", "Search"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.words: List[str] = []
        self.db_conn = None
        self._search_cache: Dict[str, list] = {}

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
            yield Static(id="definition_panel")
        yield Footer()

    def action_focus_search(self) -> None:
        """Focus the search input."""
        self.query_one(Input).focus()

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle live search as the user types."""
        search_term = event.value.strip().lower()
        if len(search_term) >= 1:
            self.perform_fuzzy_search(search_term)
        else:
            self.query_one(OptionList).clear_options()

    @work(exclusive=True, thread=True)
    async def perform_fuzzy_search(self, search_term: str) -> None:
        """Perform optimized fuzzy search using RapidFuzz."""
        if search_term in self._search_cache:
            matches = self._search_cache[search_term]
        else:
            # Speed optimization: 
            # 1. Use fuzz.QRatio (faster than WRatio for short queries)
            # 2. Use thread=True to avoid blocking the event loop
            # 3. Limit processing for very short strings
            
            scorer = fuzz.QRatio if len(search_term) < 4 else fuzz.WRatio
            
            matches = process.extract(
                search_term, 
                self.words, 
                scorer=scorer, 
                limit=40,
                score_cutoff=50 if len(search_term) > 2 else 30
            )
            self._search_cache[search_term] = matches
            # Simple cache eviction
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
        for word, score, idx in matches:
            option_list.add_option(word)

    async def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
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
            "SELECT word, wordtype, definition FROM entries WHERE word = ?", 
            (word,)
        )
        results = cursor.fetchall()

        if results:
            content = f"[b underline $accent]{word.upper()}[/]\n\n"
            for i, (w, t, d) in enumerate(results, 1):
                content += f"[b]{i}.[/] [i $secondary]{t}[/] {d}\n\n"
            
            self.app.call_from_thread(self.query_one("#definition_panel", Static).update, content)
        else:
            self.app.call_from_thread(self.query_one("#definition_panel", Static).update, "Definition not found.")

    def on_unmount(self) -> None:
        """Close database connection on exit."""
        if self.db_conn:
            self.db_conn.close()

if __name__ == "__main__":
    app = DictionaryTUI()
    app.run()
