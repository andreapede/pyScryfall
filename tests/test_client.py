import pytest
import requests_mock
import re
from pyscryfall.client import PyScryfallClient, ScryfallError
from pyscryfall.models import Format, Rarity

@pytest.fixture
def client():
    return PyScryfallClient()

def test_search_cards_query_construction(client):
    with requests_mock.Mocker() as m:
        m.get(re.compile("https://api.scryfall.com/cards/search"), json={"data": [], "has_more": False})
        
        client.search_cards(set_code="neo", format_name=Format.PAUPER)
        
        history = m.request_history
        assert len(history) == 1
        qs = history[0].qs
        assert qs['q'] == ['f:pauper e:neo']

def test_search_cards_with_spaces_in_set(client):
    with requests_mock.Mocker() as m:
        m.get(re.compile("https://api.scryfall.com/cards/search"), json={"data": [], "has_more": False})
        
        client.search_cards(set_code="Kamigawa: Neon Dynasty")
        
        history = m.request_history
        qs = history[0].qs
        # Note: requests-mock might be lowercasing, or something else. 
        # Scryfall is case-insensitive anyway.
        assert qs['q'][0].lower() == 'e:"kamigawa: neon dynasty"'

def test_search_cards_pagination(client):
    with requests_mock.Mocker() as m:
        # Page 1
        m.get(
            "https://api.scryfall.com/cards/search",
            json={
                "object": "list",
                "total_cards": 2,
                "has_more": True,
                "next_page": "https://api.scryfall.com/cards/search?page=2",
                "data": [{"name": "Card 1"}]
            }
        )
        # Page 2
        m.get(
            "https://api.scryfall.com/cards/search?page=2",
            json={
                "object": "list",
                "total_cards": 2,
                "has_more": False,
                "data": [{"name": "Card 2"}]
            }
        )
        
        # Note: explicit set_code is needed to form query, otherwise it raises error
        cards = client.search_cards(set_code="neo")
        
        assert len(cards) == 2
        assert cards[0]['name'] == "Card 1"
        assert cards[1]['name'] == "Card 2"

def test_api_error(client):
    with requests_mock.Mocker() as m:
        m.get(re.compile("https://api.scryfall.com/cards/search"), status_code=404, json={"details": "Not Found"})
        
        with pytest.raises(ScryfallError) as excinfo:
            client.search_cards(set_code="invalid")
        
        assert "Not Found" in str(excinfo.value)
