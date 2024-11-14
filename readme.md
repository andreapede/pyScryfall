# PyScryfall

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-Attribution_Only-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Scryfall](https://img.shields.io/badge/API-Scryfall-orange.svg)
![Features](https://img.shields.io/badge/formats-10-purple.svg)

A Python script to fetch Magic: The Gathering cards from Scryfall API, with support for multiple formats and flexible search options.

## Features

### Core Features
- Search cards from specific Magic: The Gathering sets
- Filter by game format (Standard, Modern, Legacy, etc.)
- Display cards with customizable number of copies
- Generate deck lists in a standard format
- Export results to text files
- Color filtering support
- Respects Scryfall API rate limits
- Comprehensive error handling

### Supported Formats
- Standard
- Modern
- Legacy
- Vintage
- Commander
- Pauper
- Pioneer
- Brawl
- Historic
- Penny

### Interface Options
- Command Line Interface (CLI) with comprehensive arguments
- Interactive mode with guided input
- Automatic fallback to interactive mode when no arguments provided

## Requirements

- Python 3.6+
- `requests` library

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pyScryfall.git
cd pyScryfall
```

2. Install required packages:
```bash
pip install requests
```

## Usage

### Command Line Interface
```bash
# Basic usage with CLI arguments
python pyscryfall.py --set neo --format pauper --copies 4

# Full example with all options
python pyscryfall.py --set neo --format modern --copies 4 --colors ur --output deck.txt --verbose

# Show help
python pyscryfall.py --help
```

### Interactive Mode
```bash
# Launch in interactive mode
python pyscryfall.py
```

The interactive mode will guide you through:
1. Set selection
2. Format selection
3. Number of copies
4. Color filtering
5. Output file specification
6. Verbose mode toggle

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| --set | -s | Set code (e.g., neo) | Required |
| --format | -f | Game format | pauper |
| --copies | -c | Number of copies (0-4) | 0 |
| --colors | -col | Color filter (w,u,b,r,g) | None |
| --output | -o | Output file path | None |
| --verbose | -v | Enable verbose output | False |
| --version | | Show version | |

### Output Format

- With copies > 0: `N Card Name (SET)`
- With copies = 0: `Card Name (SET)`

Example output:
```
4 Lightning Bolt (DMR)
Consider (MID)
4 Counterspell (DMR)
```

## API Reference

This project uses the [Scryfall API](https://scryfall.com/docs/api). The script implements:
- Card search endpoint
- Format filtering
- Set-based filtering
- Color filtering
- Automatic pagination handling

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

This work is licensed under Attribution-Only License.

You are free to:
- Use, modify, and distribute this software for any purpose (including commercial use)
- Include this software in other projects
- Change the software to suit your needs

Under the following terms:
- You must give appropriate credit to the original author (Andrea Pede)
- Attribution must include the original author's name and a link to the original repository

## Acknowledgments

- [Scryfall](https://scryfall.com/) for providing the API and card data
- Magic: The Gathering and all card names are trademarks of Wizards of the Coast