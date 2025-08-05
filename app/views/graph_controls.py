import tkinter as tk
from tkinter import ttk


class GraphControls(ttk.Frame):
    """Die Steuerelemente für den Graphen. Rufen nur noch Methoden am Controller auf."""

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Wir speichern eine Referenz auf das Hauptfenster, nicht nur den direkten Parent
        self.main_window = self.winfo_toplevel()

        # GUI Elemente
        label = ttk.Label(self, text="Artefakt auswählen:")
        label.pack(side="left", padx=(0, 10))

        self.artifact_var = tk.StringVar()
        self.artifact_combo = ttk.Combobox(
            self,
            textvariable=self.artifact_var,
            state="readonly",
            width=40
        )
        self.artifact_combo.pack(side="left", fill="x", expand=True)
        self.artifact_combo.bind("<<ComboboxSelected>>", self.on_artifact_select)

        load_button = ttk.Button(self, text="Graph laden", command=self.on_load_button_click)
        load_button.pack(side="left", padx=10)

        refresh_button = ttk.Button(self, text="Liste aktualisieren", command=self.refresh_artifacts_list)
        refresh_button.pack(side="left", padx=5)

        # Initial die Liste der Artefakte laden
        self.refresh_artifacts_list()

    def refresh_artifacts_list(self):
        """Holt die Artefaktliste vom Controller und füllt das Dropdown."""
        artifacts = self.controller.get_artifacts()
        self.artifact_combo['values'] = artifacts
        if artifacts and not self.artifact_var.get():
            self.artifact_var.set(artifacts[0])

    def on_load_button_click(self):
        """Wird aufgerufen, wenn der "Laden"-Button geklickt wird."""
        artifact_id = self.artifact_var.get()
        # Übergibt das Hauptfenster an den Controller, damit dieser den Lade-Indikator
        # korrekt zentrieren und steuern kann.
        self.controller.load_graph_for_artifact(artifact_id, self.main_window)

    def on_artifact_select(self, event):
        """Wird aufgerufen, wenn ein Artefakt im Dropdown ausgewählt wird. Lädt den Graph direkt."""
        self.on_load_button_click()