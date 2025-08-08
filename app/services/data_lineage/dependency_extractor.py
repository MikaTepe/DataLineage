class DependencyExtractor:
    """
    Extrahiert Tabellen-/View-Abhängigkeiten aus einem geparsten SQL-Statement.
    """
    def extract(self, parsed_statements) -> list:
        deps = []
        for stmt in parsed_statements:
            tokens = [t for t in stmt.tokens if not t.is_whitespace]
            for idx, token in enumerate(tokens):
                if token.ttype is None and token.value.upper() in ("FROM", "JOIN"):
                    if idx + 1 < len(tokens):
                        deps.append(tokens[idx + 1].value)
        return deps
