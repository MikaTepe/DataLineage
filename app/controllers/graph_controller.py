from PyQt5.QtCore import QObject
from app.services.data_service import DataService
from app.models.graph_model import GraphModel

class GraphController(QObject):
    """
    Steuert den Datenfluss zwischen der UI und dem DataService.
    Leitet Anfragen zur Graphenerzeugung und für Metadaten weiter.
    """
    def __init__(self, model: GraphModel, canvas):
        super().__init__()
        self.model = model
        self.canvas = canvas
        self.data_service = DataService()

    def load_graph(self, selections: dict):
        """
        Fordert einen Graphen über den zentralen Endpunkt im DataService an
        und lädt das Ergebnis in das GraphModel.
        """
        if not selections or not selections.get('artifact'):
            self.model.clear()
            return

        graph_obj = self.data_service.get_graph_for_artifact(selections)
        self.model.load_graph(graph_obj)

    def get_data_service(self) -> DataService:
        """
        Gibt eine Referenz auf den DataService zurück, damit die UI
        Metadaten (z.B. für den Auswahl-Dialog) abrufen kann.
        """
        return self.data_service

    def search_and_highlight_node(self, search_term: str):
        """
        Sucht den ersten passenden Knoten, hebt ihn hervor und zoomt darauf.
        """
        if not search_term:
            self.canvas.clear_highlighting()
            return

        found_node_id = None
        for node_id, attrs in self.model.graph.nodes(data=True):
            node_obj = attrs.get('data')
            if node_obj and search_term.lower() in node_obj.name.lower():
                found_node_id = node_id
                break

        if found_node_id:
            self.canvas.highlight_node(found_node_id)
            self.canvas.zoom_to_node(found_node_id)
        else:
            self.canvas.clear_highlighting()

    def clear_node_highlighting(self):
        """Beauftragt den Canvas, nur die Hervorhebungen zu entfernen."""
        self.canvas.clear_highlighting()