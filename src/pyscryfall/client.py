import logging
import time
from typing import List, Dict, Optional, Union
import requests

from .models import Format, Rarity

class ScryfallError(Exception):
    """Base exception for Scryfall API errors."""
    pass

class PyScryfallClient:
    """Client for interacting with the Scryfall API."""

    BASE_URL = "https://api.scryfall.com"
    SEARCH_ENDPOINT = "/cards/search"
    DELAY = 0.1  # 100ms delay between requests

    def __init__(self, verbose: bool = False):
        """
        Initialize the client.

        Args:
            verbose: If True, enables debug logging.
        """
        self.logger = logging.getLogger(__name__)
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def search_cards(
        self,
        set_code: Optional[str] = None,
        format_name: Optional[Union[Format, str]] = None,
        colors: Optional[str] = None,
        rarity: Optional[Union[Rarity, str]] = None,
        unique: str = "prints",
        order: str = "name"
    ) -> List[Dict]:
        """
        Search for cards using specific filters.

        Args:
            set_code: The set code (e.g., 'neo').
            format_name: The format legality (e.g., 'pauper').
            colors: Color string (e.g., 'wubrg', 'u', 'r').
            rarity: Card rarity (e.g., 'common').
            unique: Strategy for omitting duplicates ('cards', 'art', 'prints').
            order: Sort order ('name', 'set', 'released', 'rarity', 'color', 'usd', 'tix', 'eur', 'cmc', 'power', 'toughness', 'edhrec', 'artist').

        Returns:
            A list of card dictionaries.
        """
        query_parts = []
        
        # Build the query string 'q'
        if format_name:
            fmt_value = format_name.value if isinstance(format_name, Format) else format_name
            query_parts.append(f"f:{fmt_value}")
        
        if set_code:
            # Wrap in quotes if it contains spaces
            if " " in set_code:
                query_parts.append(f'e:"{set_code}"')
            else:
                query_parts.append(f"e:{set_code}")
        
        if colors:
            query_parts.append(f"c:{colors}")

        if rarity:
            rarity_value = rarity.value if isinstance(rarity, Rarity) else rarity
            query_parts.append(f"r:{rarity_value}")

        if not query_parts:
            # If no specific filters, we can't just search everything blindly without a query.
            # Scryfall requires 'q'.
            raise ScryfallError("At least one filter (set, format, etc.) must be provided.")

        full_query = " ".join(query_parts)
        params = {
            'q': full_query,
            'unique': unique,
            'order': order
        }

        return self._fetch_all_pages(self.SEARCH_ENDPOINT, params)

    def _fetch_all_pages(self, endpoint: str, initial_params: Dict) -> List[Dict]:
        """Helper to fetch all pages of a search query."""
        # Check if we are using a full URL or relative endpoint
        if endpoint.startswith("http"):
             url = endpoint
        else:
             url = f"{self.BASE_URL}{endpoint}"

        all_cards = []
        has_more = True
        page = 1
        params = initial_params

        self.logger.info(f"Starting search with params: {params}")

        try:
            while has_more:
                self.logger.debug(f"Fetching page {page}...")
                
                # Make request
                response = requests.get(url, params=params)
                
                # Check for errors
                if response.status_code != 200:
                    try:
                        error_data = response.json()
                        msg = error_data.get('details', response.reason)
                    except Exception:
                        msg = response.reason
                    raise ScryfallError(f"API Error ({response.status_code}): {msg}")

                data = response.json()
                cards = data.get('data', [])
                all_cards.extend(cards)

                self.logger.info(f"Page {page}: fetched {len(cards)} cards.")

                has_more = data.get('has_more', False)
                if has_more:
                    next_page = data.get('next_page')
                    if next_page:
                        url = next_page
                        params = {} # Query params are already encoded in next_page URL
                    else:
                        # Fallback logic if next_page is missing (unlikely)
                        params['page'] = page + 1
                    
                    page += 1
                    time.sleep(self.DELAY)

            return all_cards

        except requests.exceptions.RequestException as e:
            raise ScryfallError(f"Network error: {e}")
