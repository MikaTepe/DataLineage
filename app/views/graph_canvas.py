import networkx as nx
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsLineItem, QGraphicsTextItem, QFileDialog, \
    QApplication
from PyQt5.QtGui import QPen, QFont, QPainter, QColor, QImage
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPointF, QRectF

from app.models.node_types import BaseNode, ELTNode, TableNode, ViewNode, ScriptNode, CTENode, UndefinedNode, \
    GraphNodeMixin
from app.views.dialogs import InfoDialog
from app.models.node import Node


class EdgeLine(QGraphicsLineItem):
    """Eine Kante, die sich automatisch an die Bewegung der Knoten anpasst."""
    def __init__(self, source_node, dest_node, parent=None):
        super().__init__(parent)
        self.source, self.dest = source_node, dest_node
        self.is_faded = False

        self.default_pen = QPen(Qt.darkGray, 1.5)
        self.highlight_pen = QPen(QColor("#FF007F"), 2.5, Qt.SolidLine)

        self.setPen(self.default_pen)
        self.setZValue(-1)

    def set_highlighted(self, highlighted: bool):
        self.setPen(self.highlight_pen if highlighted else self.default_pen)

    def set_faded(self, faded: bool):
        """Setzt die Kante auf verblasst oder normal."""
        self.is_faded = faded
        self.setOpacity(0.3 if faded else 1.0)

    def update_position(self):
        """Calculates and sets the line's start and end points based on node positions."""
        p1 = self.source.scenePos() + self.source.boundingRect().center()
        p2 = self.dest.scenePos() + self.dest.boundingRect().center()
        self.setLine(p1.x(), p1.y(), p2.x(), p2.y())

    def paint(self, painter, option, widget=None):
        # Sicherstellen, dass die Position vor dem Malen aktuell ist.
        self.update_position()
        super().paint(painter, option, widget)


class GraphCanvas(QGraphicsView):
    """
    Die Zeichenfläche mit Standard-Panning und der Zoom-Logik.
    """
    node_double_clicked = pyqtSignal(object)
    node_clicked = pyqtSignal(str)
    highlighting_cleared = pyqtSignal()

    BASE_FONT_SIZE = 12

    def __init__(self, model, parent=None, interaction_mode='highlight'):
        super().__init__(parent)
        self.model = model
        self.interaction_mode = interaction_mode

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRenderHint(QPainter.Antialiasing)

        self.node_items = {}
        self.edge_items = []
        self._initial_scale = 1.0
        self._mouse_press_pos = QPointF()

        self.node_double_clicked.connect(self.show_info_dialog)

    def clear_scene(self):
        self.scene.clear()
        self.node_items = {}
        self.edge_items = []

    def show_loading_message(self, message: str):
        """Zeigt eine zentrierte Lade-Nachricht auf der Canvas an."""
        self.clear_scene()
        text_item = self.scene.addText(message, QFont("Arial", 16))
        text_item.setDefaultTextColor(Qt.gray)
        # Zentrierung des Textes im sichtbaren Bereich
        view_rect = self.viewport().rect()
        scene_rect = self.mapToScene(view_rect).boundingRect()
        text_rect = text_item.boundingRect()
        center_x = scene_rect.x() + (scene_rect.width() - text_rect.width()) / 2
        center_y = scene_rect.y() + (scene_rect.height() - text_rect.height()) / 2
        text_item.setPos(center_x, center_y)

    def show_error_message(self, message: str):
        """Zeigt eine zentrierte Fehler-Nachricht an."""
        self.clear_scene()
        text_item = self.scene.addText(message, QFont("Arial", 12))
        text_item.setDefaultTextColor(Qt.red)
        # Zentrierung
        view_rect = self.viewport().rect()
        scene_rect = self.mapToScene(view_rect).boundingRect()
        text_rect = text_item.boundingRect()
        center_x = scene_rect.x() + (scene_rect.width() - text_rect.width()) / 2
        center_y = scene_rect.y() + (scene_rect.height() - text_rect.height()) / 2
        text_item.setPos(center_x, center_y)

    def draw_graph(self, G: nx.DiGraph, pos: dict):
        self.clear_scene()
        if not pos:
            self.show_error_message("Layout-Berechnung fehlgeschlagen.")
            return

        for clean_id, attrs in G.nodes(data=True):
            node_obj = attrs.get('data')
            if node_obj:
                x, y = pos.get(clean_id, (0, 0))
                node_item = self.create_node_item(node_obj, x, -y, self.BASE_FONT_SIZE)
                self.scene.addItem(node_item)
                self.node_items[clean_id] = node_item

        for source_clean_id, target_clean_id in G.edges():
            s_item = self.node_items.get(source_clean_id)
            t_item = self.node_items.get(target_clean_id)
            if s_item and t_item:
                edge = EdgeLine(s_item, t_item)
                self.scene.addItem(edge)
                self.edge_items.append(edge)

        QTimer.singleShot(0, self.fit_view)
        
    def update_all_edge_positions(self):
        """Forces an update on all edge items in the scene."""
        for edge in self.edge_items:
            edge.update_position()

    def export_to_png(self, info_text: str = ""):
        if not self.scene.items():
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Graph als PNG speichern", "graph-export.png",
                                                   "PNG-Bilder (*.png)")
        if not file_path:
            return

        rect = self.scene.itemsBoundingRect().adjusted(-20, -20, 20, 20)
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.white)

        painter = QPainter(image)
        try:
            self.scene.render(painter, target=QRectF(image.rect()), source=rect)

            if info_text:
                font = QFont("Arial", 12)
                painter.setFont(font)
                painter.setPen(Qt.black)
                text_rect = image.rect().adjusted(10, 0, 0, -10)
                painter.drawText(text_rect, Qt.AlignBottom | Qt.AlignLeft, info_text)
        finally:
            painter.end()
        image.save(file_path)

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
        if not self.scene.items(): return
        # Vor dem Anpassen sicherstellen, dass alle Kanten an der richtigen Position sind
        self.scene.update()
        self.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.scale(0.95, 0.95)
        self._initial_scale = self.transform().m11()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_view()

    def wheelEvent(self, event):
        """Ermöglicht freies Zoomen mit Grenzen."""
        angle = event.angleDelta().y()
        if angle == 0: return
        factor = 1.1 if angle > 0 else 1 / 1.1
        current_scale = self.transform().m11()
        new_scale = current_scale * factor
        min_allowed_scale = self._initial_scale / 1.5
        max_allowed_scale = self._initial_scale * 5.0
        if new_scale < min_allowed_scale:
            factor = min_allowed_scale / current_scale
        elif new_scale > max_allowed_scale:
            factor = max_allowed_scale / current_scale
        self.scale(factor, factor)

    def mouseReleaseEvent(self, event):
        if (event.pos() - self._mouse_press_pos).manhattanLength() < 3:
            item = self.itemAt(event.pos())
            if isinstance(item, QGraphicsTextItem): item = item.parentItem()

            if isinstance(item, GraphNodeMixin):
                node_id = item.get_node_id()
                # Führe die Aktion basierend auf dem Modus aus
                if self.interaction_mode == 'highlight':
                    self.node_clicked.emit(node_id)
                elif self.interaction_mode == 'fade':
                    self.toggle_node_faded_state(node_id)

            # Klick auf den Hintergrund im Highlight-Modus
            elif item is None and self.interaction_mode == 'highlight':
                self.clear_highlighting()
                self.highlighting_cleared.emit()
        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        self._mouse_press_pos = event.pos()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Behandelt den Doppelklick auf einen Knoten."""
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsTextItem): item = item.parentItem()
        if isinstance(item, GraphNodeMixin):
            self.node_double_clicked.emit(item.get_node_id())
        else:
            super().mouseDoubleClickEvent(event)

    def show_info_dialog(self, node_id: str):
        node_attrs = self.model.graph.nodes.get(node_id)
        if not node_attrs or 'data' not in node_attrs: return
        node_obj: Node = node_attrs['data']
        info = {"Name": node_obj.name, "ID": node_obj.context, "Typ": node_obj.node_type,
                "Besitzer": node_obj.owner, "Beschreibung": node_obj.description,
                "Vorgänger": node_obj.predecessors if node_obj.predecessors else "Keine",
                "Nachfolger": node_obj.successors if node_obj.successors else "Keine", }
        dialog = InfoDialog(info, self)
        dialog.exec_()

    def toggle_node_faded_state(self, node_id: str):
        """Ändert den 'faded'-Zustand eines Knotens und seiner Kanten."""
        node_item = self.node_items.get(node_id)
        if not isinstance(node_item, BaseNode):
            return

        is_now_faded = not node_item.is_faded
        node_item.set_faded(is_now_faded)

        for edge in self.edge_items:
            source_id = edge.source.get_node_id()
            dest_id = edge.dest.get_node_id()
            if source_id == node_id or dest_id == node_id:
                source_is_faded = self.node_items[source_id].is_faded
                dest_is_faded = self.node_items[dest_id].is_faded
                edge.set_faded(source_is_faded or dest_is_faded)

    def highlight_nodes(self, node_ids: list):
        self.clear_highlighting()
        highlight_pen = QPen(QColor("#FF007F"), 3, Qt.SolidLine)
        for node_id in node_ids:
            node_item = self.node_items.get(node_id)
            if node_item: node_item.setPen(highlight_pen)
        highlighted_node_set = set(node_ids)
        for edge in self.edge_items:
            source_id = edge.source.get_node_id()
            dest_id = edge.dest.get_node_id()
            if source_id in highlighted_node_set and dest_id in highlighted_node_set:
                edge.set_highlighted(True)

    def highlight_node(self, node_id: str):
        self.highlight_nodes([node_id])

    def zoom_to_node(self, node_id: str):
        """Zentriert die Ansicht und zoomt auf einen bestimmten Knoten."""
        node_item = self.node_items.get(node_id)
        if node_item:
            padding = 50
            rect = node_item.sceneBoundingRect().adjusted(-padding, -padding, padding, padding)
            self.fitInView(rect, Qt.KeepAspectRatio)

    def clear_highlighting(self):
        """Setzt die Hervorhebung aller Knoten auf den Standard zurück."""
        default_pen = QPen(Qt.black, 1)
        for node_item in self.node_items.values(): node_item.setPen(default_pen)
        for edge in self.edge_items: edge.set_highlighted(False)