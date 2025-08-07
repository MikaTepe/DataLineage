import networkx as nx


class GraphAnalysisService:
    """
    Stellt Methoden zur Analyse von Graphen bereit, z.B. für die Suche
    nach Vorgängern oder Nachfolgern.
    """

    def __init__(self, graph: nx.DiGraph):
        """
        Initialisiert den Service mit einem Graphen.
        """
        if not isinstance(graph, nx.DiGraph):
            raise TypeError("Ein networkx.DiGraph wird als Graph-Objekt erwartet.")
        self.graph = graph

    def find_node_by_name(self, query: str) -> str | None:
        """
        Findet den ersten Knoten, dessen Name die Suchanfrage enthält (case-insensitive).
        """
        if not query:
            return None

        for node_id, node_data in self.graph.nodes(data=True):
            node_name = node_data.get('data', {}).get('name', '')
            if query.lower() in node_name.lower():
                return node_id
        return None

    def get_all_predecessors(self, start_node: str) -> set:
        """
        Gibt ein Set mit dem Startknoten und allen seinen Vorgängern zurück.
        """
        if start_node not in self.graph:
            return set()

        # nx.ancestors findet alle Vorgänger
        predecessors = nx.ancestors(self.graph, start_node)
        # Füge den Startknoten selbst zum Set hinzu
        predecessors.add(start_node)
        return predecessors

    def get_all_successors(self, start_node: str) -> set:
        """
        Gibt ein Set mit dem Startknoten und allen seinen Nachfolgern zurück.
        """
        if start_node not in self.graph:
            return set()

        # nx.descendants findet alle Nachfolger
        successors = nx.descendants(self.graph, start_node)
        # Füge den Startknoten selbst zum Set hinzu
        successors.add(start_node)
        return successors