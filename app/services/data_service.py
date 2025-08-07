import networkx as nx
from app.models.node import Node
from app.data.mock_database import MockDatabase
from app.data.test_data import dependencies as graph_dependencies
import re

class DataService:
    """
    Zentraler Service, der den Graphenerzeugungs-Algorithmus anstößt.
    Er interagiert mit der Datenbankschicht (MockDatabase) für Metadaten
    und nutzt die 'dependencies' für den Graphenbau.
    """

    def __init__(self):
        # Instanziiert die Datenbankschnittstelle.
        self.db = MockDatabase()
        # Hält den Graphen im Cache, um wiederholtes Bauen zu vermeiden
        self._graph_cache = {}

    def get_available_data_sources(self):
        """Holt die verfügbaren Datenquellen von der Datenbankschnittstelle."""
        return self.db.get_available_databases()

    def get_schemas_for_data_source(self, data_source: str):
        """Holt die verfügbaren Schemata für eine gegebene Datenquelle."""
        return self.db.get_schemas_for_database(data_source)

    def get_artifacts_for_schema(self, data_source: str, schema: str, artifact_type: str):
        """Holt Artefakte eines bestimmten Typs aus einem Schema."""
        return self.db.get_artifacts_for_schema(data_source, schema, artifact_type)

    def _sanitize_id(self, name: str) -> str:
        """Erstellt eine saubere, für Graphviz unproblematische ID."""
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)

    def get_graph_for_artifact(self, selections: dict) -> nx.DiGraph:
        """
        Erstellt immer einen Graphen mit drei Knoten (Vorgänger -> Hauptknoten -> Nachfolger),
        um das Layout mit mehreren Knoten zu testen.
        """
        artifact_name = selections.get('artifact')
        if not artifact_name:
            return nx.DiGraph()

        print(f"INFO: Graph-Anforderung für '{artifact_name}' erhalten. Starte Algorithmus mit sauberen IDs...")

        # Cache-Prüfung
        if artifact_name in self._graph_cache:
            print(f"INFO: Graph für '{artifact_name}' aus dem Cache geladen.")
            return self._graph_cache[artifact_name]

        graph = nx.DiGraph()
        nodes_to_process = [artifact_name]
        processed_nodes = set()

        while nodes_to_process:
            current_real_name = nodes_to_process.pop(0)
            if current_real_name in processed_nodes:
                continue
            processed_nodes.add(current_real_name)

            current_clean_id = self._sanitize_id(current_real_name)

            # --- Vorgänger finden (Upstream) ---
            if current_real_name in graph_dependencies:
                details = graph_dependencies[current_real_name]
                inputs = details.get('inputs', []) if isinstance(details, dict) else (details if isinstance(details, list) else [])
                for upstream_real_name in inputs:
                    upstream_clean_id = self._sanitize_id(upstream_real_name)
                    graph.add_edge(upstream_clean_id, current_clean_id)
                    if upstream_real_name not in processed_nodes:
                        nodes_to_process.append(upstream_real_name)

            for process, details in graph_dependencies.items():
                outputs = details.get('outputs', []) if isinstance(details, dict) else []
                if current_real_name in outputs:
                    process_clean_id = self._sanitize_id(process)
                    graph.add_edge(process_clean_id, current_clean_id)
                    if process not in processed_nodes:
                        nodes_to_process.append(process)

            # --- Nachfolger finden (Downstream) ---
            for downstream_real_name, details in graph_dependencies.items():
                inputs = details.get('inputs', []) if isinstance(details, dict) else (details if isinstance(details, list) else [])
                if current_real_name in inputs:
                    downstream_clean_id = self._sanitize_id(downstream_real_name)
                    graph.add_edge(current_clean_id, downstream_clean_id)
                    if downstream_real_name not in processed_nodes:
                        nodes_to_process.append(downstream_real_name)

        # Metadaten für alle Knoten im Graphen hinzufügen/aktualisieren
        for clean_id in list(graph.nodes()):
            # Finde den ursprünglichen, "echten" Namen für den aktuellen sauberen Schlüssel
            # Dies ist eine umgekehrte Suche, die sicherstellt, dass wir den korrekten Namen für die Metadaten haben
            original_name = ""
            for name in processed_nodes:
                if self._sanitize_id(name) == clean_id:
                    original_name = name
                    break

            node_type = "TABLE"
            if "V_" in original_name or "VIEW" in original_name: node_type = "VIEW"
            elif "ELT_" in original_name: node_type = "ELT"

            # KORREKTUR: Das Node-Objekt verwendet jetzt die saubere ID als primäre ID
            node_obj = Node(
                id=clean_id,
                name=original_name.split('.')[-1],
                node_type=node_type,
                context=original_name # Der volle, "echte" Name wird als Kontext gespeichert
            )
            graph.nodes[clean_id]['data'] = node_obj
            # Die Listen der Vorgänger/Nachfolger müssen auch die sauberen IDs enthalten
            graph.nodes[clean_id]['data'].predecessors = [self._sanitize_id(p) for p in graph.predecessors(clean_id)]
            graph.nodes[clean_id]['data'].successors = [self._sanitize_id(s) for s in graph.successors(clean_id)]

        print(f"INFO: Algorithmus abgeschlossen. Graph mit {len(graph.nodes())} Knoten und {len(graph.edges())} Kanten für '{artifact_name}' wurde erstellt.")

        self._graph_cache[artifact_name] = graph
        return graph