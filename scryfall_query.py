import requests
import json

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
    set_name = input("Enter the set name (i.e. NEO): ").upper()
    
    # Provide choices for legal format
    print("Choose the legal format:")
    print("1. pauper")
    print("2. standard")
    print("3. modern")
    print("4. legacy")
    print("5. vintage")
    legal_format_choice = int(input("Enter the format (default is 1 - Pauper): ") or 1)
    legal_formats = ['pauper', 'standard', 'modern', 'legacy', 'vintage']
    legal_format = legal_formats[legal_format_choice - 1]

    common_only = False
    if legal_format == 'pauper':
        common_only = input("Extract only common cards? (y/n, default n): ").strip().lower() == 'y'
    
    number_choice = int(input("Enter a number to put in front the list from 0 to 4 (default is 0): ") or 0)
    output_choice = input("Do you want to save the result to a file? (y/n, default n): ").strip().lower() or 'n'

    cards, query = fetch_cards(set_name, legal_format, common_only)
    
    # Pass query parameters to print_cards
    print_cards(cards, number_choice, set_name, legal_format, common_only, query)
    
    # Optionally save to file
    if output_choice == 'y':
        filename = input("Enter the filename to save the results: ")
        save_to_file(cards, filename)
        print(f"Results saved to {filename}")

if __name__ == "__main__":
    main()