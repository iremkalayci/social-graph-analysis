import heapq
import math

class AStar:
    def __init__(self, graph):
        self.graph = graph

    def heuristic(self, a, b):
        # Basit sezgisel: node id farkı
        return abs(a - b)

    def run(self, start_id, end_id):
        pq = []
        heapq.heappush(pq, (0, start_id))

        came_from = {}
        g_score = {nid: math.inf for nid in self.graph.nodes}
        g_score[start_id] = 0

        while pq:
            _, current = heapq.heappop(pq)

            if current == end_id:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return g_score[end_id], path[::-1]

            for neighbor in self.graph.nodes[current].neighbors:
                edge_key = tuple(sorted((current, neighbor)))
                weight = self.graph.edges[edge_key].weight
                tentative = g_score[current] + weight

                if tentative < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    f_score = tentative + self.heuristic(neighbor, end_id)
                    heapq.heappush(pq, (f_score, neighbor))

        return math.inf, []
