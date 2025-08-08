import networkx as nx
from app.models.node import Node

class GraphBuilder:
    """
    Baut einen NetworkX-DiGraph für Data-Lineage.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, name: str, node_type="TABLE"):
        clean_id = name.replace(".", "_")
        if clean_id not in self.graph:
            self.graph.add_node(clean_id, data=Node(id=clean_id, name=name, node_type=node_type))

    def add_edge(self, src: str, dst: str):
        self.add_node(src)
        self.add_node(dst)
        self.graph.add_edge(src.replace(".", "_"), dst.replace(".", "_"))

    def get_graph(self):
        return self.graph
