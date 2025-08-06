from PyQt5.QtCore import QObject
from app.services.data_service import DataService
from app.models.graph_model import GraphModel

class GraphController(QObject):
    """
    Steuert den Datenfluss zwischen der UI und dem DataService.
    Leitet Anfragen zur Graphenerzeugung und für Metadaten weiter.
    """
    def __init__(self, model: GraphModel):
        super().__init__()
        self.model = model
        self.data_service = DataService()

    def load_graph(self, selections: dict):
        """
        Fordert einen Graphen über den zentralen Endpunkt im DataService an
        und lädt das Ergebnis in das GraphModel.
        """
        if not selections or not selections.get('artifact'):
            self.model.clear()
            return

        # Einziger Aufrufpunkt: die vereinheitlichte Methode im DataService
        graph_obj = self.data_service.get_graph_for_artifact(selections)
        self.model.load_graph(graph_obj)

    def get_data_service(self) -> DataService:
        """
        Gibt eine Referenz auf den DataService zurück, damit die UI
        Metadaten (z.B. für den Auswahl-Dialog) abrufen kann.
        """
        return self.data_service
