# Contributing to LexiSearch

First off, thank you for considering contributing to LexiSearch! It's people like you that make open-source software great.

## Local Development Setup

1. Fork and clone the repository.
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install the application in editable mode with dev dependencies:
   ```bash
   pip install -e .
   pip install black isort pylint pyright
   ```
4. Make your changes in `src/lexisearch/`.
5. Run the linter checks before submitting your Pull Request:
   ```bash
   black src/
   isort src/
   pyright src/
   pylint src/
   ```

## Creating Pull Requests
- Provide a clear title and description of your changes.
- Ensure all CI tests pass.
