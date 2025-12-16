from src.algorithms.base import Algorithm

class DFS(Algorithm):
    def run(self, start_id):
        if start_id not in self.graph.nodes:
            raise ValueError("Baslangic dugumu yok")

        visited = set()

        def explore(n):
            visited.add(n)
            for komsu in self.graph.nodes[n].neighbors:
                if komsu not in visited:
                    explore(komsu)

        explore(start_id)
        return visited
