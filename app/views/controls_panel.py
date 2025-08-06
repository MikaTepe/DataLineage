from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame, QHBoxLayout
from app.views.artifact_selection_dialog import ArtifactSelectionDialog
from app.services.data_service import DataService


class ControlsPanel(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        # Das ControlsPanel erhält seine eigene Instanz des DataService.
        # Dies entkoppelt es von den Tabs und verhindert den Absturz.
        self.data_service = DataService()

        self.setFixedWidth(350)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        selection_label = QLabel("Graph-Steuerung:")
        selection_label.setStyleSheet("font-weight: bold;")
        self.select_artifact_button = QPushButton("Artefakt analysieren...")
        main_layout.addWidget(selection_label)
        main_layout.addWidget(self.select_artifact_button)

        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line1)

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

        self.select_artifact_button.clicked.connect(self.open_artifact_dialog)

    def open_artifact_dialog(self):
        """Öffnet den Dialog und übergibt die eigene DataService-Instanz."""
        dialog = ArtifactSelectionDialog(
            data_service=self.data_service,
            parent=self
        )
        if dialog.exec_():
            selections = dialog.getSelections()
            if selections:
                self.main_window.add_new_tab(selections)