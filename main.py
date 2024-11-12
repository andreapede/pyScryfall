import requests
from typing import List, Dict
import sys
from time import sleep


class PyScryfall:
    def __init__(self):
        self.base_url = "https://api.scryfall.com"
        self.search_endpoint = "/cards/search"
        self.delay = 0.1  # 100ms delay between requests as per Scryfall guidelines

    def search_cards(self, set_code: str) -> List[Dict]:
        """
        Search for all Pauper-legal cards in a specific set.

        Args:
            set_code (str): The set code to search for

        Returns:
            List[Dict]: List of card data dictionaries
        """
        url = f"{self.base_url}{self.search_endpoint}"
        params = {
            'order': 'name',
            'q': f'f:pauper e:{set_code}'
        }

        try:
            all_cards = []
            has_more = True
            page = 1

            while has_more:
                response = requests.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                cards = data.get('data', [])
                all_cards.extend(cards)

                print(f"Fetched page {page} - Found {len(cards)} cards")

                has_more = data.get('has_more', False)
                if has_more:
                    params['page'] = page + 1
                    page += 1
                    sleep(self.delay)

            return all_cards

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Scryfall: {e}", file=sys.stderr)
            sys.exit(1)


def get_card_copies() -> int:
    """
    Ask user for the default number of copies for each card.

    Returns:
        int: Number of copies (0-4)
    """
    while True:
        try:
            num = int(input("Number before the any element of the list - use 0 for no number (0-4): "))
            if 0 <= num <= 4:
                return num
            else:
                print("Please between 0 and 4")
        except ValueError:
            print("Please a insert a valid number")


def main():
    client = PyScryfall()

    # Get set code from user
    set_code = input("Enter the set code (e.g., 'neo' for Kamigawa: Neon Dynasty): ").strip()

    # Fetch cards
    cards = client.search_cards(set_code)

    # Get default number of copies
    default_copies = get_card_copies()

    # Print results in a deck-list format
    print(f"\nFound {len(cards)} Pauper-legal cards in set {set_code.upper()}")
    print("\nDecklist format:")
    print("-" * 40)

    # Create decklist
    decklist = []
    for card in cards:
        if default_copies > 0:
            line = f"{default_copies} {card['name']} ({card['set'].upper()})"
        else:
            line = f"{card['name']} ({card['set'].upper()})"
        decklist.append(line)
        print(line)

    # Save to file option
    save = input("\nWould you like to save this list to a file? (y/n): ").lower()
    if save == 'y':
        filename = f"pauper_{set_code}_decklist.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for line in decklist:
                f.write(f"{line}\n")
        print(f"\nDecklist saved to {filename}")


if __name__ == "__main__":
    main()