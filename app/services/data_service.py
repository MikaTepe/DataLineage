import networkx as nx
from app.data.test_data import test_cache_data, db_connections_data
from app.models.node import Node


class DataService:
    """Stellt die Testdaten für den Dialog bereit und baut Graphen."""

    def get_cache_data(self):
        return test_cache_data

    def get_db_connections(self):
        return db_connections_data

    def build_graph_for_selection(self, selections: dict) -> nx.DiGraph:
        """
        Baut einen Graphen basierend auf der Auswahl aus dem Dialog.
        Für dieses Beispiel generieren wir einen repräsentativen Graphen.
        """
        graph = nx.DiGraph()
        artifact_name = selections['artifact']

        # Knoten basierend auf der Auswahl erstellen
        node1 = Node(id=artifact_name, name=artifact_name, node_type=selections['artifact_type'])
        node2 = Node(id="source_table_1", name="Source Table 1", node_type="TABLE")
        node3 = Node(id="source_view_1", name="Source View 1", node_type="VIEW")

        graph.add_node(node1.id, data=node1)
        graph.add_node(node2.id, data=node2)
        graph.add_node(node3.id, data=node3)

        graph.add_edge(node2.id, node3.id)
        graph.add_edge(node3.id, node1.id)

        # Fülle Vorgänger/Nachfolger für den Info-Dialog
        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]['data']
            node_data.predecessors = list(graph.predecessors(node_id))
            node_data.successors = list(graph.successors(node_id))

        return graph