from app.data import test_data

class SQLExecutor:
    """
    Holt SQL-Text für ein Artefakt – entweder aus Mock-Daten oder einer echten DB.
    """
    def __init__(self, config, connection=None):
        self.config = config
        self.connection = connection

    def get_sql_for_artifact(self, artifact_name: str) -> str:
        if self.config.mock_mode:
            return test_data.sql_definitions.get(artifact_name, "")
        if not self.connection:
            return ""
        cur = self.connection.cursor()
        cur.execute(f"SELECT sql_text FROM metadata WHERE name='{artifact_name}'")
        row = cur.fetchone()
        return row[0] if row else ""
