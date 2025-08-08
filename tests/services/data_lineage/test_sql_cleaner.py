import pytest
from app.services.data_lineage.sql_cleaner import SQLCleaner

@pytest.fixture
def cleaner():
    """Stellt eine Instanz von SQLCleaner für jeden Test bereit."""
    return SQLCleaner()

def test_remove_line_comments(cleaner):
    """Testet das Entfernen von Zeilenkommentaren (--)."""
    sql = "SELECT * FROM my_table; -- Dies ist ein Kommentar"
    expected = "SELECT * FROM my_table;"
    assert cleaner.clean(sql) == expected

def test_remove_block_comments(cleaner):
    """Testet das Entfernen von Blockkommentaren (/* ... */)."""
    sql = "SELECT /* Ein Blockkommentar */ col1, col2 FROM other_table;"
    expected = "SELECT col1, col2 FROM other_table;"
    assert cleaner.clean(sql) == expected

def test_normalize_whitespaces(cleaner):
    """Testet die Normalisierung von mehrfachen Leerzeichen und Tabs."""
    sql = "SELECT    col1,  col2\nFROM\t a_table"
    expected = "SELECT col1, col2 FROM a_table"
    assert cleaner.clean(sql) == expected

def test_empty_string(cleaner):
    """Testet das Verhalten bei einer leeren Eingabe."""
    assert cleaner.clean("") == ""

def test_no_comments(cleaner):
    """Stellt sicher, dass SQL ohne Kommentare unverändert bleibt."""
    sql = "SELECT id FROM users WHERE id = 1"
    assert cleaner.clean(sql) == sql