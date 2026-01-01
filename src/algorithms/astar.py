import heapq
import math 
from src.algorithms.base import Algorithm

class AStar(Algorithm):
    def heuristic(self, a, b):
          n1 = self.graph.nodes[a]
          n2 = self.graph.nodes[b]

          d_aktif = n1.aktiflik - n2.aktiflik
          d_etk = n1.etkilesim - n2.etkilesim
          d_bag = n1.baglanti_sayisi - n2.baglanti_sayisi


          dist = math.sqrt(d_aktif**2 + d_etk**2 + d_bag**2)
          
          return dist
   

    def run(self, start_id, end_id):
        if start_id not in self.graph.nodes or end_id not in self.graph.nodes:
            raise ValueError("Başlangıç veya hedef düğüm yok")

        if start_id == end_id:
            return 0.0, [start_id]

        came_from = {}
        g_score = {nid: float("inf") for nid in self.graph.nodes}
        g_score[start_id] = 0.0

        pq = []
        heapq.heappush(pq, (0.0, start_id))  

        while pq:
            current_f, current = heapq.heappop(pq)

           
            if current_f > g_score[current] + self.heuristic(current, end_id):
                continue

            if current == end_id:
                path = []
                cur = end_id
                while cur != start_id:
                    path.append(cur)
                    cur = came_from.get(cur)
                    if cur is None:
                        return float("inf"), []
                path.append(start_id)
                path.reverse()
                return g_score[end_id], path

            for neighbor in self.graph.nodes[current].neighbors:
                key = tuple(sorted((current, neighbor)))
                edge = self.graph.edges.get(key)
                if edge is None:
                    continue

                cost = float(edge.weight)  
                tentative = g_score[current] + cost

                if tentative < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    f_score = tentative + self.heuristic(neighbor, end_id)
                    heapq.heappush(pq, (f_score, neighbor))
