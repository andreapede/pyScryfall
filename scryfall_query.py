import requests
import json
import argparse

def fetch_cards(set_name, legal_format='pauper', common_only=False):
    query = f'set:{set_name} legal:{legal_format}'
    if common_only:
        query += ' rarity:common'
    
    url = f"https://api.scryfall.com/cards/search"
    params = {
        'q': query,
        'order': 'set',
        'unique': 'prints'
    }
    cards = []
    while url:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            cards.extend(data['data'])
            url = data.get('next_page')
            params = {}  # Clear params for subsequent pages
        else:
            print(f"Error: {response.status_code}")
            break
    return cards, query

def save_to_file(cards, filename):
    with open(filename, 'w') as file:
        json.dump(cards, file, indent=4)

def print_cards(cards, number, set_name, legal_format, common_only, query):
    # Sort cards by collector number
    sorted_cards = sorted(cards, key=lambda x: int(''.join(filter(str.isdigit, x['collector_number']))) if x['collector_number'].isdigit() else float('inf'))
    
    for card in sorted_cards:
        if number == 0:
            print(f"{card['name']} ({card['set'].upper()})")
        else:
            print(f"{number} {card['name']} ({card['set'].upper()})")
    
    # Print summary information
    print(f"\nQuery parameters:")
    print(f"Set: {set_name}")
    print(f"Format: {legal_format}")
    print(f"Common only: {'yes' if common_only else 'no'}")
    print(f"API call: https://api.scryfall.com/cards/search?q={query}")
    print(f"Total cards: {len(cards)}")

def main():
    parser = argparse.ArgumentParser(description='Fetch cards from Scryfall.')
    parser.add_argument('set_name', type=str, help='The name of the card set')
    parser.add_argument('--legal_format', type=str, default='pauper', help='The legal format of the cards')
    parser.add_argument('--common_only', action='store_true', help='Fetch only common cards')
    parser.add_argument('--number_choice', type=int, default=0, help='Enter a number to put in front the list from 0 to 4')
    parser.add_argument('--output_choice', type=str, default='n', help='Do you want to save the result to a file? (y/n)')

    args = parser.parse_args()

    cards, query = fetch_cards(args.set_name, args.legal_format, args.common_only)
    
    # Pass query parameters to print_cards
    print_cards(cards, args.number_choice, args.set_name, args.legal_format, args.common_only, query)
    
    # Optionally save to file
    if args.output_choice == 'y':
        filename = input("Enter the filename to save the results: ")
        save_to_file(cards, filename)
        print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()