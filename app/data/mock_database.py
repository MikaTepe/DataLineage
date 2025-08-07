from app.data.test_data import test_cache_data

class MockDatabase:
    """
    Simuliert eine Datenbankverbindung und -abfrage.
    Diese Klasse dient als einheitliche Schnittstelle für alle zukünftigen
    Datenbankimplementierungen (z.B. Exasol).
    """
    def __init__(self):
        # Nutzt die importierten, komplexen Daten
        self._mock_data = test_cache_data

    def get_available_databases(self):
        """Gibt die Namen der simulierten Datenbanken zurück."""
        return list(self._mock_data.keys())

    def get_schemas_for_database(self, db_name: str):
        """Gibt die Schemata für eine bestimmte Datenbank zurück."""
        return list(self._mock_data.get(db_name, {}).keys())

    def get_artifacts_for_schema(self, db_name: str, schema: str, artifact_type: str):
        """Gibt die Artefakte für ein bestimmtes Schema und einen Typ zurück."""
        return self._mock_data.get(db_name, {}).get(schema, {}).get(artifact_type, [])