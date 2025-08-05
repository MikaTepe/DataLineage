from PyQt5.QtWidgets import (
    QDialog, QComboBox, QFormLayout, QDialogButtonBox,
    QVBoxLayout, QMessageBox, QCompleter, QCheckBox
)
from PyQt5.QtCore import Qt


class ArtifactSelectionDialog(QDialog):
    def __init__(self, cache_data, db_connections, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Artefakt-Analyse konfigurieren")
        self.setMinimumSize(500, 200)

        self.cache_data = cache_data or {}
        self.db_connections = db_connections or {}

        # UI-Elemente
        self.data_source_combo = QComboBox()
        self.artifact_type_combo = QComboBox()
        self.schema_combo = QComboBox()
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
        form_layout.addRow("Datenquelle:", self.data_source_combo)
        form_layout.addRow("Artefaktart:", self.artifact_type_combo)
        form_layout.addRow("Schema:", self.schema_combo)
        form_layout.addRow("Artefakt:", self.artifact_combo)
        form_layout.addRow("Optionen:", self.cte_checkbox)
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        # Verbindungen
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)
        self.new_tab_button.clicked.connect(self.new_tab_clicked)
        self.data_source_combo.currentIndexChanged.connect(self.update_schemas)
        self.artifact_type_combo.currentIndexChanged.connect(self.update_schemas)
        self.schema_combo.currentIndexChanged.connect(self.update_artifacts)

        # Initialisierung
        self.populate_initial_data()

    def populate_initial_data(self):
        self.data_source_combo.addItems(self.cache_data.keys())
        self.artifact_type_combo.addItems(["ELT", "Tabellen", "Views"])
        self.update_schemas()

    def update_schemas(self):
        data_source = self.data_source_combo.currentText()
        if not data_source or data_source not in self.cache_data:
            return

        all_schemas = list(self.cache_data[data_source].keys())
        self.schema_combo.clear()
        self.schema_combo.addItems(sorted(all_schemas))
        self.update_artifacts()

    def update_artifacts(self):
        data_source = self.data_source_combo.currentText()
        schema = self.schema_combo.currentText()
        artifact_type = self.artifact_type_combo.currentText()

        self.artifact_combo.clear()
        items = []

        if not all([data_source, schema, artifact_type]) or data_source not in self.cache_data or schema not in \
                self.cache_data[data_source]:
            return

        schema_content = self.cache_data[data_source][schema]
        if artifact_type == "ELT":
            items = sorted(schema_content.get("unique_artifacts", []))
        elif artifact_type == "Tabellen":
            items = sorted([t['table_name'] for t in schema_content.get("unique_tables", [])])
        elif artifact_type == "Views":
            items = sorted([v['view_name'] for v in schema_content.get("unique_views", [])])

        self.artifact_combo.addItems(items)
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
        return {
            "data_source": self.data_source_combo.currentText(),
            "artifact_type": self.artifact_type_combo.currentText(),
            "schema": self.schema_combo.currentText(),
            "artifact": self.artifact_combo.currentText(),
            "include_ctes": self.cte_checkbox.isChecked(),
            "new_tab": self.new_tab,
        }