import networkx as nx
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem
from PyQt5.QtGui import QPen, QFont, QPainter, QColor
from PyQt5.QtCore import Qt, QTimer, pyqtSignal

from app.models.node_types import ELTNode, TableNode, ViewNode, ScriptNode, CTENode, UndefinedNode, GraphNodeMixin
from app.views.dialogs import InfoDialog
from app.models.node import Node


class EdgeLine(QGraphicsLineItem):
    """Eine Kante, die sich automatisch an die Bewegung der Knoten anpasst."""

    def __init__(self, source_node, dest_node, parent=None):
        super().__init__(parent)
        self.source, self.dest = source_node, dest_node
        self.setPen(QPen(Qt.darkGray, 1.5))
        self.setZValue(-1)

    def paint(self, painter, option, widget=None):
        """Zeichnet die Linie zwischen den Mittelpunkten der verbundenen Knoten."""
        p1 = self.source.scenePos() + self.source.boundingRect().center()
        p2 = self.dest.scenePos() + self.dest.boundingRect().center()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())
        super().paint(painter, option, widget)


class GraphCanvas(QGraphicsView):
    """
    Die Zeichenfläche mit Standard-Panning und der Zoom-Logik.
    """
    node_double_clicked = pyqtSignal(object)
    BASE_FONT_SIZE, MIN_FONT_SIZE, MAX_FONT_SIZE = 12, 4, 30

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)

        self.node_items = {}
        self._initial_scale = 1.0  # Initialwert für die Skalierung
        self.node_double_clicked.connect(self.show_info_dialog)

    def clear_scene(self):
        self.scene.clear()
        self.node_items = {}

    def show_error_message(self, message: str):
        self.clear_scene()
        self.scene.addText(message, QFont("Arial", 12)).setDefaultTextColor(Qt.red)

    def draw_graph(self, G: nx.DiGraph, pos: dict):
        self.clear_scene()
        if not pos:
            self.show_error_message("Layout-Berechnung fehlgeschlagen.")
            return

        for node_id, attrs in G.nodes(data=True):
            node_obj = attrs.get('data')
            if node_obj:
                x, y = pos.get(node_id, (0, 0))
                node_item = self.create_node_item(node_obj, x, -y, self.BASE_FONT_SIZE)
                self.scene.addItem(node_item)
                self.node_items[node_id] = node_item

        for source, target in G.edges():
            s_item, t_item = self.node_items.get(source), self.node_items.get(target)
            if s_item and t_item:
                self.scene.addItem(EdgeLine(s_item, t_item))

        QTimer.singleShot(0, self.fit_view)

    def create_node_item(self, node_obj: Node, x, y, font_size):
        node_type = node_obj.node_type.upper()
        node_class_map = {
            "ELT": ELTNode, "TABLE": TableNode, "VIEW": ViewNode,
            "SCRIPT": ScriptNode, "CTE": CTENode,
        }
        NodeClass = node_class_map.get(node_type, UndefinedNode)
        return NodeClass(node_obj.id, node_obj.name, x, y, font_size)

    def fit_view(self):
        """Passt die Ansicht an den Inhalt an und speichert die ideale Skalierung."""
        if not self.scene.items():
            return

        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.scale(0.95, 0.95)  # Ein kleiner Rand ist angenehmer

        # Speichere die "perfekte" Skalierung als Referenz für die Zoom-Begrenzung.
        self._initial_scale = self.transform().m11()

        self._update_node_fonts()

    def _update_node_fonts(self):
        """Passt die Schriftgröße aller Knoten an die aktuelle Zoom-Stufe an."""
        if not self.scene.items(): return
        scale = self.transform().m11()
        font_size = self.BASE_FONT_SIZE / scale
        clamped_font_size = max(self.MIN_FONT_SIZE, min(font_size, self.MAX_FONT_SIZE))
        for node in self.node_items.values():
            if hasattr(node, 'set_font_size'):
                node.set_font_size(int(clamped_font_size))

    def resizeEvent(self, event):
        """Wird aufgerufen, wenn die Fenstergröße geändert wird."""
        super().resizeEvent(event)
        self.fit_view()

    def wheelEvent(self, event):
        """
        Ermöglicht freies herein- und herauszoomen mit sanften Faktoren.
        """
        angle = event.angleDelta().y()
        if angle == 0:
            return

        factor = 1.1 if angle > 0 else 1 / 1.1
        current_scale = self.transform().m11()
        new_scale = current_scale * factor

        # Definiere die untere und obere Zoom-Grenze basierend auf der initialen Skalierung.
        min_allowed_scale = self._initial_scale / 4.0  # Maximal 4x kleiner als der Graph
        max_allowed_scale = self._initial_scale * 10.0  # Maximal 10x größer zoomen

        # Wende die Begrenzungen an
        if new_scale < min_allowed_scale:
            factor = min_allowed_scale / current_scale
        elif new_scale > max_allowed_scale:
            factor = max_allowed_scale / current_scale

        self.scale(factor, factor)
        self._update_node_fonts()

    def mouseDoubleClickEvent(self, event):
        """Behandelt den Doppelklick auf einen Knoten."""
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsTextItem):
            item = item.parentItem()

        if isinstance(item, GraphNodeMixin):
            self.node_double_clicked.emit(item.get_node_id())
        else:
            super().mouseDoubleClickEvent(event)

    def show_info_dialog(self, node_id: str):
        """Öffnet den Info-Dialog mit den Daten aus dem Node-Objekt."""
        node_attrs = self.model.graph.nodes.get(node_id)
        if not node_attrs or 'data' not in node_attrs: return

        node_obj: Node = node_attrs['data']
        info = {
            "Name": node_obj.name,
            "ID": node_obj.id,
            "Typ": node_obj.node_type,
            "Kontext": node_obj.context,
            "Besitzer": node_obj.owner,
            "Beschreibung": node_obj.description,
            "Vorgänger": node_obj.predecessors if node_obj.predecessors else "Keine",
            "Nachfolger": node_obj.successors if node_obj.successors else "Keine",
        }
        dialog = InfoDialog(info, self)
        dialog.exec_()