import os
from dotenv import load_dotenv


def load_database_connections():
    """
    Lädt Datenbankverbindungen aus Umgebungsvariablen.
    Sucht nach Variablen im Format:
    - PROD_HOST, PROD_USER, PROD_PASSWORD, PROD_PORT
    - DEV_HOST, DEV_USER, DEV_PASSWORD, DEV_PORT
    usw. für jede definierte Umgebung (z.B. 'PROD', 'DEV').

    Gibt ein Dictionary zurück, das für die Anwendung nutzbar ist.
    """
    load_dotenv()  # Lädt Variablen aus der .env Datei, falls vorhanden

    connections = {}
    # Findet alle Umgebungs-Präfixe (z.B. 'PROD', 'DEV')
    prefixes = set(key.split('_')[0] for key in os.environ if '_' in key)

    for prefix in prefixes:
        host = os.getenv(f'{prefix}_HOST')
        user = os.getenv(f'{prefix}_USER')
        password = os.getenv(f'{prefix}_PASSWORD')
        port = os.getenv(f'{prefix}_PORT')

        # Prüft, ob alle vier Variablen für ein Präfix vorhanden sind
        if all([host, user, password, port]):
            # Baut den Namen der Datenquelle, z.B. 'PROD_DATABASE'
            connection_name = f'{prefix}_DATABASE'
            connections[connection_name] = {
                "host": host,
                "port": int(port),
                "user": user,
                "password": password
            }

    if not connections:
        print("WARNUNG: Keine vollständigen Datenbankverbindungen in den Umgebungsvariablen gefunden.")

    return connections
