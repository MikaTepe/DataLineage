import re

class SQLCleaner:
    """
    Bereinigt SQL-Text, entfernt Kommentare und normalisiert Whitespaces.
    """
    def clean(self, sql_text: str) -> str:
        if not sql_text:
            return ""
        # Zeilenkommentare entfernen
        sql_text = re.sub(r'--.*', '', sql_text)
        # Blockkommentare entfernen
        sql_text = re.sub(r'/\*.*?\*/', '', sql_text, flags=re.S)
        # Mehrfache Whitespaces reduzieren
        sql_text = re.sub(r'\s+', ' ', sql_text).strip()
        return sql_text
