import heapq
from src.algorithms.base import Algorithm

class Dijkstra(Algorithm):
    def run(self, start_id, end_id):
        if start_id not in self.graph.nodes or end_id not in self.graph.nodes:
            raise ValueError("Başlangıç veya hedef düğüm yok")

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
                
                # KRİTİK DÜZELTME:
                # Kenar ağırlığı (Benzerlik) ne kadar yüksekse, Maliyet o kadar DÜŞÜK olmalı.
                # Bu yüzden 1/weight kullanıyoruz.
                # Örn: Benzerlik 1.0 ise Maliyet 1.0
                # Örn: Benzerlik 0.1 ise Maliyet 10.0 (Uzak)
                cost = 1.0 / edge.weight 
                
                new_dist = current_dist + cost

                if new_dist < distances[komsu]:
                    distances[komsu] = new_dist
                    previous[komsu] = current
                    heapq.heappush(pq, (new_dist, komsu))

        path = []
        cur = end_id
        while cur in previous:
            path.append(cur)
            cur = previous[cur]
        if path: # Yol bulunduysa başlangıcı ekle
            path.append(start_id)
        path.reverse()

        # Eğer yol yoksa (path boşsa ve start!=end) mesafe sonsuzdur
        if not path and start_id != end_id:
            return float("inf"), []
            
        return distances[end_id], path