from collections import deque
from src.algorithms.base import Algorithm

class BFS(Algorithm):
    def run(self, start_id):
        if start_id not in self.graph.nodes:
            raise ValueError("Baslangic dugumu yok")

        visited = set()
        order = []          # ziyaret sırası
        queue = deque([start_id])

        visited.add(start_id)

        while queue:
            current = queue.popleft()
            order.append(current)

            for komsu in self.graph.nodes[current].neighbors:
                if komsu not in visited:
                    visited.add(komsu)
                    queue.append(komsu)

        return order
