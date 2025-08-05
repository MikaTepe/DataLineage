import networkx as nx


class LayoutService:
    """
    Berechnet ein robustes und visuell ansprechendes Layout für einen Graphen.
    Diese Version benötigt keine externen Abhängigkeiten wie Graphviz.
    """

    def calculate_layout(self, graph: nx.DiGraph):
        """
        Wählt den besten verfügbaren Layout-Algorithmus basierend auf der
        Graphenstruktur, um sicherzustellen, dass die Knoten immer verteilt sind.
        """
        if not graph.nodes:
            print("Layout-Berechnung übersprungen: Graph hat keine Knoten.")
            return {}

        # muss überarbeitet werden
        is_connected = nx.is_weakly_connected(graph)

        if is_connected:
            print("Graph ist zusammenhängend. Verwende Kamada-Kawai-Layout für beste Ergebnisse...")
            try:
                pos = nx.kamada_kawai_layout(graph)
                print("Kamada-Kawai-Layout erfolgreich berechnet.")
                return pos
            except Exception as e:
                print(f"Kamada-Kawai-Layout fehlgeschlagen (selbst bei verbundenem Graph): {e}")
                # Fallback, falls etwas Unerwartetes passiert

        else:
            print("Graph ist nicht zusammenhängend.")

        # Fallback für nicht zusammenhängende Graphen oder wenn kamada_kawai fehlschlägt
        print("Nutze robustes Spring-Layout...")

        pos = nx.spring_layout(graph, k=200 / (len(graph.nodes()) ** 0.5), iterations=100, seed=42)

        print("Robustes Spring-Layout erfolgreich berechnet.")
        return pos