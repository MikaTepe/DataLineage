class GraphUtils:
    """
    Hilfsfunktionen für Graphen.
    """
    @staticmethod
    def summarize_graph(graph):
        return {
            "nodes": len(graph.nodes),
            "edges": len(graph.edges)
        }
