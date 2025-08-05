import tkinter as tk
from tkinter import ttk

class LoadingIndicator:
    """Ein einfacher, zentrierter Lade-Indikator."""
    def __init__(self, parent):
        self.top_level = tk.Toplevel(parent)
        self.top_level.title("Laden...")
        self.top_level.transient(parent)
        self.top_level.grab_set()
        self.top_level.resizable(False, False)

        label = ttk.Label(self.top_level, text="Daten werden geladen, bitte warten...", padding=20)
        label.pack()
        progress = ttk.Progressbar(self.top_level, mode='indeterminate', length=200)
        progress.pack(pady=10, padx=20)
        progress.start()

        # Zentriere das Fenster
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.top_level.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.top_level.winfo_height()) // 2
        self.top_level.geometry(f"+{x}+{y}")

    def close(self):
        """Schließt den Lade-Indikator."""
        self.top_level.destroy()