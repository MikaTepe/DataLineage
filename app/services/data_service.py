import re
import networkx as nx
from typing import List

from app.models.node import Node
from app.data.mock_database import MockDatabase
from app.data import test_data  # nutzt dependencies / optional sql_definitions

from app.services.data_lineage import (
    DataLineageService,
    DataLineageConfig,
)


class DataService:
    """
    Zentraler Service für Graphenaufbau und Metadaten.
    - mock_mode=True: nutzt MockDatabase & test_data.dependencies/sql_definitions
    - mock_mode=False: nutzt DataLineageService (echter Algorithmus, DB-Verbindung)
    """

    def __init__(self, mock_mode: bool = True, connection=None):
        self.mock_mode = mock_mode
        self.connection = connection
        self.db = MockDatabase() if mock_mode else None
        self._graph_cache = {}

    # ---------------------------
    # Öffentliche UI-APIs (unverändert)
    # ---------------------------
    def get_available_data_sources(self) -> List[str]:
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
        Haupt-Einstiegspunkt: gibt einen NetworkX-DiGraph zurück.
        - Mock: baut Graph aus test_data.dependencies (wie vorher)
        - Real: ruft DataLineageService auf (neuer Algorithmus)
        """
        if self.mock_mode:
            return self._build_mock_graph(selections)
        else:
            return self._build_real_graph(selections)

    # ---------------------------
    # Interner Mock-Graph-Builder
    # ---------------------------
    def _build_mock_graph(self, selections: dict) -> nx.DiGraph:
        """
        Kompatibel zur bisherigen Mock-Logik:
        - nutzt test_data.dependencies zum Kantenbau
        - erzeugt Node-Objekte im Attribut 'data'
        - füllt predecessors/successors
        """
        artifact_name = selections.get('artifact')
        if not artifact_name:
            return nx.DiGraph()

        # Cache
        if artifact_name in self._graph_cache:
            return self._graph_cache[artifact_name]

        dependencies = getattr(test_data, "dependencies", {})
        graph = nx.DiGraph()
        nodes_to_process = [artifact_name]
        processed_nodes = set()

        while nodes_to_process:
            current_real_name = nodes_to_process.pop(0)
            if current_real_name in processed_nodes:
                continue
            processed_nodes.add(current_real_name)

            current_clean_id = self._sanitize_id(current_real_name)

            # --- Upstream (Inputs) ---
            if current_real_name in dependencies:
                details = dependencies[current_real_name]
                inputs = details.get('inputs', []) if isinstance(details, dict) else (
                    details if isinstance(details, list) else []
                )
                for upstream_real_name in inputs:
                    upstream_clean_id = self._sanitize_id(upstream_real_name)
                    graph.add_edge(upstream_clean_id, current_clean_id)
                    if upstream_real_name not in processed_nodes:
                        nodes_to_process.append(upstream_real_name)

            # --- Downstream (Artefakte, die current als Input nutzen) ---
            for downstream_real_name, details in dependencies.items():
                inputs = details.get('inputs', []) if isinstance(details, dict) else (
                    details if isinstance(details, list) else []
                )
                if current_real_name in inputs:
                    downstream_clean_id = self._sanitize_id(downstream_real_name)
                    graph.add_edge(current_clean_id, downstream_clean_id)
                    if downstream_real_name not in processed_nodes:
                        nodes_to_process.append(downstream_real_name)

        # Node-Objekte & Metadaten
        for clean_id in list(graph.nodes()):
            original_name = next(
                (n for n in processed_nodes if self._sanitize_id(n) == clean_id),
                clean_id
            )
            node_type = self._infer_type_from_name(original_name)
            node_obj = Node(
                id=clean_id,
                name=original_name.split('.')[-1],
                node_type=node_type,
                context=original_name
            )
            graph.nodes[clean_id]['data'] = node_obj
            graph.nodes[clean_id]['data'].predecessors = [self._sanitize_id(p) for p in graph.predecessors(clean_id)]
            graph.nodes[clean_id]['data'].successors = [self._sanitize_id(s) for s in graph.successors(clean_id)]

        self._graph_cache[artifact_name] = graph
        return graph

    # ---------------------------
    # Interner Real-Graph-Builder
    # ---------------------------
    def _build_real_graph(self, selections: dict) -> nx.DiGraph:
        """
        Nutzt den neuen DataLineageService. Erwartet:
        - selections['artifact']
        Optionale Felder:
        - selections['include_ctes'] (bool) → mapped auf Config
        - selections['max_depth'] (int)
        """
        artifact = selections.get("artifact")
        if not artifact:
            return nx.DiGraph()

        include_ctes = bool(selections.get("include_ctes", False))
        max_depth = int(selections.get("max_depth", 5))

        config = DataLineageConfig(
            mock_mode=False,
            include_ctes=include_ctes,
            max_depth=max_depth,
        )
        service = DataLineageService(config=config, connection=self.connection)
        graph = service.build_graph(root_artifact=artifact)

        # Falls deine UI erwartet, dass predecessors/successors in Node.data befüllt sind:
        self._populate_node_relations(graph)
        return graph

    # ---------------------------
    # Helpers
    # ---------------------------
    def _sanitize_id(self, name: str) -> str:
        """Erstellt eine saubere ID (GraphCanvas/Graphviz-freundlich)."""
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)

    def _infer_type_from_name(self, original_name: str) -> str:
        """Heuristik wie vorher: VIEW/ELT/Table anhand des Namens."""
        up = original_name.upper()
        if "V_" in up or "VIEW" in up:
            return "VIEW"
        if "ELT_" in up:
            return "ELT"
        return "TABLE"

    def _populate_node_relations(self, graph: nx.DiGraph) -> None:
        """Setzt predecessors/successors-Listen in den Node-Objekten (für die UI)."""
        for node_id in graph.nodes:
            attrs = graph.nodes[node_id]
            node_obj: Node = attrs.get('data')
            if not isinstance(node_obj, Node):
                # Falls der DataLineageService den Node ohne Node-Objekt angelegt hat,
                # minimal befüllen:
                name_for_label = node_id.replace('_', '.')
                node_obj = Node(
                    id=node_id,
                    name=name_for_label.split('.')[-1],
                    node_type=attrs.get("SQL_Befehl", "TABLE"),
                    context=name_for_label
                )
                graph.nodes[node_id]['data'] = node_obj

            preds = [p for p in graph.predecessors(node_id)]
            succs = [s for s in graph.successors(node_id)]
            node_obj.predecessors = preds
            node_obj.successors = succs
