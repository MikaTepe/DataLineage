from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QDialogButtonBox, QTextEdit


class InfoDialog(QDialog):
    """Ein Dialog zur Anzeige von Key-Value-Informationen über einen Knoten."""

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Knoten-Information")
        self.setMinimumWidth(400)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        for key, value in data.items():
            value_str = ""
            if isinstance(value, list):
                if not value:
                    value_str = "None"
                else:
                    value_str = "\n".join([f"- {item}" for item in value])
            else:
                value_str = str(value)

            if "\n" in value_str:
                text_edit = QTextEdit(value_str)
                text_edit.setReadOnly(True)

                height = int(text_edit.document().size().height() + 10)
                text_edit.setFixedHeight(min(100, height))

                form_layout.addRow(QLabel(f"<b>{key}:</b>"), text_edit)
            else:
                form_layout.addRow(QLabel(f"<b>{key}:</b>"), QLabel(value_str))

        main_layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        main_layout.addWidget(button_box)