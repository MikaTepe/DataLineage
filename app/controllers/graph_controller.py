from PyQt5.QtCore import QObject
from app.services.data_service import DataService
from app.models.graph_model import GraphModel


class GraphController(QObject):
    """Steuert den Datenfluss zwischen DataService und GraphModel."""

    def __init__(self, model: GraphModel):
        super().__init__()
        self.model = model
        self.data_service = DataService()

    def get_artifacts(self):
        """Holt die Liste der verfügbaren Artefakte vom DataService."""
        return self.data_service.get_available_artifacts()

    def load_graph_for_artifact(self, artifact_id: str):
        """Fordert einen Graphen vom DataService an und lädt ihn ins Model."""
        if not artifact_id:
            self.model.clear()
            return

        graph_obj = self.data_service.build_graph_for_artifact(artifact_id)
        self.model.load_graph(graph_obj)

    def load_graph_for_selection(self, selections: dict):
        """Fordert einen Graphen basierend auf den Dialog-Auswahlen an."""
        if not selections.get('artifact'):
            self.model.clear()
            return

        graph_obj = self.data_service.build_graph_for_selection(selections)
        self.model.load_graph(graph_obj)