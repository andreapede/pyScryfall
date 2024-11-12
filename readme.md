# PyScryfall

![Python](https://img.shields.io/badge/python-3.6+-blue.svg)
![License](https://img.shields.io/badge/license-Attribution_Only-green.svg)
![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Scryfall](https://img.shields.io/badge/API-Scryfall-orange.svg)
![Format](https://img.shields.io/badge/format-Pauper-purple.svg)

A Python script to fetch Magic: The Gathering cards from Scryfall API, specifically designed for Pauper format deck building.

## Features

- Search Pauper-legal cards from specific Magic: The Gathering sets
- Display cards with customizable number of copies
- Generate deck lists in a standard format
- Export results to text files
- Respects Scryfall API rate limits
- Error handling for API requests

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

Run the script:
```bash
python pyscryfall.py
```

The script will:
1. Ask for a set code (e.g., 'neo' for Kamigawa: Neon Dynasty)
2. Ask for the default number of copies for each card (0-4)
3. Display the list of Pauper-legal cards from the specified set
4. Offer to save the results to a text file

### Output Format

- When copies > 0: `N Card Name (SET)`
- When copies = 0: `Card Name (SET)`

Example output:
```
4 Lightning Bolt (DMR)
4 Counterspell (DMR)
```
or with 0
```
Lightning Bolt (DMR)
Counterspell (DMR)

```

## API Reference

This project uses the [Scryfall API](https://scryfall.com/docs/api). The script implements:
- Card search endpoint
- Pauper format filtering
- Set-based filtering
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
