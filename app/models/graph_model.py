import networkx as nx
from PyQt5.QtCore import QObject, pyqtSignal


class GraphModel(QObject):
    """Hält den Graphen und benachrichtigt Views über Änderungen."""
    model_updated = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.graph = nx.DiGraph()

    def clear(self):
        """Setzt das Modell zurück."""
        self.graph.clear()
        self.model_updated.emit()

    def load_graph(self, graph: nx.DiGraph):
        """Lädt einen vorbereiteten Graphen und benachrichtigt die Views."""
        self.graph = graph
        if not self.graph.nodes:
            self.error_occurred.emit("Der ausgewählte Graph enthält keine Knoten.")

        self.model_updated.emit()