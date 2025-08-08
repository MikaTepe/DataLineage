# Diese Datei ist die Build-Konfiguration für PyInstaller.
# Sie wird mit dem Befehl `pyinstaller build.spec` ausgeführt.

import sys
from PyInstaller.utils.hooks import collect_data_files

# Wichtige Metadaten für die Anwendung
app_name = 'Data Lineage Tool'
main_script = 'main.py'
icon_path = 'DataLineageIcon.icns' # Pfad zu Ihrer Icon-Datei

# --- Datendateien sammeln ---
# Wir fügen die Icon-Datei hinzu, damit sie im Bundle verfügbar ist.
bundled_files = [
    ('vendor', 'vendor'),
    (icon_path, '.') # Kopiert das Icon in das Hauptverzeichnis der App
]

# Manchmal findet PyInstaller nicht alle Abhängigkeiten automatisch.
hidden_imports = [
    'PyQt5.sip',
    'PyQt5.QtNetwork',
    'PyQt5.QtPrintSupport',
    'dotenv'
]


# --- Hauptkonfiguration ---

a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=bundled_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# --- Konfiguration für die ausführbare Datei ---
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Hinzufügen des Icons für die .exe-Datei (Windows)
    icon=icon_path
)

# --- Sammlung aller Dateien für den finalen Ordner ---
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)

# --- macOS-spezifische Konfiguration ---
# Erstellt ein .app-Bundle für eine saubere macOS-Integration
app = BUNDLE(
    coll,
    name=f'{app_name}.app',
    # Hinzufügen des Icons für das .app-Bundle (macOS)
    # Hinweis: Eine .icns-Datei wäre hier ideal, aber .ico funktioniert oft auch.
    icon=icon_path,
    bundle_identifier=None,
)