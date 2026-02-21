import argparse
import pytest
from unittest.mock import MagicMock, patch
from pyscryfall.cli import validate_colors, validate_copies, main, setup_parser, parse_format, parse_rarity
from pyscryfall.models import Format, Rarity

def test_validate_colors():
    assert validate_colors("wub") == "wub"
    assert validate_colors("WUBRG") == "wubrg"
    assert validate_colors("") == ""
    with pytest.raises(argparse.ArgumentTypeError):
        validate_colors("xyz")

def test_validate_copies():
    assert validate_copies("0") == 0
    assert validate_copies("4") == 4
    with pytest.raises(argparse.ArgumentTypeError):
        validate_copies("5")
    with pytest.raises(argparse.ArgumentTypeError):
        validate_copies("a")

def test_parse_format():
    assert parse_format("standard") == Format.STANDARD
    assert parse_format("STANDARD") == Format.STANDARD
    assert parse_format("PaUpEr") == Format.PAUPER
    with pytest.raises(argparse.ArgumentTypeError):
        parse_format("invalid")

def test_parse_rarity():
    assert parse_rarity("common") == Rarity.COMMON
    assert parse_rarity("COMMON") == Rarity.COMMON
    with pytest.raises(argparse.ArgumentTypeError):
        parse_rarity("invalid")

def test_parser_defaults():
    parser = setup_parser()
    args = parser.parse_args([])
    assert args.format == Format.PAUPER
    assert args.copies == 0
    assert args.unique == "prints"

@patch('pyscryfall.cli.PyScryfallClient')
def test_main_with_arguments(MockClient, capsys):
    # Mock return value of search_cards
    mock_instance = MockClient.return_value
    mock_instance.search_cards.return_value = [{"name": "Test Card", "set": "neo"}]

    # Simulate command line arguments with mixed case format
    test_args = ["pyscryfall", "--set", "neo", "--format", "PAUPER"]
    with patch('sys.argv', test_args):
        main()
    
    # Verify client was called with correct arguments
    mock_instance.search_cards.assert_called_once()
    call_args = mock_instance.search_cards.call_args[1]
    assert call_args['set_code'] == 'neo'
    assert call_args['format_name'] == Format.PAUPER

    # Verify output
    captured = capsys.readouterr()
    assert "Test Card (NEO)" in captured.out

@patch('pyscryfall.cli.PyScryfallClient')
def test_main_json_output(MockClient, capsys):
    mock_instance = MockClient.return_value
    mock_instance.search_cards.return_value = [{"name": "Test Card", "set": "neo"}]

    test_args = ["pyscryfall", "--set", "neo", "--output-format", "json"]
    with patch('sys.argv', test_args):
        main()
    
    captured = capsys.readouterr()
    assert '"name": "Test Card"' in captured.out
