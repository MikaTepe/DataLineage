import networkx as nx
import os
import sys
import platform
import logging

logger = logging.getLogger(__name__)


class LayoutService:
    """
    Berechnet ein hierarchisches Layout für einen Graphen.
    Nutzt eine gebündelte, portable und vorab gepatchte Version von Graphviz.
    """

    def _get_graphviz_path(self):
        """
        Findet den Pfad zum 'bin'-Verzeichnis von Graphviz.
        Funktioniert in der Entwicklung und in der gebauten App.
        """
        try:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Modus: Gebaute PyInstaller-Anwendung
                base_path = sys._MEIPASS
            else:
                # Modus: Entwicklungsumgebung
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            current_os = platform.system().lower()
            subfolder = "graphviz-macos" if "darwin" in current_os else "graphviz-win64" if "windows" in current_os else None

            if not subfolder:
                logger.warning(f"Keine portable Graphviz-Version für OS '{current_os}' gebündelt.")
                return None

            bin_path = os.path.join(base_path, 'vendor', subfolder, 'bin')

            if not os.path.exists(bin_path):
                logger.error(f"FATAL: Graphviz 'bin'-Verzeichnis nicht gefunden: {bin_path}")
                return None

            return bin_path
        except Exception as e:
            logger.critical(f"Fehler beim Finden des Graphviz-Pfades: {e}", exc_info=True)
            return None

    def calculate_layout(self, graph: nx.DiGraph):
        """
        Berechnet ein hierarchisches Layout von links nach rechts.
        """
        if not graph.nodes:
            logger.warning("Layout-Berechnung übersprungen: Graph hat keine Knoten.")
            return {}

        try:
            from networkx.drawing.nx_pydot import graphviz_layout

            graphviz_bin_path = self._get_graphviz_path()
            if not graphviz_bin_path:
                raise EnvironmentError("Graphviz-Pfad konnte nicht ermittelt werden.")

            # Temporär den PATH setzen, damit pydot die 'dot'-Executable findet
            original_path = os.environ.get('PATH', '')
            os.environ['PATH'] = f"{graphviz_bin_path}{os.pathsep}{original_path}"

            logger.info("Versuche hierarchisches Layout mit gepatchtem Graphviz...")
            graph.graph['graph'] = {'rankdir': 'LR'}
            pos = graphviz_layout(graph, prog='dot')

            os.environ['PATH'] = original_path  # Zurücksetzen
            logger.info("Horizontales hierarchisches Layout erfolgreich berechnet.")
            return pos
        except Exception as e:
            logger.critical(f"FATAL: Hierarchisches Layout fehlgeschlagen: {e}", exc_info=True)

        # Fallback: Robustes Spring-Layout
        logger.warning("Nutze robustes Spring-Layout als Fallback...")
        try:
            k_value = 200 / (len(graph.nodes()) ** 0.5) if len(graph.nodes()) > 0 else 200
            pos = nx.spring_layout(graph, k=k_value, iterations=100, seed=42)
            logger.info("Robustes Spring-Layout erfolgreich berechnet.")
            return pos
        except Exception as e:
            logger.critical(f"FATAL: Selbst das Fallback-Layout ist fehlgeschlagen: {e}", exc_info=True)
            return {}

        #TODO Für build Datei muss man inital_setup.py umschreiben auf build