# LexiSearch Documentation

Welcome to the LexiSearch documentation!

## Overview
LexiSearch is an English dictionary TUI (Terminal User Interface).

## Project Structure
- `src/lexisearch/app.py`: Contains the main Textual application logic.
- `src/lexisearch/data/dictionary.db`: The SQLite database containing 176k+ definitions.
- `legacy_data/`: Contains legacy formats (CSV, MySQL) inherited from the upstream project.

## Contributing
We welcome contributions! Feel free to submit issues, pull requests, or feature requests on the GitHub repository.

### Development Setup
1. Clone the repo
2. Run `python -m venv .venv && source .venv/bin/activate`
3. Run `pip install -e .`
4. Run `lexisearch`
