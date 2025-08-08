from dataclasses import dataclass

@dataclass
class DataLineageConfig:
    """
    Konfiguration für den DataLineageService.
    """
    mock_mode: bool = True          # True = nutzt app.data.test_data statt DB
    max_depth: int = 5              # Maximale Rekursionstiefe
    include_ctes: bool = False      # CTEs (WITH-Klauseln) berücksichtigen
