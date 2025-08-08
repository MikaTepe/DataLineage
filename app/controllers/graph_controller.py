import logging
import pyexasol
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

# Lokale Anwendungsimporte
from app.config import load_database_connections
from app.models.graph_model import GraphModel
from app.services.data_service import DataService
from app.services.graph_analysis_service import GraphAnalysisService
from app.services.data_lineage import DataLineageService, DataLineageConfig


class DataLineageWorker(QThread):
    """
    Führt die Graphenerstellung in einem separaten Thread aus,
    um die UI nicht zu blockieren. Unterstützt sowohl Mock- als auch Real-Modus.
    """
    finished_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)

    def __init__(self, data_service, selections, connection=None):
        super().__init__()
        self.data_service = data_service
        self.selections = selections
        self.connection = connection
        self.mock_mode = connection is None

    def run(self):
        """Die eigentliche Arbeit, die im Thread ausgeführt wird."""
        try:
            # Der DataService wird so konfiguriert, dass er den richtigen Modus verwendet
            self.data_service.mock_mode = self.mock_mode
            self.data_service.connection = self.connection

            graph_obj = self.data_service.get_graph_for_artifact(self.selections)
            self.finished_signal.emit(graph_obj)
        except Exception as e:
            logging.error("Fehler im DataLineageWorker", exc_info=True)
            self.error_signal.emit(f"Fehler bei der Graph-Erstellung: {e}")
        finally:
            # Wichtig: Die im Controller erstellte Verbindung hier wieder schließen
            if self.connection:
                try:
                    self.connection.close()
                except pyexasol.ExaError as ex:
                    logging.warning(f"Fehler beim Schließen der DB-Verbindung: {ex}")


class GraphController(QObject):
    """
    Steuert den Datenfluss zwischen der UI und dem DataService.
    Leitet Anfragen zur Graphenerzeugung und für Metadaten weiter
    und managt die asynchrone Ausführung.
    """

    def __init__(self, model: GraphModel, canvas):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.model = model
        self.canvas = canvas
        self.worker = None

        # Lädt DB-Verbindungen aus .env-Datei oder Umgebungsvariablen
        self.db_connections = load_database_connections()

        # Initialisiert den DataService (wird für Mock-Modus und als Dispatcher genutzt)
        self.data_service = DataService(mock_mode=True)  # Startet standardmäßig im Mock-Modus

        if not self.db_connections:
            self.logger.warning("Keine DB-Verbindungen in .env gefunden. Nur Mock-Modus verfügbar.")
            # Optional: Informieren Sie den Benutzer, dass nur der Mock-Modus funktioniert
            # QMessageBox.information(self.canvas, "Hinweis", "Keine Datenbankverbindungen konfiguriert. Nur der Mock-Modus ist verfügbar.")

    def get_data_service(self) -> DataService:
        """Gibt den DataService für UI-Datenabfragen (z.B. Artefaktlisten) zurück."""
        return self.data_service

    def load_graph(self, selections: dict):
        """
        Startet den DataLineageWorker, um den Graphen asynchron zu laden.
        Entscheidet anhand der Auswahl, ob der Mock- oder Real-Modus genutzt wird.
        """
        if not selections or not selections.get('artifact'):
            self.model.clear()
            return

        selected_source = selections.get("data_source")

        # Entscheidung: Mock- vs. Real-Modus
        if selected_source in self.db_connections:
            # --- Real-Modus ---
            self.logger.info(f"Starte Analyse im Real-Modus für Quelle: {selected_source}")
            self.canvas.show_loading_message("Verbinde mit Datenbank und analysiere Artefakt...")
            try:
                conn_data = self.db_connections[selected_source]
                connection = pyexasol.connect(
                    dsn=f"{conn_data['host']}:{conn_data['port']}",
                    user=conn_data['user'],
                    password=conn_data['password']
                )
                self.logger.info(f"Verbindung zu {selected_source} hergestellt.")

                # Starte den Worker mit der offenen Verbindung
                self.worker = DataLineageWorker(self.data_service, selections, connection)
                self.worker.finished_signal.connect(self.on_loading_finished)
                self.worker.error_signal.connect(self.on_loading_error)
                self.worker.start()

            except Exception as e:
                error_msg = f"Fehler bei der Datenbankverbindung: {e}"
                self.logger.error(error_msg, exc_info=True)
                self.on_loading_error(error_msg)
        else:
            # --- Mock-Modus ---
            self.logger.info("Starte Analyse im Mock-Modus.")
            self.canvas.show_loading_message("Lade Mock-Daten...")
            self.worker = DataLineageWorker(self.data_service, selections)  # Ohne Verbindung
            self.worker.finished_signal.connect(self.on_loading_finished)
            self.worker.error_signal.connect(self.on_loading_error)
            self.worker.start()

    def on_loading_finished(self, graph_obj):
        """Wird aufgerufen, wenn der Worker die Graphenerstellung beendet hat."""
        self.model.load_graph(graph_obj)
        self.worker = None

    def on_loading_error(self, error_message):
        """Wird aufgerufen, wenn im Worker ein Fehler auftritt."""
        self.model.error_occurred.emit(error_message)
        self.worker = None
        QMessageBox.critical(self.canvas, "Analysefehler", error_message)

    def search_and_highlight_node(self, search_term: str):
        """Sucht den ersten passenden Knoten und hebt ihn hervor."""
        if not search_term:
            self.canvas.clear_highlighting()
            return
        found_node_id = next(
            (node_id for node_id, attrs in self.model.graph.nodes(data=True)
             if (obj := attrs.get('data')) and search_term.lower() in obj.name.lower()),
            None
        )
        if found_node_id:
            self.canvas.highlight_node(found_node_id)
            self.canvas.zoom_to_node(found_node_id)
        else:
            self.canvas.clear_highlighting()

    def highlight_predecessors(self, node_id: str):
        """Hebt den Knoten und alle seine Vorgänger hervor."""
        if not self.model.graph or not node_id:
            return
        analysis_service = GraphAnalysisService(self.model.graph)
        self.canvas.highlight_nodes(list(analysis_service.get_all_predecessors(node_id)))

    def clear_node_highlighting(self):
        """Entfernt alle Hervorhebungen."""
        self.canvas.clear_highlighting()
