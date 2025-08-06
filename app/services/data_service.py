import networkx as nx
from app.models.node import Node
from app.data.mock_database import MockDatabase  # Importiert die neue Mock-Datenbank


class DataService:
    """
    Zentraler Service, der den Graphenerzeugungs-Algorithmus anstößt.
    Er interagiert mit der Datenbankschicht (aktuell MockDatabase).
    """

    def __init__(self):
        # Instanziiert die Datenbankschnittstelle.
        # Später kann hier eine echte Datenbankverbindung oder ein Pool verwaltet werden.
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
        **Zentraler Endpunkt zur Graphenerzeugung.**

        Diese Methode ist der einzige Einstiegspunkt für die Anforderung eines Graphen.
        Sie ruft den Algorithmus zur Graphenerstellung auf (derzeit als Mock implementiert).
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
        #
        # Aktuelle Mock-Implementierung:
        graph = nx.DiGraph()
        main_node = Node(id=artifact_name, name=artifact_name, node_type=artifact_type)
        graph.add_node(main_node.id, data=main_node)

        # Simuliere einige Abhängigkeiten basierend auf dem Typ
        if artifact_type == "VIEW":
            source_table = Node(id=f"src_table_for_{artifact_name}", name="BASE_TABLE", node_type="TABLE")
            graph.add_node(source_table.id, data=source_table)
            graph.add_edge(source_table.id, main_node.id)

        if artifact_type == "ELT":
            source_table = Node(id=f"src_for_{artifact_name}", name="SOURCE_DATA", node_type="TABLE")
            target_table = Node(id=f"target_for_{artifact_name}", name="TARGET_TABLE", node_type="TABLE")
            graph.add_node(source_table.id, data=source_table)
            graph.add_node(target_table.id, data=target_table)
            graph.add_edge(source_table.id, main_node.id)
            graph.add_edge(main_node.id, target_table.id)

        # Metadaten für den Info-Dialog anreichern
        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]['data']
            node_data.predecessors = list(graph.predecessors(node_id))
            node_data.successors = list(graph.successors(node_id))

        print(f"INFO: Algorithmus abgeschlossen. Graph für '{artifact_name}' wurde erstellt.")
        return graph
