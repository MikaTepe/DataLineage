import re
import networkx as nx
from app.models.node import Node
from app.data import test_data

class MockGraphBuilder:
    """
    Baut einen Data-Lineage-Graphen ausschließlich aus den statischen
    `test_data.dependencies`.
    """
    def __init__(self):
        self._graph_cache = {}
        # Der Gesamtgraph aller möglichen Abhängigkeiten wird einmalig erstellt.
        self._full_dependency_graph, self._all_nodes = self._build_full_dependency_graph()

    def _build_full_dependency_graph(self):
        """
        Baut einmalig einen Graphen, der ALLE definierten Abhängigkeiten enthält.
        """
        dependencies = getattr(test_data, "dependencies", {})
        full_graph = nx.DiGraph()
        all_nodes = set()

        for key, value in dependencies.items():
            all_nodes.add(key)
            inputs = []

            if isinstance(value, list):
                inputs = value
            elif isinstance(value, dict):
                inputs = value.get('inputs', [])
                for output in value.get('outputs', []):
                    all_nodes.add(output)
                    full_graph.add_edge(self._sanitize_id(key), self._sanitize_id(output))

            for source in inputs:
                all_nodes.add(source)
                full_graph.add_edge(self._sanitize_id(source), self._sanitize_id(key))

        return full_graph, all_nodes

    def build_graph(self, selections: dict) -> nx.DiGraph:
        """
        Extrahiert den relevanten Subgraphen für das ausgewählte Artefakt.
        """
        artifact_name = selections.get('artifact')
        start_node_clean = self._sanitize_id(artifact_name)

        if not artifact_name or start_node_clean not in self._full_dependency_graph:
            return nx.DiGraph()

        if artifact_name in self._graph_cache:
            return self._graph_cache[artifact_name]

        ancestors = nx.ancestors(self._full_dependency_graph, start_node_clean)
        descendants = nx.descendants(self._full_dependency_graph, start_node_clean)
        relevant_nodes = ancestors.union(descendants).union({start_node_clean})

        final_graph = self._full_dependency_graph.subgraph(relevant_nodes).copy()

        for clean_id in final_graph.nodes():
            original_name = next((n for n in self._all_nodes if self._sanitize_id(n) == clean_id), clean_id)
            node_type = self._infer_type_from_name(original_name)
            node_obj = Node(
                id=clean_id,
                name=original_name.split('.')[-1],
                node_type=node_type,
                context=original_name,
                predecessors=list(final_graph.predecessors(clean_id)),
                successors=list(final_graph.successors(clean_id))
            )
            final_graph.nodes[clean_id]['data'] = node_obj

        self._graph_cache[artifact_name] = final_graph
        return final_graph

    def _sanitize_id(self, name: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)

    def _infer_type_from_name(self, original_name: str) -> str:
        up = original_name.upper()
        if "V_" in up or "VIEW" in up: return "VIEW"
        if "ELT_" in up: return "ELT"
        return "TABLE"