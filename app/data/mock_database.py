import networkx as nx
from app.models.node import Node

class MockDatabase:
    """
    Simuliert eine Datenbankverbindung und -abfrage.
    Diese Klasse dient als einheitliche Schnittstelle für alle zukünftigen
    Datenbankimplementierungen (z.B. Exasol).
    """
    def __init__(self):
        # Diese Daten simulieren den Inhalt von zwei verschiedenen Datenbanken.
        # Jede zukünftige Datenbank-Implementierung sollte diese Struktur bereitstellen.
        self._mock_data = {
            "PROD_DB": {
                "DWH_CORE": {
                    "TABLE": ["F_SALES", "D_CUSTOMER"],
                    "VIEW": ["V_SALES_AGGREGATED"],
                    "ELT": []
                },
                "REPORTING": {
                    "TABLE": [],
                    "VIEW": ["V_CEO_DASHBOARD"],
                    "ELT": ["ELT_LOAD_REPORTS"]
                }
            },
            "DEV_DB": {
                "SANDBOX_MIKA": {
                    "TABLE": ["TEMP_ANALYSIS"],
                    "VIEW": [],
                    "ELT": ["MIKA_FEATURE_TEST"]
                }
            }
        }

    def get_available_databases(self):
        """Gibt die Namen der simulierten Datenbanken zurück."""
        return list(self._mock_data.keys())

    def get_schemas_for_database(self, db_name: str):
        """Gibt die Schemata für eine bestimmte Datenbank zurück."""
        return list(self._mock_data.get(db_name, {}).keys())

    def get_artifacts_for_schema(self, db_name: str, schema: str, artifact_type: str):
        """Gibt die Artefakte für ein bestimmtes Schema und einen Typ zurück."""
        return self._mock_data.get(db_name, {}).get(schema, {}).get(artifact_type, [])
