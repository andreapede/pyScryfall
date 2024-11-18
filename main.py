import requests  # Import the requests module for making HTTP requests / Importa il modulo requests per effettuare richieste HTTP
from typing import List, Dict, Optional, Set  # Import type hints from the typing module / Importa suggerimenti di tipo dal modulo typing
import sys  # Import the sys module for system-specific parameters and functions / Importa il modulo sys per parametri e funzioni specifici del sistema
from time import sleep  # Import the sleep function to add delays / Importa la funzione sleep per aggiungere ritardi
import argparse  # Import the argparse module for parsing command-line arguments / Importa il modulo argparse per l'analisi degli argomenti della riga di comando
import logging  # Import the logging module for logging messages / Importa il modulo logging per registrare messaggi
from pathlib import Path  # Import the Path class from pathlib for filesystem paths / Importa la classe Path da pathlib per i percorsi del filesystem
from enum import Enum, auto  # Import Enum and auto from the enum module for enumerations / Importa Enum e auto dal modulo enum per enumerazioni

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
        """
        Initialize the PyScryfall client.
        Inizializza il client PyScryfall.
        
        Args:
            verbose (bool): Enable verbose logging if True.
                            Abilita il logging verboso se True.
        """
        self.base_url = "https://api.scryfall.com"  # Base URL for the Scryfall API / URL di base per l'API di Scryfall
        self.search_endpoint = "/cards/search"  # Endpoint for searching cards / Endpoint per la ricerca di carte
        self.delay = 0.1  # 100ms delay between requests as per Scryfall guidelines / Ritardo di 100 ms tra le richieste secondo le linee guida di Scryfall
        
        # Setup logging
        log_level = logging.DEBUG if verbose else logging.INFO  # Set logging level based on verbose flag / Imposta il livello di registrazione in base al flag verbose
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)  # Get a logger instance / Ottieni un'istanza del logger
        
    def search_cards(self, set_code: str, format_name: Format, colors: Optional[str] = None) -> List[Dict]:
        """
        Search for cards in a specific set and format.
        Cerca carte in un set specifico e formato.
        
        Args:
            set_code (str): The set code to search for.
                            Il codice del set da cercare.
            format_name (Format): The format to filter by.
                                  Il formato da filtrare.
            colors (str, optional): Color filter (w,u,b,r,g).
                                    Filtro colore (w,u,b,r,g).
            
        Returns:
            List[Dict]: List of card data dictionaries.
                        Elenco di dizionari di dati delle carte.
        """
        url = f"{self.base_url}{self.search_endpoint}"  # Construct the full URL for the search endpoint / Costruisci l'URL completo per l'endpoint di ricerca
        query = f'f:{format_name.value} e:{set_code}'  # Form the query string / Forma la stringa di query
        
        if colors:
            query += f' c:{colors}'  # Append color filters to the query if provided / Aggiungi filtri di colore alla query se forniti
            
        params = {
            'order': 'name',
            'q': query
        }
        
        try:
            all_cards = []  # Initialize an empty list to store card data / Inizializza una lista vuota per memorizzare i dati delle carte
            has_more = True  # Flag to control pagination / Flag per controllare la paginazione
            page = 1  # Start from the first page / Inizia dalla prima pagina
            
            while has_more:
                self.logger.debug(f"Fetching page {page} from Scryfall API")  # Log the current page being fetched / Registra la pagina corrente in fase di recupero
                response = requests.get(url, params=params)  # Make the API request / Effettua la richiesta API
                response.raise_for_status()  # Raise an error if the request failed / Solleva un errore se la richiesta è fallita
                
                data = response.json()  # Parse the JSON response / Analizza la risposta JSON
                cards = data.get('data', [])  # Extract card data / Estrai i dati delle carte
                all_cards.extend(cards)  # Add the cards to the list / Aggiungi le carte alla lista
                
                self.logger.info(f"Fetched page {page} - Found {len(cards)} cards")  # Log the number of cards fetched / Registra il numero di carte recuperate
                
                has_more = data.get('has_more', False)  # Check if there are more pages / Controlla se ci sono altre pagine
                if has_more:
                    params['page'] = page + 1  # Increment the page number / Incrementa il numero di pagina
                    page += 1
                    sleep(self.delay)  # Wait for a short delay before next request / Attendi un breve ritardo prima della prossima richiesta
                    
            return all_cards
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data from Scryfall: {e}")  # Log an error message if the request failed / Registra un messaggio di errore se la richiesta è fallita
            sys.exit(1)  # Exit the program with an error code / Esci dal programma con un codice di errore

def validate_copies(value: str) -> int:
    """Validate the number of copies argument.
    Valida l'argomento del numero di copie.
    """
    try:
        ivalue = int(value)  # Convert the value to an integer / Converti il valore in un intero
        if 0 <= ivalue <= 4:
            return ivalue  # Return the value if it is within the valid range / Restituisci il valore se è all'interno dell'intervallo valido
        raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not in range [0-4]")  # Raise an error if the value is invalid / Solleva un errore se il valore non è valido

def validate_colors(value: str) -> str:
    """Validate the colors argument.
    Valida l'argomento dei colori.
    """
    valid_colors = set('wubrg')  # Define the set of valid color characters / Definisci l'insieme dei caratteri di colore validi
    colors = set(value.lower())  # Convert the input value to lowercase / Converti il valore di input in minuscolo
    if not colors.issubset(valid_colors):
        raise argparse.ArgumentTypeError(f"Invalid colors. Use combinations of: w,u,b,r,g")  # Raise an error if the input contains invalid colors / Solleva un errore se l'input contiene colori non validi
    return value.lower()

def validate_format(value: str) -> Format:
    """Validate the format argument.
    Valida l'argomento del formato.
    """
    try:
        return Format(value.lower())  # Convert the value to a Format enum / Converti il valore in un'enumerazione Format
    except ValueError:
        valid_formats = ", ".join(f.value for f in Format)  # Create a string of valid formats / Crea una stringa di formati validi
        raise argparse.ArgumentTypeError(
            f"Invalid format. Valid formats are: {valid_formats}"
        )

def get_interactive_input() -> Dict:
    """
    Get input parameters interactively from user.
    Ottieni i parametri di input interattivamente dall'utente.
    
    Returns:
        Dict: A dictionary of input parameters.
              Un dizionario di parametri di input.
    """
    print("\nWelcome to PyScryfall!")
    print("-" * 40)
    
    # Get set code
    set_code = input("Enter set code (e.g., neo for Kamigawa: Neon Dynasty): ").strip()  # Prompt the user for the set code / Richiedi all'utente il codice del set
    
    # Get format
    print("\nAvailable formats:")
    for i, format_type in enumerate(Format, 1):
        print(f"{i}. {format_type.value}")  # Display the available formats / Mostra i formati disponibili
    while True:
        try:
            format_choice = input("\nSelect format number (default: pauper): ").strip()  # Prompt the user to select a format / Richiedi all'utente di selezionare un formato
            if not format_choice:
                format_name = Format.PAUPER  # Default to pauper format if no choice is made / Imposta il formato predefinito su pauper se non viene effettuata alcuna scelta
                break
            format_index = int(format_choice) - 1
            format_name = list(Format)[format_index]  # Map the user's choice to the Format enum / Mappa la scelta dell'utente all'enumerazione Format
            break
        except (ValueError, IndexError):
            print("Please enter a valid format number")  # Prompt the user again if the input is invalid / Richiedi nuovamente all'utente se l'input non è valido
    
    # Get number of copies
    while True:
        try:
            copies_input = input("\nEnter number of copies (0-4, default: 0): ").strip()  # Prompt the user for the number of copies / Richiedi all'utente il numero di copie
            copies = validate_copies(copies_input) if copies_input else 0  # Validate the input and set default / Valida l'input e imposta il valore predefinito
            break
        except argparse.ArgumentTypeError as e:
            print(e)
    
    # Get colors
    while True:
        try:
            colors_input = input("\nEnter colors to filter (w,u,b,r,g or empty for all): ").strip()  # Prompt the user for color filters / Richiedi all'utente filtri di colore
            colors = validate_colors(colors_input) if colors_input else None  # Validate the input and set default / Valida l'input e imposta il valore predefinito
            break
        except argparse.ArgumentTypeError as e:
            print(e)
    
    # Get output file
    output_path = input("\nEnter output file path (or empty for console only): ").strip()  # Prompt the user for the output file path / Richiedi all'utente il percorso del file di output
    output = Path(output_path) if output_path else None  # Convert the input to a Path object / Converti l'input in un oggetto Path
    
    # Get verbose mode
    verbose = input("\nEnable verbose mode? (y/n, default: n): ").lower().startswith('y')  # Prompt the user to enable verbose mode / Richiedi all'utente di abilitare la modalità verbosa
    
    return {
        'set': set_code,
        'format': format_name,
        'copies': copies,
        'colors': colors,
        'output': output,
        'verbose': verbose
    }

def setup_argparse() -> argparse.ArgumentParser:
    """Setup and return argument parser.
    Configura e restituisci l'analizzatore di argomenti.
    """
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
    parser = setup_argparse()  # Setup the argument parser / Configura l'analizzatore di argomenti
    args = parser.parse_args()  # Parse the command-line arguments / Analizza gli argomenti della riga di comando
    
    # If no set code provided, switch to interactive mode
    if not args.set:
        params = get_interactive_input()  # Get input from the user interactively / Ottieni input dall'utente in modo interattivo
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
    client = PyScryfall(verbose=params['verbose'])  # Initialize the PyScryfall client / Inizializza il client PyScryfall
    
    try:
        # Fetch cards
        cards = client.search_cards(params['set'], params['format'], params['colors'])  # Search for cards using the provided parameters / Cerca carte utilizzando i parametri forniti
        
        # Prepare output
        decklist = []  # Initialize an empty list for the decklist / Inizializza una lista vuota per la lista del mazzo
        for card in cards:
            if params['copies'] > 0:
                line = f"{params['copies']} {card['name']} ({card['set'].upper()})"  # Format the output line with copies / Format the output line with copies
            else:
                line = f"{card['name']} ({card['set'].upper()})"  # Format the output line without copies / Format the output line without copies
            decklist.append(line)  # Add the line to the decklist / Aggiungi la riga alla lista del mazzo
        
        # Print to console
        print(f"\nFound {len(cards)} {params['format'].value.title()}-legal cards in set {params['set'].upper()}")  # Print the summary / Stampa il riepilogo
        print("\nDecklist format:")
        print("-" * 40)
        for line in decklist:
            print(line)  # Print each line of the decklist / Stampa ogni riga della lista del mazzo
        
        # Save to file if specified
        if params['output']:
            params['output'].parent.mkdir(parents=True, exist_ok=True)  # Create the output directory if it doesn't exist / Crea la directory di output se non esiste
            with params['output'].open('w', encoding='utf-8') as f:
                for line in decklist:
                    f.write(f"{line}\n")  # Write each line to the output file / Scrivi ogni riga nel file di output
            print(f"\nDecklist saved to {params['output']}")  # Print confirmation message / Stampa il messaggio di conferma
            
    except Exception as e:
        logging.error(f"An error occurred: {e}")  # Log an error message if an exception occurs / Registra un messaggio di errore se si verifica un'eccezione
        sys.exit(1)  # Exit the program with an error code / Esci dal programma con un codice di errore

if __name__ == "__main__":
    main()  # Call the main function / Chiama la funzione main
