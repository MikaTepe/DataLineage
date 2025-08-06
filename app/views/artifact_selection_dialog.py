from PyQt5.QtWidgets import (
    QDialog, QComboBox, QFormLayout, QDialogButtonBox,
    QVBoxLayout, QMessageBox, QCompleter, QCheckBox, QLabel
)
from PyQt5.QtCore import Qt


class ArtifactSelectionDialog(QDialog):
    def __init__(self, data_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Artefakt-Analyse konfigurieren")
        self.setMinimumSize(500, 250)

        # Der Dialog erhält eine direkte Referenz auf den DataService
        self.data_service = data_service

        # UI-Elemente
        self.data_source_combo = QComboBox()
        self.schema_combo = QComboBox()
        self.artifact_type_combo = QComboBox()
        self.artifact_combo = QComboBox()
        self.artifact_combo.setEditable(True)
        self.artifact_combo.setInsertPolicy(QComboBox.NoInsert)
        self.cte_checkbox = QCheckBox("CTEs mitgenerieren")
        self.cte_checkbox.setChecked(True)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.new_tab_button = self.button_box.addButton("In neuem Tab", QDialogButtonBox.ActionRole)
        self.new_tab = False

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("1. Datenquelle:"), self.data_source_combo)
        form_layout.addRow(QLabel("2. Schema:"), self.schema_combo)
        form_layout.addRow(QLabel("3. Artefakt-Typ:"), self.artifact_type_combo)
        form_layout.addRow(QLabel("4. Artefakt:"), self.artifact_combo)
        form_layout.addRow(QLabel("Optionen:"), self.cte_checkbox)
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        # Verbindungen
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        self.new_tab_button.clicked.connect(self.new_tab_clicked)

        # Kaskadierende Logik: Jede Änderung löst die nächste Aktualisierung aus
        self.data_source_combo.currentIndexChanged.connect(self.update_schemas)
        self.schema_combo.currentIndexChanged.connect(self.update_artifact_types)
        self.artifact_type_combo.currentIndexChanged.connect(self.update_artifacts)

        # Initialisierung
        self.populate_data_sources()

    def populate_data_sources(self):
        """Füllt die Datenquellen-Combobox mit allen verfügbaren Quellen."""
        # Korrekter Methodenaufruf am DataService
        all_sources = self.data_service.get_available_data_sources()
        self.data_source_combo.addItems(sorted(all_sources))
        # Die erste Aktualisierung wird durch das Setzen des Index ausgelöst

    def update_schemas(self):
        """Aktualisiert die Schema-Liste basierend auf der ausgewählten Datenquelle."""
        data_source = self.data_source_combo.currentText()
        self.schema_combo.clear()
        if data_source:
            schemas = self.data_service.get_schemas_for_data_source(data_source)
            self.schema_combo.addItems(schemas)

    def update_artifact_types(self):
        """Füllt die Artefakt-Typen. Diese sind für alle Quellen gleich."""
        self.artifact_type_combo.clear()
        # Für alle Quellen die gleichen Typen anbieten
        self.artifact_type_combo.addItems(["TABLE", "VIEW", "ELT"])

    def update_artifacts(self):
        """Aktualisiert die Artefakt-Liste basierend auf Schema und Typ."""
        data_source = self.data_source_combo.currentText()
        schema = self.schema_combo.currentText()
        artifact_type = self.artifact_type_combo.currentText()

        self.artifact_combo.clear()
        if not all([data_source, schema, artifact_type]):
            return

        # Korrekter Methodenaufruf
        items = self.data_service.get_artifacts_for_schema(data_source, schema, artifact_type)
        self.artifact_combo.addItems(items)

        # Autocompleter für einfache Suche
        completer = QCompleter(items, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.artifact_combo.setCompleter(completer)

    def new_tab_clicked(self):
        self.new_tab = True
        self.accept()

    def validate_and_accept(self):
        if not self.artifact_combo.currentText():
            QMessageBox.warning(self, "Ungültige Auswahl", "Bitte wählen Sie ein Artefakt aus.")
            return
        self.accept()

    def getSelections(self):
        """Gibt die finale Auswahl in einer einheitlichen Struktur zurück."""
        return {
            "data_source": self.data_source_combo.currentText(),
            "schema": self.schema_combo.currentText(),
            "artifact_type": self.artifact_type_combo.currentText(),
            "artifact": self.artifact_combo.currentText(),
            "include_ctes": self.cte_checkbox.isChecked(),
            "new_tab": self.new_tab,
        }