from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Node:
    """
    Ein strukturiertes Datenobjekt, das einen Knoten im Graphen repräsentiert.
    """
    id: str  # Eindeutiger Bezeichner des Knotens
    name: str  # Anzeigename, z.B. der Artefakt- oder Tabellenname
    node_type: str  # z.B. 'ELT', 'TABLE', 'VIEW', 'SCRIPT', 'CTE'

    # Optionale, detaillierte Informationen
    context: Optional[str] = "Nicht spezifiziert"
    description: Optional[str] = "Keine Beschreibung verfügbar."
    owner: Optional[str] = "Unbekannt"

    # Vorgänger und Nachfolger werden bei der Graph-Erstellung dynamisch gefüllt
    predecessors: List[str] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)