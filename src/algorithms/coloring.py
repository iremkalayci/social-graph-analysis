class WelshPowell:
    def __init__(self, graph):
        self.graph = graph

    def color(self):
        # Düğümleri dereceye göre azalan sırala
        nodes_sorted = sorted(
            self.graph.nodes.values(),
            key=lambda n: len(n.neighbors),
            reverse=True
        )

        color_map = {}
        current_color = 0

        for node in nodes_sorted:
            if node.id in color_map:
                continue

            color_map[node.id] = current_color

            for other in nodes_sorted:
                if other.id not in color_map:
                    conflict = False
                    for neighbor in other.neighbors:
                        if neighbor in color_map and color_map[neighbor] == current_color:
                            conflict = True
                            break
                    if not conflict:
                        color_map[other.id] = current_color

            current_color += 1

        return color_map
