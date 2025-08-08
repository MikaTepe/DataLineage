import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from app.views.main_window import MainWindow


# =============================================================================
# Umfassende Protokollierung zur Fehlerdiagnose in der gebauten App
# =============================================================================
class StreamToLogger:
    """
    Eine Hilfsklasse, um Ausgaben (wie stdout, stderr) in einen Logger umzuleiten.
    """

    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        # Nötig für die io.TextIOWrapper-Schnittstelle, tut aber nichts.
        pass


def setup_logging():
    """
    Konfiguriert das Logging, um alle Ausgaben in eine Datei zu schreiben.
    Das ist essenziell für die Fehlersuche bei der .app-Datei.
    """
    # Die Log-Datei wird im Home-Verzeichnis des Benutzers erstellt
    log_file = os.path.join(os.path.expanduser("~"), "datalineage_visualizer.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename=log_file,
        filemode='w'  # Überschreibt die alte Log-Datei bei jedem Start
    )

    # Leite alle print()-Ausgaben (stdout) und Fehler (stderr) in die Log-Datei um
    stdout_logger = logging.getLogger('STDOUT')
    sys.stdout = StreamToLogger(stdout_logger, logging.INFO)
    stderr_logger = logging.getLogger('STDERR')
    sys.stderr = StreamToLogger(stderr_logger, logging.ERROR)

    logging.info("Logging-System initialisiert. Alle Ausgaben werden in die Datei umgeleitet.")
    print(f"Log-Datei befindet sich unter: {log_file}")
    print(f"Aktuelles Arbeitsverzeichnis: {os.getcwd()}")
    print(f"Python-Version: {sys.version}")


# =============================================================================

def main():
    """Hauptfunktion zum Starten der Anwendung."""
    # WICHTIG: Logging direkt am Anfang aufrufen
    setup_logging()

    logging.info("Anwendung startet.")
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    logging.info("Anwendung läuft.")
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()