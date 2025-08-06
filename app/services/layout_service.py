import networkx as nx
import os
import sys
import platform


class LayoutService:
    """
    Berechnet ein robustes, hierarchisches Layout für einen Graphen.
    Nutzt eine gebündelte, portable Version von Graphviz.
    """

    def _get_graphviz_path(self):
        """Sucht den Pfad zur portablen Graphviz-Version für das aktuelle OS."""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            # Geht drei Ebenen nach oben, um vom aktuellen Verzeichnis zum Projekt-Root zu gelangen
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        current_os = os.environ.get('OS', platform.system()).lower()
        subfolder = ""

        if "win" in current_os:
            subfolder = "graphviz-win64"
        elif "darwin" in current_os or "mac" in current_os:
            subfolder = "graphviz-macos"

        else:
            print(f"WARNUNG: Keine portable Graphviz-Version für {current_os} gebündelt.")
            return None

        vendor_path = os.path.join(base_path, 'vendor', subfolder, 'bin')

        if os.path.exists(vendor_path):
            return vendor_path

        print(f"WARNUNG: Portabler Graphviz-Pfad nicht gefunden: {vendor_path}")
        return None

    def calculate_layout(self, graph: nx.DiGraph):
        """
        Berechnet ein hierarchisches Layout von links nach rechts.
        """
        if not graph.nodes:
            print("Layout-Berechnung übersprungen: Graph hat keine Knoten.")
            return {}

        try:
            from networkx.drawing.nx_pydot import graphviz_layout

            graphviz_path = self._get_graphviz_path()
            if not graphviz_path:
                raise EnvironmentError("Kein gültiger Graphviz-Pfad gefunden.")

            original_path = os.environ.get('PATH', '')
            os.environ['PATH'] = f"{graphviz_path}{os.pathsep}{original_path}"

            print(f"INFO: Nutze portable Graphviz-Version für '{platform.system()}'")

            graph.graph['graph'] = {'rankdir': 'LR'}
            pos = graphviz_layout(graph, prog='dot')

            os.environ['PATH'] = original_path

            print("INFO: Horizontales hierarchisches Layout erfolgreich berechnet.")
            return pos
        except Exception as e:
            print(f"FEHLER: Hierarchisches Layout fehlgeschlagen: {e}")

        # Fallback: Robustes Spring-Layout
        print("WARNUNG: Nutze robustes Spring-Layout als Fallback...")
        try:
            k_value = 200 / (len(graph.nodes()) ** 0.5) if len(graph.nodes()) > 0 else 200
            pos = nx.spring_layout(graph, k=k_value, iterations=100, seed=42)
            print("INFO: Robustes Spring-Layout erfolgreich berechnet.")
            return pos
        except Exception as e:
            print(f"FATAL: Selbst das Fallback-Layout (Spring) ist fehlgeschlagen: {e}")
            return {}