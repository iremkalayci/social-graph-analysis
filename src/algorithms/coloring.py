class WelshPowell:
    def __init__(self, graph):
        self.graph = graph

    def color(self):
        # Dereceye göre azalan, eşitlikte id'ye göre artan (deterministik)
        nodes_sorted = sorted(
            self.graph.nodes.values(),
            key=lambda n: (-len(n.neighbors), n.id)
        )

        color_map = {}
        current_color = 0

        for node in nodes_sorted:
            if node.id in color_map:
                continue

            # Yeni bir renk başlat
            color_map[node.id] = current_color

            # Aynı renge boyanabilecek diğer düğümleri seç
            for other in nodes_sorted:
                if other.id in color_map:
                    continue

                # Çakışma: other'ın komşularından biri bu renkte mi?
                if any(color_map.get(nei) == current_color for nei in other.neighbors):
                    continue

                color_map[other.id] = current_color

            current_color += 1

        return color_map
