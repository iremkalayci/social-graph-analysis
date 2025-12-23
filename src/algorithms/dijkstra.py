import heapq
from src.algorithms.base import Algorithm

class Dijkstra(Algorithm):
    def run(self, start_id, end_id):
        if start_id not in self.graph.nodes or end_id not in self.graph.nodes:
            raise ValueError("Başlangıç veya hedef düğüm yok")

        if start_id == end_id:
            return 0.0, [start_id]

        distances = {nid: float("inf") for nid in self.graph.nodes}
        previous = {}

        distances[start_id] = 0.0
        pq = [(0.0, start_id)]

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current_dist > distances[current]:
                continue

            if current == end_id:
                break

            for neighbor in self.graph.nodes[current].neighbors:
                key = tuple(sorted((current, neighbor)))
                edge = self.graph.edges.get(key)
                if edge is None:
                    continue

                cost = float(edge.weight)   # isterlere göre: weight = maliyet
                new_dist = current_dist + cost

                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))

        if distances[end_id] == float("inf"):
            return float("inf"), []

        # Path reconstruction
        path = []
        cur = end_id
        while cur != start_id:
            path.append(cur)
            cur = previous.get(cur)
            if cur is None:
                return float("inf"), []
        path.append(start_id)
        path.reverse()

        return distances[end_id], path
