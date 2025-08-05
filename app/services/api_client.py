import os
import time
import random

class ApiClient:
    """Simuliert Anfragen an die Data Lineage API."""
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://mock.api")

    def get_available_artifacts(self):
        """Ruft die Liste der verfügbaren Artefakte ab."""
        print(f"API: Rufe Artefakte ab...")
        time.sleep(0.2)
        return ["VDH_IAM_FAKT_ANLASS_OHNEKOLLISION", "RMS_ALG_STKTF_WZ", "VDH_IAM_FAKT_MAP_ANLASS_SUBZIELGRUPPE_AUZUSPIELEN", "Sales-Report_2024"]

    def get_graph_data_for_artifact(self, artifact_id: str):
        """Ruft Graphendaten für ein Artefakt ab."""
        print(f"API: Rufe Graph für '{artifact_id}' ab...")
        time.sleep(0.5)

        nodes = []
        # Hauptknoten
        nodes.append({"id": artifact_id, "label": artifact_id, "type": "ELT"})

        # Unterknoten
        for i in range(1, random.randint(5, 15)):
            node_id = f"table_{i}"
            node_type = random.choice(["TABLE", "VIEW", "CTE", "SCRIPT"])
            nodes.append({"id": node_id, "label": f"{node_type}_{i}", "type": node_type})

        edges = []
        # Kanten von Unterknoten zum Hauptknoten oder zu anderen Unterknoten
        for i in range(1, len(nodes)):
            source_node = random.choice(nodes[i:])
            target_node = nodes[i-1]
            if source_node['id'] != target_node['id']:
                 edges.append({"source": source_node['id'], "target": target_node['id']})

        return {"nodes": nodes, "edges": edges}