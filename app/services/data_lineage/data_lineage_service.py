import networkx as nx
from .sql_cleaner import SQLCleaner
from .sql_executor import SQLExecutor
from .sql_parser import SQLParser
from .dependency_extractor import DependencyExtractor
from .object_resolver import ObjectResolver
from .graph_builder import GraphBuilder
from .graph_utils import GraphUtils
from .data_lineage_config import DataLineageConfig


class DataLineageService:
    """
    Orchestriert den kompletten Data-Lineage-Prozess.
    """
    def __init__(self, config: DataLineageConfig, connection=None):
        self.config = config
        self.connection = connection
        self.sql_cleaner = SQLCleaner()
        self.sql_executor = SQLExecutor(config, connection)
        self.sql_parser = SQLParser()
        self.dependency_extractor = DependencyExtractor()
        self.object_resolver = ObjectResolver(connection)
        self.graph_builder = GraphBuilder()

    def build_graph(self, root_artifact: str) -> nx.DiGraph:
        visited = set()
        to_visit = [root_artifact]

        while to_visit:
            artifact = to_visit.pop()
            if artifact in visited:
                continue
            visited.add(artifact)

            sql_text = self.sql_executor.get_sql_for_artifact(artifact)
            if not sql_text:
                continue

            cleaned_sql = self.sql_cleaner.clean(sql_text)
            parsed = self.sql_parser.parse(cleaned_sql)
            deps = self.dependency_extractor.extract(parsed)

            resolved_deps = [self.object_resolver.resolve(dep) for dep in deps]
            self.graph_builder.add_node(artifact)
            for dep in resolved_deps:
                self.graph_builder.add_edge(dep, artifact)
                to_visit.append(dep)

        return self.graph_builder.get_graph()
