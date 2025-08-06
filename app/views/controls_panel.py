from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QHBoxLayout, QLineEdit
from app.views.artifact_selection_dialog import ArtifactSelectionDialog
from app.services.data_service import DataService


class ControlsPanel(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.data_service = DataService()

        self.setFixedWidth(350)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- Graph-Auswahl ---
        selection_label = QLabel("Graph-Steuerung:")
        selection_label.setStyleSheet("font-weight: bold;")
        self.select_artifact_button = QPushButton("Artefakt analysieren...")
        main_layout.addWidget(selection_label)
        main_layout.addWidget(self.select_artifact_button)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line1)

        # --- Suchfunktion UI ---
        search_label = QLabel("Knoten suchen:")
        search_label.setStyleSheet("font-weight: bold; padding-top: 10px;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Namensteil eingeben...")
        self.search_button = QPushButton("Suchen")

        main_layout.addWidget(search_label)
        main_layout.addWidget(self.search_input)
        main_layout.addWidget(self.search_button)

        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line2)

        # --- Legende ---
        legend_title = QLabel("Legende")
        legend_title.setStyleSheet("font-weight: bold; padding-top: 10px;")
        main_layout.addWidget(legend_title)

        legend_items = [
            ("ELT", "#FAD7A0"),
            ("View", "#A9DFBF"),
            ("Table", "#AED6F1"),
            ("Script", "#F5B041"),
            ("CTE", "#F5B7B1"),
            ("Undefined", "#D5DBDB")
        ]

        for label, color in legend_items:
            row = QHBoxLayout()
            box = QLabel()
            box.setFixedSize(20, 20)
            box.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
            text = QLabel(label)
            row.addWidget(box)
            row.addWidget(text)
            row.addStretch()
            main_layout.addLayout(row)

        main_layout.addStretch()

        # --- Verbindungen ---
        self.select_artifact_button.clicked.connect(self.open_artifact_dialog)
        self.search_button.clicked.connect(self.search_node)
        # Verbinde die Enter-Taste im Suchfeld mit der Suchfunktion
        self.search_input.returnPressed.connect(self.search_node)

        self.main_window.tab_widget.currentChanged.connect(self.connect_highlighting_clear_signal)
        self.connect_highlighting_clear_signal()

    def open_artifact_dialog(self):
        dialog = ArtifactSelectionDialog(data_service=self.data_service, parent=self)
        if dialog.exec_():
            selections = dialog.getSelections()
            if selections:
                self.main_window.add_new_tab(selections)

    def search_node(self):
        """Holt den Suchbegriff und startet die Suche im aktuellen Tab."""
        search_term = self.search_input.text()
        current_tab = self.main_window.tab_widget.currentWidget()
        if hasattr(current_tab, 'controller'):
            current_tab.controller.search_and_highlight_node(search_term)

    def connect_highlighting_clear_signal(self):
        """Verbindet das Signal des aktuellen Canvas mit dem Leeren des Suchfeldes."""
        current_tab = self.main_window.tab_widget.currentWidget()
        if hasattr(current_tab, 'canvas'):
            try:
                current_tab.canvas.highlighting_cleared.disconnect(self.search_input.clear)
            except TypeError:
                pass

            current_tab.canvas.highlighting_cleared.connect(self.search_input.clear)