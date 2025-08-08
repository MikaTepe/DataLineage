import sqlparse

class SQLParser:
    """
    Nutzt sqlparse, um SQL in Tokens zu zerlegen.
    """
    def parse(self, sql_text: str):
        return sqlparse.parse(sql_text)
