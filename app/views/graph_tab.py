from PyQt5.QtWidgets import QWidget, QVBoxLayout

from app.models.graph_model import GraphModel
from app.controllers.graph_controller import GraphController
from app.views.graph_canvas import GraphCanvas
from app.services.layout_service import LayoutService


class GraphTab(QWidget):
    """
    Ein eigenständiges Widget, das einen einzelnen Graphen darstellt.
    Es enthält sein eigenes MVC-Setup.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Jeder Tab besitzt eigene Komponenten
        self.model = GraphModel()
        self.layout_service = LayoutService()
        self.canvas = GraphCanvas(self.model)
        # Der Controller benötigt eine Referenz auf den Canvas, um die Hervorhebung zu steuern
        self.controller = GraphController(self.model, self.canvas)

        # Layout für den Tab
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        # Verbindungen innerhalb des Tabs
        self.model.model_updated.connect(self.draw_graph)
        self.model.error_occurred.connect(self.canvas.show_error_message)

    def draw_graph(self):
        """Zeichnet den Graphen für diesen spezifischen Tab."""
        if not self.model.graph.nodes:
            self.canvas.clear_scene()
            return

        pos = self.layout_service.calculate_layout(self.model.graph)
        self.canvas.draw_graph(self.model.graph, pos)