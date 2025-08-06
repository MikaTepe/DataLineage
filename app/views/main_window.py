from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter, QTabWidget
from PyQt5.QtCore import Qt

from app.views.controls_panel import ControlsPanel
from app.views.graph_tab import GraphTab


class MainWindow(QMainWindow):
    """
    Das Hauptfenster, das dem Kontroll-Panel erlaubt, neue Tabs zu erstellen.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Lineage Visualizer")
        self.setGeometry(100, 100, 1800, 1200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Das Panel bekommt wieder eine Referenz zum MainWindow
        self.controls = ControlsPanel(self)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tab_widget)
        splitter.addWidget(self.controls)
        splitter.setSizes([1400, 400])
        splitter.setCollapsible(0, False)
        main_layout.addWidget(splitter)

        # Initial einen Willkommens-Tab hinzufügen.
        # Ein GraphTab wird als Platzhalter verwendet, damit der Controller existiert.
        # Alternativ könnte man einen reinen Info-Screen erstellen.
        initial_tab = GraphTab()
        self.tab_widget.addTab(initial_tab, "Willkommen")


    def add_new_tab(self, selections: dict):
        """Erstellt einen neuen Tab und nutzt die vereinheitlichte Lade-Methode."""
        artifact_name = selections['artifact']

        # Prüfen, ob der aktuelle Tab der "Willkommen"-Tab ist.
        # Wenn ja, wird dieser wiederverwendet, anstatt einen neuen zu erstellen.
        current_widget = self.tab_widget.currentWidget()
        if self.tab_widget.tabText(self.tab_widget.currentIndex()) == "Willkommen" and isinstance(current_widget, GraphTab):
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), artifact_name)
            current_widget.controller.load_graph(selections)
            return

        # Wenn ein neuer Tab explizit gewünscht wird oder kein Willkommen-Tab aktiv ist
        if selections.get('new_tab', False):
            graph_view_tab = GraphTab()
            index = self.tab_widget.addTab(graph_view_tab, artifact_name)
            self.tab_widget.setCurrentIndex(index)
            graph_view_tab.controller.load_graph(selections)
            return

        # Ansonsten den aktuellen Tab wiederverwenden
        active_tab = self.tab_widget.currentWidget()
        if isinstance(active_tab, GraphTab):
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), artifact_name)
            active_tab.controller.load_graph(selections)
        else:
            # Fallback: Wenn der aktive Tab kein Graph-Tab ist, neuen erstellen
            graph_view_tab = GraphTab()
            index = self.tab_widget.addTab(graph_view_tab, artifact_name)
            self.tab_widget.setCurrentIndex(index)
            graph_view_tab.controller.load_graph(selections)


    def close_tab(self, index: int):
        """Schließt den Tab am angegebenen Index."""
        # Verhindert das Schließen des letzten Tabs
        if self.tab_widget.count() == 1:
            return

        widget_to_remove = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        widget_to_remove.deleteLater()