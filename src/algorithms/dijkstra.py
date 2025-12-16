import heapq
from src.algorithms.base import Algorithm

class Dijkstra(Algorithm):
    def run(self, start_id, end_id):
        if start_id not in self.graph.nodes or end_id not in self.graph.nodes:
            raise ValueError("Baslangic veya hedef dugum yok")

        distances = {node_id: float("inf") for node_id in self.graph.nodes}
        previous = {}

        distances[start_id] = 0
        pq = [(0, start_id)]

        while pq:
            current_dist, current = heapq.heappop(pq)

            if current == end_id:
                break

            if current_dist > distances[current]:
                continue

            for komsu in self.graph.nodes[current].neighbors:
                key = tuple(sorted((current, komsu)))
                edge = self.graph.edges[key]
                new_dist = current_dist + edge.weight

                if new_dist < distances[komsu]:
                    distances[komsu] = new_dist
                    previous[komsu] = current
                    heapq.heappush(pq, (new_dist, komsu))

        path = []
        cur = end_id
        while cur in previous:
            path.append(cur)
            cur = previous[cur]
        path.append(start_id)
        path.reverse()

        return distances[end_id], path
