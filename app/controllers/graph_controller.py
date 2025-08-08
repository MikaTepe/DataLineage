# app/controllers/graph_controller.py
from PyQt5.QtCore import QObject
from app.services.data_service import DataService
from app.models.graph_model import GraphModel
from app.services.graph_analysis_service import GraphAnalysisService

class GraphController(QObject):
    """
    Steuert den Datenfluss zwischen der UI und dem DataService.
    Leitet Anfragen zur Graphenerzeugung und für Metadaten weiter.
    """
    def __init__(self, model: GraphModel, canvas, mock_mode=True, connection=None):
        super().__init__()
        self.model = model
        self.canvas = canvas
        # mock_mode=True -> nutzt MockDatabase, False -> echter Data-Lineage-Algorithmus
        self.data_service = DataService(mock_mode=mock_mode, connection=connection)

    def load_graph(self, selections: dict):
        """Fordert einen Graphen vom DataService an und lädt ihn ins Model."""
        if not selections or not selections.get('artifact'):
            self.model.clear()
            return

        graph_obj = self.data_service.get_graph_for_artifact(selections)
        self.model.load_graph(graph_obj)

    def get_data_service(self) -> DataService:
        """Gibt den DataService für UI-Datenabfragen zurück."""
        return self.data_service

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

        # Erstellt eine Instanz des Analyse-Service mit dem aktuellen Graphen
        analysis_service = GraphAnalysisService(self.model.graph)
        self.canvas.highlight_nodes(list(analysis_service.get_all_predecessors(node_id)))

    def clear_node_highlighting(self):
        """Entfernt alle Hervorhebungen."""
        self.canvas.clear_highlighting()
