import requests
from typing import List, Dict, Optional, Set
import sys
from time import sleep
import argparse
import logging
from pathlib import Path
from enum import Enum, auto

class Format(Enum):
    """Supported Magic: The Gathering formats
    Formati supportati di Magic: The Gathering
    """
    STANDARD = 'standard'
    MODERN = 'modern'
    LEGACY = 'legacy'
    VINTAGE = 'vintage'
    COMMANDER = 'commander'
    PAUPER = 'pauper'
    PIONEER = 'pioneer'
    BRAWL = 'brawl'
    HISTORIC = 'historic'
    PENNY = 'penny'

class PyScryfall:
    def __init__(self, verbose: bool = False):
        self.base_url = "https://api.scryfall.com"
        self.search_endpoint = "/cards/search"
        self.delay = 0.1  # 100ms delay between requests as per Scryfall guidelines
        
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def search_cards(self, set_code: str, format_name: Format, colors: Optional[str] = None) -> List[Dict]:
        """
        Search for cards in a specific set and format.
        
        Args:
            set_code (str): The set code to search for
            format_name (Format): The format to filter by
            colors (str, optional): Color filter (w,u,b,r,g)
            
        Returns:
            List[Dict]: List of card data dictionaries
        """
        url = f"{self.base_url}{self.search_endpoint}"
        query = f'f:{format_name.value} e:{set_code}'
        
        if colors:
            query += f' c:{colors}'
            
        params = {
            'order': 'name',
            'q': query
        }
        
        try:
            all_cards = []
            has_more = True
            page = 1
            
            while has_more:
                self.logger.debug(f"Fetching page {page} from Scryfall API")
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                cards = data.get('data', [])
                all_cards.extend(cards)
                
                self.logger.info(f"Fetched page {page} - Found {len(cards)} cards")
                
                has_more = data.get('has_more', False)
                if has_more:
                    params['page'] = page + 1
                    page += 1
                    sleep(self.delay)
                    
            return all_cards
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data from Scryfall: {e}")
            sys.exit(1)

def validate_copies(value: str) -> int:
    """Validate the number of copies argument."""
    try:
        ivalue = int(value)
        if 0 <= ivalue <= 4:
            return ivalue
        raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not in range [0-4]")

def validate_colors(value: str) -> str:
    """Validate the colors argument."""
    valid_colors = set('wubrg')
    colors = set(value.lower())
    if not colors.issubset(valid_colors):
        raise argparse.ArgumentTypeError(f"Invalid colors. Use combinations of: w,u,b,r,g")
    return value.lower()

def validate_format(value: str) -> Format:
    """Validate the format argument."""
    try:
        return Format(value.lower())
    except ValueError:
        valid_formats = ", ".join(f.value for f in Format)
        raise argparse.ArgumentTypeError(
            f"Invalid format. Valid formats are: {valid_formats}"
        )

def get_interactive_input() -> Dict:
    """Get input parameters interactively from user."""
    print("\nWelcome to PyScryfall!")
    print("-" * 40)
    
    # Get set code
    set_code = input("Enter set code (e.g., neo for Kamigawa: Neon Dynasty): ").strip()
    
    # Get format
    print("\nAvailable formats:")
    for i, format_type in enumerate(Format, 1):
        print(f"{i}. {format_type.value}")
    while True:
        try:
            format_choice = input("\nSelect format number (default: pauper): ").strip()
            if not format_choice:
                format_name = Format.PAUPER
                break
            format_index = int(format_choice) - 1
            format_name = list(Format)[format_index]
            break
        except (ValueError, IndexError):
            print("Please enter a valid format number")
    
    # Get number of copies
    while True:
        try:
            copies_input = input("\nEnter number of copies (0-4, default: 0): ").strip()
            copies = validate_copies(copies_input) if copies_input else 0
            break
        except argparse.ArgumentTypeError as e:
            print(e)
    
    # Get colors
    while True:
        try:
            colors_input = input("\nEnter colors to filter (w,u,b,r,g or empty for all): ").strip()
            colors = validate_colors(colors_input) if colors_input else None
            break
        except argparse.ArgumentTypeError as e:
            print(e)
    
    # Get output file
    output_path = input("\nEnter output file path (or empty for console only): ").strip()
    output = Path(output_path) if output_path else None
    
    # Get verbose mode
    verbose = input("\nEnable verbose mode? (y/n, default: n): ").lower().startswith('y')
    
    return {
        'set': set_code,
        'format': format_name,
        'copies': copies,
        'colors': colors,
        'output': output,
        'verbose': verbose
    }

def setup_argparse() -> argparse.ArgumentParser:
    """Setup and return argument parser."""
    parser = argparse.ArgumentParser(
        description='Fetch Magic: The Gathering cards from Scryfall API.',
        epilog='Example: %(prog)s --set neo --format pauper --copies 4 --output neo_pauper.txt'
    )
    
    # Make all arguments optional to support interactive mode
    parser.add_argument(
        '--set', '-s',
        help='Set code (e.g., neo for Kamigawa: Neon Dynasty)'
    )
    
    parser.add_argument(
        '--format', '-f',
        type=validate_format,
        help='Game format to filter by',
        default=Format.PAUPER
    )
    
    parser.add_argument(
        '--copies', '-c',
        type=validate_copies,
        help='Number of copies for each card (0-4)',
        default=0
    )
    
    parser.add_argument(
        '--colors', '-col',
        type=validate_colors,
        help='Filter by colors (combination of w,u,b,r,g)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file path'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    return parser

def main():
    # Parse command line arguments
    parser = setup_argparse()
    args = parser.parse_args()
    
    # If no set code provided, switch to interactive mode
    if not args.set:
        params = get_interactive_input()
    else:
        # Use command line arguments
        params = {
            'set': args.set,
            'format': args.format,
            'copies': args.copies,
            'colors': args.colors,
            'output': args.output,
            'verbose': args.verbose
        }
    
    # Initialize PyScryfall with verbose flag
    client = PyScryfall(verbose=params['verbose'])
    
    try:
        # Fetch cards
        cards = client.search_cards(params['set'], params['format'], params['colors'])
        
        # Prepare output
        decklist = []
        for card in cards:
            if params['copies'] > 0:
                line = f"{params['copies']} {card['name']} ({card['set'].upper()})"
            else:
                line = f"{card['name']} ({card['set'].upper()})"
            decklist.append(line)
        
        # Print to console
        print(f"\nFound {len(cards)} {params['format'].value.title()}-legal cards in set {params['set'].upper()}")
        print("\nDecklist format:")
        print("-" * 40)
        for line in decklist:
            print(line)
        
        # Save to file if specified
        if params['output']:
            params['output'].parent.mkdir(parents=True, exist_ok=True)
            with params['output'].open('w', encoding='utf-8') as f:
                for line in decklist:
                    f.write(f"{line}\n")
            print(f"\nDecklist saved to {params['output']}")
            
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()