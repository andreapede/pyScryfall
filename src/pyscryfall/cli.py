import argparse
import logging
import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from .client import PyScryfallClient, ScryfallError
from .models import Format, Rarity

def validate_colors(value: str) -> str:
    """Validate color string."""
    valid_colors = set('wubrg')
    if not value:
        return ""
    value = value.lower()
    if not set(value).issubset(valid_colors):
        raise argparse.ArgumentTypeError("Invalid colors. Use combinations of: w, u, b, r, g")
    return value

def validate_copies(value: str) -> int:
    """Validate number of copies."""
    try:
        ivalue = int(value)
        if 0 <= ivalue <= 4:
            return ivalue
        raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not in range [0-4]")

def parse_format(value: str) -> Format:
    """Parse format case-insensitively."""
    try:
        return Format(value.lower())
    except ValueError:
        valid = ", ".join([f.value for f in Format])
        raise argparse.ArgumentTypeError(f"Invalid format: {value}. Valid: {valid}")

def parse_rarity(value: str) -> Rarity:
    """Parse rarity case-insensitively."""
    try:
        return Rarity(value.lower())
    except ValueError:
        valid = ", ".join([r.value for r in Rarity])
        raise argparse.ArgumentTypeError(f"Invalid rarity: {value}. Valid: {valid}")

def get_interactive_input() -> Dict[str, Any]:
    """Get input parameters interactively."""
    print("\nWelcome to PyScryfall!")
    print("-" * 40)

    # Set
    set_code = input("Enter set code (e.g., neo): ").strip()

    # Format
    print("\nAvailable formats:")
    formats = list(Format)
    for i, fmt in enumerate(formats, 1):
        print(f"{i}. {fmt.value}")
    
    while True:
        choice = input("\nSelect format number (default: pauper): ").strip()
        if not choice:
            format_name = Format.PAUPER
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(formats):
                format_name = formats[idx]
                break
        except ValueError:
            pass
        print("Please enter a valid format number.")

    # Copies
    while True:
        choice = input("\nEnter number of copies (0-4, default: 0): ").strip()
        if not choice:
            copies = 0
            break
        try:
            copies = validate_copies(choice)
            break
        except argparse.ArgumentTypeError as e:
            print(e)

    # Colors
    while True:
        choice = input("\nEnter colors to filter (w,u,b,r,g or empty for all): ").strip()
        if not choice:
            colors = None
            break
        try:
            colors = validate_colors(choice)
            break
        except argparse.ArgumentTypeError as e:
            print(e)

    # Rarity
    # We didn't have interactive rarity in main.py, but let's add it as it's a new feature
    print("\nAvailable rarities (optional):")
    rarities = list(Rarity)
    for i, rar in enumerate(rarities, 1):
        print(f"{i}. {rar.value}")
    
    rarity = None
    while True:
        choice = input("\nSelect rarity number (empty for any): ").strip()
        if not choice:
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(rarities):
                rarity = rarities[idx]
                break
        except ValueError:
            pass
        print("Please enter a valid rarity number.")

    # Output
    output_path = input("\nEnter output file path (or empty for console only): ").strip()
    
    # Verbose
    verbose = input("\nEnable verbose mode? (y/n, default: n): ").lower().startswith('y')

    return {
        'set': set_code,
        'format': format_name,
        'copies': copies,
        'colors': colors,
        'rarity': rarity,
        'output': output_path,
        'verbose': verbose,
        # Defaults for others not in interactive mode yet
        'unique': 'prints',
        'order': 'name',
        'output_format': 'txt'
    }

def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch Magic: The Gathering cards from Scryfall API.",
        epilog="Example: pyscryfall --set neo --format pauper --copies 4"
    )
    parser.add_argument("--set", "-s", help="Set code (e.g., neo)")
    parser.add_argument("--format", "-f", type=parse_format, help="Game format", default=Format.PAUPER)
    parser.add_argument("--copies", "-c", type=validate_copies, default=0, help="Number of copies (0-4)")
    parser.add_argument("--colors", "-col", type=validate_colors, help="Colors (wubrg)")
    parser.add_argument("--rarity", "-r", type=parse_rarity, help="Card rarity")
    parser.add_argument("--unique", default="prints", help="Unique strategy (cards, prints, etc.)")
    parser.add_argument("--order", default="name", help="Sort order")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--output-format", choices=["txt", "json"], default="txt", help="Output format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    return parser

def main():
    parser = setup_parser()
    args = parser.parse_args()

    # Interactive mode if no set provided
    if not args.set:
        params = get_interactive_input()
    else:
        params = {
            'set': args.set,
            'format': args.format,
            'copies': args.copies,
            'colors': args.colors,
            'rarity': args.rarity,
            'unique': args.unique,
            'order': args.order,
            'output': args.output,
            'output_format': args.output_format,
            'verbose': args.verbose
        }

    client = PyScryfallClient(verbose=params['verbose'])

    try:
        cards = client.search_cards(
            set_code=params['set'],
            format_name=params['format'],
            colors=params['colors'],
            rarity=params['rarity'],
            unique=params['unique'],
            order=params['order']
        )

        # Output logic
        if params['verbose']:
            print(f"Found {len(cards)} cards.")

        if params['output_format'] == 'json':
            output_content = json.dumps(cards, indent=2)
        else:
            # TXT Decklist format
            lines = []
            for card in cards:
                set_name = card.get('set', '').upper()
                name = card.get('name', 'Unknown')
                if params['copies'] > 0:
                    lines.append(f"{params['copies']} {name} ({set_name})")
                else:
                    lines.append(f"{name} ({set_name})")
            output_content = "\n".join(lines)

        # Print to console
        print(output_content)

        # Save to file
        if params['output']:
            out_path = Path(params['output'])
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(output_content, encoding='utf-8')
            print(f"Saved results to {out_path}")

    except ScryfallError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
