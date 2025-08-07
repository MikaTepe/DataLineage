import networkx as nx
from app.models.node import Node
from app.data.mock_database import MockDatabase
from app.data.test_data import dependencies as graph_dependencies


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

    def get_graph_for_artifact(self, selections: dict) -> nx.DiGraph:
        """
        Erstellt immer einen Graphen mit drei Knoten (Vorgänger -> Hauptknoten -> Nachfolger),
        um das Layout mit mehreren Knoten zu testen.
        """
        artifact_name = selections.get('artifact')
        if not artifact_name:
            return nx.DiGraph()

        print(f"INFO: Graph-Anforderung für '{artifact_name}' erhalten. Algorithmus wird gestartet...")

        # Cache-Prüfung
        if artifact_name in self._graph_cache:
            print(f"INFO: Graph für '{artifact_name}' aus dem Cache geladen.")
            return self._graph_cache[artifact_name]

        graph = nx.DiGraph()
        nodes_to_process = [artifact_name]
        processed_nodes = set()

        # Rekursive Funktion zum Hinzufügen von Knoten und Kanten
        def add_related_nodes(node_name, direction):
            if node_name not in graph_dependencies:
                return

            if direction == 'predecessors':
                # Inputs/Vorgänger holen
                related = graph_dependencies[node_name]
                if isinstance(related, dict):
                    related = related.get('inputs', [])
            else:  # successors
                # Outputs/Nachfolger holen
                related = graph_dependencies[node_name]
                if isinstance(related, dict):
                    related = related.get('outputs', [])
                else:  # Wenn es eine View ist, die nur inputs hat
                    related = []

            for rel_node in related:
                # Kante hinzufügen
                if direction == 'predecessors':
                    graph.add_edge(rel_node, node_name)
                else:
                    graph.add_edge(node_name, rel_node)

                # Den verbundenen Knoten zur weiteren Verarbeitung hinzufügen
                if rel_node not in processed_nodes:
                    nodes_to_process.append(rel_node)

        while nodes_to_process:
            current_node_name = nodes_to_process.pop(0)
            if current_node_name in processed_nodes:
                continue

            processed_nodes.add(current_node_name)

            # Füge Vorgänger hinzu
            add_related_nodes(current_node_name, 'predecessors')
            # Füge Nachfolger hinzu
            add_related_nodes(current_node_name, 'successors')

            # Finde alle Knoten, die den aktuellen Knoten als Input verwenden (Nachfolger)
            for potential_successor, details in graph_dependencies.items():
                inputs = []
                if isinstance(details, list):
                    inputs = details
                elif isinstance(details, dict):
                    inputs = details.get('inputs', [])

                if current_node_name in inputs:
                    graph.add_edge(current_node_name, potential_successor)
                    if potential_successor not in processed_nodes:
                        nodes_to_process.append(potential_successor)

        # Alle Knoten im Graphen mit Metadaten anreichern
        for node_id in list(graph.nodes()):
            # Falls ein Knoten noch nicht als "data" Attribut existiert
            if 'data' not in graph.nodes[node_id]:
                # Annahme des Typs basierend auf dem Namen
                node_type = "TABLE"
                if node_id.startswith("V_"):
                    node_type = "VIEW"
                elif node_id.startswith("ELT_"):
                    node_type = "ELT"

                node_obj = Node(id=node_id, name=node_id, node_type=node_type)
                graph.nodes[node_id]['data'] = node_obj

            # Vorgänger und Nachfolger aktualisieren
            node_data = graph.nodes[node_id]['data']
            node_data.predecessors = list(graph.predecessors(node_id))
            node_data.successors = list(graph.successors(node_id))

        print(
            f"INFO: Algorithmus abgeschlossen. Graph mit {len(graph.nodes())} Knoten und {len(graph.edges())} Kanten für '{artifact_name}' wurde erstellt.")

        self._graph_cache[artifact_name] = graph
        return graph