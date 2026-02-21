# PyScryfall

PyScryfall is a Python wrapper and CLI tool for the Scryfall API, designed to help Magic: The Gathering players and developers search for cards, build decklists, and filter sets with ease.

This project is a refactored and improved version of the original `pyScryfall` script, now available as a proper Python package.

## Features

-   **Advanced Filtering**: Search by Set, Format, Color, and Rarity.
-   **Flexible Output**: Generate decklists (TXT) or data exports (JSON).
-   **Interactive Mode**: Guided CLI if no arguments are provided.
-   **Robust Client**: Handles pagination and rate limiting automatically.
-   **Library Support**: Can be imported and used in other Python projects.

## Installation

You can install PyScryfall directly from the source:

```bash
git clone https://github.com/yourusername/pyScryfall.git
cd pyScryfall
pip install .
```

## Usage

### Command Line Interface (CLI)

Run `pyscryfall` from your terminal.

**Interactive Mode:**
Simply run the command without arguments:
```bash
pyscryfall
```

**Search for a Set (Pauper Legal):**
```bash
pyscryfall --set neo --format pauper
```

**Filter by Color and Rarity:**
```bash
pyscryfall --set neo --colors ur --rarity common
```

**Generate a Decklist with 4 Copies:**
```bash
pyscryfall --set neo --format pauper --copies 4 --output my_deck.txt
```

**Export Data to JSON:**
```bash
pyscryfall --set neo --output-format json > neo_cards.json
```

**Command Line Arguments:**
-   `--set`, `-s`: Set code (e.g., `neo`).
-   `--format`, `-f`: Format legality (e.g., `pauper`, `standard`, `commander`).
-   `--colors`, `-col`: Colors (e.g., `wubrg`, `u`, `r`).
-   `--rarity`, `-r`: Rarity (e.g., `common`, `rare`).
-   `--copies`, `-c`: Number of copies to prefix (0-4).
-   `--unique`: Unique strategy (`cards`, `prints`, `art`). Default: `prints`.
-   `--order`: Sort order (`name`, `set`, etc.). Default: `name`.
-   `--output`, `-o`: Output file path.
-   `--output-format`: Output format (`txt` or `json`).

### Python Library

You can use `pyscryfall` as a library in your own scripts.

```python
from pyscryfall import PyScryfallClient, Format, Rarity

client = PyScryfallClient()

# Search for common blue cards in Kamigawa: Neon Dynasty
cards = client.search_cards(
    set_code="neo",
    format_name=Format.PAUPER,
    colors="u",
    rarity=Rarity.COMMON
)

for card in cards:
    print(f"{card['name']} ({card['set'].upper()})")
```

## Development

To install dependencies for development (including tests):

```bash
pip install .[dev]
```

To run tests:

```bash
pytest
```

## License

Attribution-Only License.
Original work by Andrea Pede. Refactored by Jules.
