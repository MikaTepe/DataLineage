# app/views/main_window.py
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

        # Initial einen Willkommens-Tab hinzufügen
        welcome_tab = QWidget()
        self.tab_widget.addTab(welcome_tab, "Willkommen")

    def add_new_tab(self, selections: dict):
        """Erstellt einen neuen Tab basierend auf den Dialog-Auswahlen."""
        artifact_name = selections['artifact']

        if selections['new_tab'] is False:
            # Finde offenen Tab und ersetze ihn
            current_tab = self.tab_widget.currentWidget()
            if isinstance(current_tab, GraphTab):
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), artifact_name)
                current_tab.controller.load_graph_for_selection(selections)
                return

        # Ansonsten neuen Tab erstellen
        graph_view_tab = GraphTab()
        index = self.tab_widget.addTab(graph_view_tab, artifact_name)
        self.tab_widget.setCurrentIndex(index)
        graph_view_tab.controller.load_graph_for_selection(selections)

    def close_tab(self, index: int):
        """Schließt den Tab am angegebenen Index."""
        if self.tab_widget.tabText(index) == "Willkommen" and self.tab_widget.count() == 1:
            return

        widget_to_remove = self.tab_widget.widget(index)
        self.tab_widget.removeTab(index)
        widget_to_remove.deleteLater()