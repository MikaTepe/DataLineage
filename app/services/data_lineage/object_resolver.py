class ObjectResolver:
    """
    Löst Objekt-Namen (Tabellen, Views) auf – hier noch Dummy-Logik.
    """
    def __init__(self, connection=None):
        self.connection = connection

    def resolve(self, object_name: str) -> str:
        # TODO: Später DB-Lookup für Schema/Typ
        return object_name.strip().upper()
