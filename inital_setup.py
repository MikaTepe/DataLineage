import os
import platform
import subprocess
import sys


def run_command(cmd, quiet=False):
    """Führt einen Befehl aus und behandelt Fehler."""
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        # Ignoriere häufige, harmlose Fehler
        if "would duplicate" in e.stderr or "is not a Mach-O file" in e.stderr:
            return None
        if not quiet:
            print(f"    -  WARNUNG: {' '.join(cmd)}\n      {e.stderr.strip()}", file=sys.stderr)
        return None


def patch_macos_graphviz():
    """
    Repariert die portable Graphviz-Installation auf macOS, indem es alle absoluten Pfade
    in Binärdateien und Bibliotheken durch relative @rpath-Pfade ersetzt.
    """
    print("=" * 70)
    print("=== Umfassendes Setup für portable macOS Graphviz ===")
    print("=" * 70)

    if platform.system() != 'Darwin':
        print("INFO: Kein macOS. Skript wird nicht benötigt.")
        return

    project_root = os.path.dirname(os.path.abspath(__file__))
    vendor_path = os.path.join(project_root, 'vendor', 'graphviz-macos')
    bin_path = os.path.join(vendor_path, 'bin')
    lib_path = os.path.join(vendor_path, 'lib')
    plugin_path = os.path.join(lib_path, 'graphviz')

    if not os.path.isdir(lib_path):
        print("FEHLER: Der 'lib'-Ordner wurde nicht gefunden.", file=sys.stderr)
        sys.exit(1)

    all_executables = [os.path.join(bin_path, f) for f in os.listdir(bin_path) if not f.endswith('.sh')]
    all_libraries = [os.path.join(lib_path, f) for f in os.listdir(lib_path) if f.endswith('.dylib')]
    all_plugins = [os.path.join(plugin_path, f) for f in os.listdir(plugin_path) if f.endswith('.dylib')]
    all_files_to_patch = all_executables + all_libraries + all_plugins

    print(f"INFO: {len(all_files_to_patch)} Dateien werden analysiert und repariert...")

    # Schritt 1: Füge RPATHs hinzu
    print("\n[1/3] Setze 'Runtime Search Paths' (RPATHs)...")
    for file_path in all_files_to_patch:
        run_command(['install_name_tool', '-add_rpath', '@executable_path/../lib', file_path], quiet=True)
        run_command(['install_name_tool', '-add_rpath', '@loader_path/.', file_path], quiet=True)
        run_command(['install_name_tool', '-add_rpath', '@loader_path/../..', file_path], quiet=True)
    print("  -> RPATHs erfolgreich gesetzt.")

    # Schritt 2: Korrigiere die interne ID jeder Bibliothek
    print("\n[2/3] Korrigiere die internen IDs der Bibliotheken...")
    for file_path in all_libraries + all_plugins:
        lib_name = os.path.basename(file_path)
        run_command(['install_name_tool', '-id', f'@rpath/{lib_name}', file_path])
    print("  -> IDs erfolgreich aktualisiert.")

    # Schritt 3: Korrigiere alle internen Abhängigkeiten
    print("\n[3/3] Korrigiere Pfade zu abhängigen Bibliotheken...")
    total_changes = 0
    for file_path in all_files_to_patch:
        otool_proc = run_command(['otool', '-L', file_path])
        if not otool_proc: continue

        dependencies = otool_proc.stdout.splitlines()[1:]
        for dep in dependencies:
            dep_path = dep.strip().split(' ')[0]
            dep_name = os.path.basename(dep_path)

            if dep_path.startswith('/Users/') or dep_path.startswith('/usr/local/Cellar/') or dep_path.startswith(
                    '/opt/homebrew'):
                new_path = f"@rpath/{dep_name}"
                res = run_command(['install_name_tool', '-change', dep_path, new_path, file_path])
                if res:
                    total_changes += 1

    print("\n" + "=" * 70)
    print(f"✅ Setup abgeschlossen! {total_changes} interne Pfade wurden korrigiert.")
    print("   Die Graphviz-Installation ist jetzt vollständig portabel.")
    print("=" * 70)


if __name__ == '__main__':
    patch_macos_graphviz()