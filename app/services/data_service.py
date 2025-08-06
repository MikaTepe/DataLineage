import networkx as nx
from app.models.node import Node
from app.data.mock_database import MockDatabase


class DataService:
    """
    Zentraler Service, der den Graphenerzeugungs-Algorithmus anstößt.
    Er interagiert mit der Datenbankschicht (aktuell MockDatabase).
    """

    def __init__(self):
        # Instanziiert die Datenbankschnittstelle.
        self.db = MockDatabase()

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
        **Minimal geänderte Mock-Implementierung.**
        Erstellt immer einen Graphen mit drei Knoten (Vorgänger -> Hauptknoten -> Nachfolger),
        um das Layout mit mehreren Knoten zu testen.
        """
        artifact_name = selections.get('artifact')
        artifact_type = selections.get('artifact_type', 'Undefined')

        print(f"INFO: Graph-Anforderung für '{artifact_name}' erhalten. Algorithmus wird angestoßen...")

        # --- Hier beginnt der eigentliche Algorithmus ---
        # 1. Graph aus dem Cache holen (zukünftig)
        # 2. Wenn nicht im Cache oder veraltet, neu aus der DB bauen
        #    - Hole Haupt-Knoten
        #    - Hole dessen Abhängigkeiten (Vorgänger/Nachfolger) rekursiv
        # 3. Graph zurückgeben

        graph = nx.DiGraph()

        # 1. Hauptknoten erstellen
        main_node = Node(id=artifact_name, name=artifact_name, node_type=artifact_type)
        graph.add_node(main_node.id, data=main_node)

        # 2. Immer einen Vorgänger und einen Nachfolger hinzufügen
        source_node = Node(id=f"source_for_{artifact_name}", name="Beispiel-Quelle", node_type="TABLE")
        target_node = Node(id=f"target_for_{artifact_name}", name="Beispiel-Ziel", node_type="VIEW")

        graph.add_node(source_node.id, data=source_node)
        graph.add_node(target_node.id, data=target_node)

        # Kanten hinzufügen
        graph.add_edge(source_node.id, main_node.id)
        graph.add_edge(main_node.id, target_node.id)

        # Metadaten für den Info-Dialog anreichern
        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]['data']
            node_data.predecessors = list(graph.predecessors(node_id))
            node_data.successors = list(graph.successors(node_id))

        print(
            f"INFO: Algorithmus abgeschlossen. Graph mit {len(graph.nodes())} Knoten für '{artifact_name}' wurde erstellt.")
        return graph
