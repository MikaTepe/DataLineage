import sys
import logging
from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv

from app.views.main_window import MainWindow

# Globale Ausnahmebehandlung für bessere Fehlermeldungen
def exception_hook(exctype, value, tb):
    logging.error("Uncaught exception", exc_info=(exctype, value, tb))
    sys.__excepthook__(exctype, value, tb)
    sys.exit(1)

sys.excepthook = exception_hook

if __name__ == "__main__":
    # Konfigurieren des Loggings
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Anwendung startet.")

    # Umgebungsvariablen laden
    load_dotenv()

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    logging.info("Anwendung läuft.")
    sys.exit(app.exec_())