from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor, QPen, QFont
from PyQt5.QtCore import Qt


class GraphNodeMixin:
    """Mixin-Klasse, um die Knoten-ID zu speichern."""

    def __init__(self, node_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._node_id = node_id

    def get_node_id(self):
        return self._node_id


class BaseNode(GraphNodeMixin, QGraphicsRectItem):
    """
    Eine Basisklasse für Knoten mit dynamischer Größe basierend auf dem Inhalt.
    """
    def __init__(self, node_id, label, x, y, color, font_size=12):
        # Initial wird das Rechteck ohne Größe erstellt, die wird sofort angepasst
        super().__init__(node_id, 0, 0, 0, 0)

        self.setPos(x, y)
        self.setPen(QPen(Qt.black, 1))
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)

        # Zustand und Farbe VOR der ersten Verwendung initialisieren
        self.is_faded = False
        self.original_brush = QBrush(color)
        self.setBrush(self.original_brush)

        # Text-Item erstellen und Schriftart setzen
        self.text = QGraphicsTextItem(label, self)
        self.text.setDefaultTextColor(Qt.black)

        # Jetzt die Größe anpassen
        self.set_font_size(font_size)

    def set_faded(self, faded: bool):
        """Setzt den Knoten auf verblasst oder normal."""
        self.is_faded = faded
        opacity = 0.3 if faded else 1.0

        self.setOpacity(opacity)
        self.text.setOpacity(opacity)

    def set_font_size(self, font_size):
        """Aktualisiert die Schriftgröße und passt die Größe des Knotens an."""
        font = QFont("Arial", font_size)
        self.text.setFont(font)

        # Rechteckgröße basierend auf Textgröße neu berechnen
        text_rect = self.text.boundingRect()
        rect_width = text_rect.width() + 20
        rect_height = text_rect.height() + 10

        # Setzt die neue Rechteckgröße und zentriert den Knoten um seinen Ankerpunkt (0,0)
        self.setRect(-rect_width / 2, -rect_height / 2, rect_width, rect_height)

        # Zentriert den Text im neuen Rechteck
        self.text.setPos(-text_rect.width() / 2, -text_rect.height() / 2)


# Spezifische Knotentypen
class ELTNode(BaseNode):
    def __init__(self, node_id, label, x, y, font_size):
        super().__init__(node_id, label, x, y, QColor("#FAD7A0"), font_size)


class TableNode(BaseNode):
    def __init__(self, node_id, label, x, y, font_size):
        super().__init__(node_id, label, x, y, QColor("#AED6F1"), font_size)


class ViewNode(BaseNode):
    def __init__(self, node_id, label, x, y, font_size):
        super().__init__(node_id, label, x, y, QColor("#A9DFBF"), font_size)


class ScriptNode(BaseNode):
    def __init__(self, node_id, label, x, y, font_size):
        super().__init__(node_id, label, x, y, QColor("#F5B041"), font_size)


class CTENode(BaseNode):
    def __init__(self, node_id, label, x, y, font_size):
        super().__init__(node_id, label, x, y, QColor("#F5B7B1"), font_size)


class UndefinedNode(BaseNode):
    def __init__(self, node_id, label, x, y, font_size):
        super().__init__(node_id, label, x, y, QColor("#D5DBDB"), font_size)