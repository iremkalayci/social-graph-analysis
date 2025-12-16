from src.algorithms.base import Algorithm
class BFS(Algorithm):
    def run(self,start_id):
        if start_id not in self.graph.nodes:
            raise ValueError("baslangic dugumu yok")
        visited=set()
        queue=[start_id]
        while queue:
            current=queue.pop(0)
            if current not in visited:
                visited.add(current)
                for komsu in self.graph.nodes[current].neighbors:
                    if komsu not in visited:
                        queue.append(komsu)
        return visited