import networkx as nx
import sqlglot
import re
from collections import defaultdict
from sqlglot.errors import ParseError

from .sql_cleaner import SQLCleaner
from .sql_executor import SQLExecutor
from .sql_parser import SQLParser
from .dependency_extractor import DependencyExtractor
from .object_resolver import ObjectResolver
from .graph_builder import GraphBuilder
from .data_lineage_config import DataLineageConfig


class DataLineageService:
    """
    Orchestriert den kompletten Data-Lineage-Prozess, indem er die Logik
    eines echten, datenbankgestützten Builders implementiert.
    """
    def __init__(self, config: DataLineageConfig, connection=None):
        self.config = config
        self.connection = connection
        self.sql_executor = SQLExecutor(config, connection)
        self.sql_cleaner = SQLCleaner()
        self.sql_parser = SQLParser()
        self.dependency_extractor = DependencyExtractor(include_ctes=config.include_ctes)
        self.object_resolver = ObjectResolver(connection)
        self.graph_builder = GraphBuilder()

        self.visited_nodes = set()
        self.processing_stack = []


    def build_graph(self, root_artifact: str) -> nx.DiGraph:
        """
        Baut den Graphen iterativ auf, beginnend beim Start-Artefakt.
        """
        if not root_artifact:
            return self.graph_builder.get_graph()

        self.processing_stack.append(root_artifact)
        self.process_nodes_iteratively()

        final_graph = self.graph_builder.get_graph()

        # Optionales Entfernen von CTE-Knoten für eine sauberere Ansicht
        if not self.config.include_ctes:
            self._prune_cte_nodes(final_graph)

        return final_graph

    def process_nodes_iteratively(self):
        """
        Verarbeitet den Stack von zu analysierenden Objekten, bis dieser leer ist.
        """
        while self.processing_stack:
            artifact_name = self.processing_stack.pop()
            if artifact_name in self.visited_nodes:
                continue
            self.visited_nodes.add(artifact_name)

            # 1. SQL für das Artefakt holen
            sql_text = self.sql_executor.get_sql_for_artifact(artifact_name)
            if not sql_text:
                # Füge den Knoten trotzdem hinzu, um Sackgassen darzustellen
                self.graph_builder.add_node(artifact_name, node_type="Undefined")
                continue

            # 2. SQL-Text bereinigen
            cleaned_sql = self.sql_cleaner.clean(sql_text)

            # 3. SQL parsen (mit sqlglot)
            parsed_statements = self.sql_parser.parse(cleaned_sql)
            if not parsed_statements:
                continue

            # 4. Abhängigkeiten extrahieren
            # Annahme: Der DependencyExtractor wurde für sqlglot angepasst
            dependencies = self.dependency_extractor.extract(parsed_statements[0])

            # 5. Abhängigkeiten auflösen und zum Graphen hinzufügen
            self.graph_builder.add_node(artifact_name) # Sicherstellen, dass der Knoten existiert
            for dep_name in dependencies:
                # Hier könnte eine komplexere Auflösung stattfinden (z.B. Schema bestimmen)
                resolved_dep = self.object_resolver.resolve(dep_name)
                if resolved_dep:
                    self.graph_builder.add_edge(resolved_dep, artifact_name)
                    if resolved_dep not in self.visited_nodes:
                        self.processing_stack.append(resolved_dep)


    def _prune_cte_nodes(self, graph: nx.DiGraph):
        """
        Entfernt alle CTE-Knoten aus dem Graph und verbindet ihre
        Vorgänger direkt mit ihren Nachfolgern.
        """
        cte_nodes = [
            n for n, data in graph.nodes(data=True)
            if data.get('data') and getattr(data['data'], 'node_type', '') == 'CTE'
        ]

        for cte in cte_nodes:
            preds = list(graph.predecessors(cte))
            succs = list(graph.successors(cte))
            for p in preds:
                for s in succs:
                    if p != s and not graph.has_edge(p, s):
                        graph.add_edge(p, s)
            graph.remove_node(cte)