from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QApplication
from PyQt5.QtCore import QTimer
import networkx as nx

from app.views.graph_canvas import GraphCanvas
from app.models.graph_model import GraphModel
from app.models.node_types import BaseNode
from app.services.layout_service import LayoutService


class ExportPreviewDialog(QDialog):
    """
    Ein Dialog, der eine interaktive Vorschau des Graphen anzeigt.
    Knoten können per Klick ausgeblendet/eingeblendet (gefaded) werden.
    """

    def __init__(self, graph: nx.DiGraph, pos: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vorschau und Export")
        self.setMinimumSize(800, 600)

        self.original_graph = graph
        self.original_pos = pos

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        info_label = QLabel("Klicken Sie auf Knoten, um deren Deckkraft vor dem Export zu ändern.", self)
        layout.addWidget(info_label)

        preview_model = GraphModel()
        # Die Vorschau-Canvas wird im "fade"-Modus erstellt, um Klicks für das Ausblenden zu nutzen.
        self.preview_canvas = GraphCanvas(preview_model, self, interaction_mode='fade')

        self.button_box = QDialogButtonBox()
        self.button_box.addButton("Als PNG speichern", QDialogButtonBox.AcceptRole)
        self.button_box.addButton(QDialogButtonBox.Cancel)

        layout.addWidget(self.preview_canvas)
        layout.addWidget(self.button_box)

        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.export_and_close)

        # Den Graphen erst zeichnen, wenn der Dialog vollständig initialisiert ist, um Render-Fehler zu vermeiden.
        QTimer.singleShot(0, self.initial_draw)

    def initial_draw(self):
        """Führt das erste Zeichnen auf der Canvas aus."""
        self.preview_canvas.draw_graph(self.original_graph, self.original_pos)

    def toggle_node_faded_state(self, node_id: str):
        """Ändert den 'faded'-Zustand eines Knotens und seiner Kanten."""
        node_item = self.preview_canvas.node_items.get(node_id)
        if not isinstance(node_item, BaseNode):
            return

        is_now_faded = not node_item.is_faded
        node_item.set_faded(is_now_faded)

        for edge in self.preview_canvas.edge_items:
            source_id = edge.source.get_node_id()
            dest_id = edge.dest.get_node_id()
            # Eine Kante wird gefaded, wenn einer der verbundenen Knoten gefaded ist.
            source_is_faded = self.preview_canvas.node_items[source_id].is_faded
            dest_is_faded = self.preview_canvas.node_items[dest_id].is_faded
            edge.set_faded(source_is_faded or dest_is_faded)

    def export_and_close(self):
        """Erstellt einen neuen Graphen basierend auf der Sichtbarkeit und exportiert diesen."""

        visible_nodes_ids = {nid for nid, node in self.preview_canvas.node_items.items() if not node.is_faded}

        if not visible_nodes_ids:
            print("Export abgebrochen: Keine sichtbaren Knoten zum Exportieren.")
            self.accept()
            return

        # Erstelle einen neuen Graphen nur mit den sichtbaren Knoten.
        export_graph = self.original_graph.subgraph(visible_nodes_ids).copy()

        # Füge die überbrückten Kanten hinzu.
        edges_to_add = set()
        for u in visible_nodes_ids:
            queue = list(self.original_graph.successors(u))
            visited = set(queue)
            while queue:
                v = queue.pop(0)
                if v in visible_nodes_ids:
                    if not export_graph.has_edge(u, v):
                        edges_to_add.add((u, v))
                    continue
                for w in self.original_graph.successors(v):
                    if w not in visited:
                        visited.add(w)
                        queue.append(w)

        export_graph.add_edges_from(list(edges_to_add))

        # Berechne ein frisches Layout für den neuen Graphen.
        layout_service = LayoutService()
        export_pos = layout_service.calculate_layout(export_graph)

        if not export_pos:
            print("Export fehlgeschlagen: Layout für den modifizierten Graphen konnte nicht berechnet werden.")
            self.accept()
            return

        # Erstelle eine temporäre Canvas nur für den Export.
        temp_model = GraphModel()
        temp_canvas = GraphCanvas(temp_model)

        # Zeichne den Graphen auf die temporäre Leinwand.
        temp_canvas.draw_graph(export_graph, export_pos)

        # Erzwinge die explizite Berechnung der Kanten-Geometrie.
        temp_canvas.update_all_edge_positions()

        # Verarbeite alle ausstehenden Events, um die Szene zu aktualisieren.
        QApplication.processEvents()

        info = f"Exportierter Graph | Knoten: {len(export_graph.nodes())}, Kanten: {len(export_graph.edges())}"

        # Führe den Export aus.
        temp_canvas.export_to_png(info_text=info)

        self.accept()