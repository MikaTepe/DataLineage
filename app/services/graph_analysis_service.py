import networkx as nx
from typing import Optional


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
            raise TypeError("nx.DiGraph erwartet.")
        self.graph = graph

    def find_node_by_name(self, query: str) -> Optional[str]:
        """
        Findet den ersten Knoten, dessen Name die Suchanfrage enthält (case-insensitive).
        """
        if not query:
            return None

        for node_id, node_data in self.graph.nodes(data=True):
            node_obj = node_data.get('data')
            if node_obj and query.lower() in getattr(node_obj, 'name', '').lower():
                return node_id
        return None

    def get_all_predecessors(self, start_node: str) -> set:
        return {start_node, *nx.ancestors(self.graph, start_node)} if start_node in self.graph else set()

    def get_all_successors(self, start_node: str) -> set:
        return {start_node, *nx.descendants(self.graph, start_node)} if start_node in self.graph else set()

    def summarize_graph(self):
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "cycles": list(nx.simple_cycles(self.graph)),
            "endpoints": [n for n in self.graph.nodes if self.graph.out_degree(n) == 0]
        }

    def prune_cte_nodes(self):
        cte_nodes = [n for n, d in self.graph.nodes(data=True) if d.get("SQL_Befehl") == "CTE"]
        for cte in cte_nodes:
            preds = list(self.graph.predecessors(cte))
            succs = list(self.graph.successors(cte))
            for p in preds:
                for s in succs:
                    if p != s and not self.graph.has_edge(p, s):
                        self.graph.add_edge(p, s)
            self.graph.remove_node(cte)
