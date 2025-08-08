import networkx as nx
from typing import List

from app.models.node import Node
from app.data.mock_database import MockDatabase
from .mock_graph_builder import MockGraphBuilder  # Importieren

from app.services.data_lineage import (
    DataLineageService,
    DataLineageConfig,
)


class DataService:
    """
    Zentraler Service für Graphenaufbau und Metadaten.
    Dient als Fassade, die Anfragen an die zuständigen Builder weiterleitet.
    """

    def __init__(self, mock_mode: bool = True, connection=None):
        self.mock_mode = mock_mode
        self.connection = connection
        self.db = MockDatabase() if mock_mode else None

        # Den richtigen Builder instanziieren
        self.mock_builder = MockGraphBuilder() if mock_mode else None

    def get_available_data_sources(self) -> List[str]:
        # Diese Methoden bleiben gleich
        if self.mock_mode:
            return self.db.get_available_databases()
        # Real-Mode: hier könntest du auf echte Quellen gehen
        return ["REAL_DB"]

    def get_schemas_for_data_source(self, data_source: str) -> List[str]:
        if self.mock_mode:
            return self.db.get_schemas_for_database(data_source)
        # Real-Mode: schemata aus DB lesen (Platzhalter)
        return ["PUBLIC"]

    def get_artifacts_for_schema(self, data_source: str, schema: str, artifact_type: str) -> List[str]:
        if self.mock_mode:
            return self.db.get_artifacts_for_schema(data_source, schema, artifact_type)
        # Real-Mode: Artefakte aus DB lesen (Platzhalter)
        return []

    def get_graph_for_artifact(self, selections: dict) -> nx.DiGraph:
        """
        Delegiert die Graphenerstellung an den zuständigen Builder.
        """
        if self.mock_mode:
            return self.mock_builder.build_graph(selections)
        else:
            # Der Real-Mode wird jetzt auch sauberer delegiert
            return self._build_real_graph(selections)

    def _build_real_graph(self, selections: dict) -> nx.DiGraph:
        """
        Konfiguriert und startet den DataLineageService für den Real-Modus.
        """
        artifact = selections.get("artifact")
        if not artifact:
            return nx.DiGraph()

        config = DataLineageConfig(
            mock_mode=False,
            include_ctes=bool(selections.get("include_ctes", False)),
            max_depth=int(selections.get("max_depth", 5)),
        )
        service = DataLineageService(config=config, connection=self.connection)
        graph = service.build_graph(root_artifact=artifact)

        # Falls deine UI erwartet, dass predecessors/successors in Node.data befüllt sind:
        self._populate_node_relations(graph)
        return graph

    def _populate_node_relations(self, graph: nx.DiGraph) -> None:
        """Füllt die Vorgänger/Nachfolger-Listen in den Node-Objekten."""
        for node_id, attrs in graph.nodes(data=True):
            node_obj: Node = attrs.get('data')
            if node_obj:
                node_obj.predecessors = list(graph.predecessors(node_id))
                node_obj.successors = list(graph.successors(node_id))