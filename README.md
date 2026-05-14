# LexiSearch

**LexiSearch** is a blazing fast, terminal-based user interface (TUI) for browsing an English dictionary. Powered by **Textual** and **RapidFuzz**, it provides near-instantaneous fuzzy searching across 176,000+ words right from your terminal.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

## Features

- **🚀 Blazing Fast:** Loads the entire dictionary index into memory in milliseconds.
- **🔍 Fuzzy Search:** Typo-tolerant live search as you type.
- **💻 Modern TUI:** Beautiful, responsive terminal interface built with [Textual](https://textual.textualize.io/).
- **📚 Comprehensive:** Contains 176,023 definitions (based on the 1913 US Webster's Unabridged Dictionary).
- **🗃️ Smart Grouping:** Automatically groups multiple definitions for the same word.

## Installation

### From Source

Ensure you have Python 3.8+ installed.

```bash
# Clone the repository
git clone https://github.com/yourusername/LexiSearch.git
cd LexiSearch

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the application and dependencies
pip install -e .
```

## Usage

Once installed, you can launch the dictionary directly from your terminal:

```bash
lexisearch
```

### Controls

- **Type** to start searching.
- **Up / Down Arrows** to navigate through the matched words.
- **Esc** to refocus the search bar.
- **Q** or **Ctrl+C** to quit the application.

## Documentation

For more detailed information, please check our [Documentation](./docs/).

## Acknowledgements

- **Data Source:** Based on the Source Forge Project: [MySQL English Dictionary](https://sourceforge.net/projects/mysqlenglishdictionary/), which is based on the OPTED dictionary (1913 US Webster's Unabridged Dictionary).
- **Textual:** For the incredible TUI framework.
- **RapidFuzz:** For the hyper-optimized string matching algorithms.

## License

This project is open-source and available under the MIT License. The dictionary data is in the public domain. See [LICENSE](LICENSE) for more details.
