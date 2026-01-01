from src.node import Node
from src.edge import Edge
import math
from src.algorithms.bfs import BFS
from src.algorithms.dfs import DFS
from src.algorithms.dijkstra import Dijkstra
from src.algorithms.astar import AStar
from src.algorithms.coloring import WelshPowell

class WeightCalculator:
    @staticmethod
    def calc(n1: Node, n2: Node) -> float:
      
        d_aktif = n1.aktiflik - n2.aktiflik
        d_etk = n1.etkilesim - n2.etkilesim
        d_bag = n1.baglanti_sayisi - n2.baglanti_sayisi
        
        
        distance= math.sqrt(d_aktif**2 + d_etk**2 + d_bag**2)
        weight=1.0/(1.0+distance)
        return weight
class Graph:
    def __init__(self):
        self.nodes = {}
        self.edges = {}

    def add_node(self, node: Node):
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} zaten var!")
        self.nodes[node.id] = node

    def add_edge(self, a_id: int, b_id: int):
        if a_id == b_id:
            raise ValueError("Self-loop (kendine bağlantı) yasak.")
        
        key = tuple(sorted((a_id, b_id)))
        
        if key in self.edges:
            return 
            
        if a_id not in self.nodes or b_id not in self.nodes:
            raise KeyError("Node bulunamadı.")
            
        w = WeightCalculator.calc(self.nodes[a_id], self.nodes[b_id])
        e = Edge(a_id, b_id, w)
        
        self.edges[key] = e
        
        self.nodes[a_id].neighbors.add(b_id)
        self.nodes[b_id].neighbors.add(a_id)
   

    def remove_node(self, node_id: int):
   
        if node_id not in self.nodes:
            raise ValueError("Düğüm bulunamadı.")
        
        edges_to_remove = []
        for key, edge in self.edges.items():
            if edge.a == node_id or edge.b == node_id:
                edges_to_remove.append(key)
        
        for key in edges_to_remove:
            del self.edges[key]

        for other_node in self.nodes.values():
            if node_id in other_node.neighbors:
                other_node.neighbors.remove(node_id)

        del self.nodes[node_id]

    def remove_edge(self, a_id: int, b_id: int):
        """İki düğüm arasındaki bağlantıyı siler."""
        key = tuple(sorted((a_id, b_id)))
        if key not in self.edges:
            raise ValueError("Bağlantı yok.")
        
        del self.edges[key]
        
        if a_id in self.nodes and b_id in self.nodes[a_id].neighbors:
            self.nodes[a_id].neighbors.remove(b_id)
        if b_id in self.nodes and a_id in self.nodes[b_id].neighbors:
            self.nodes[b_id].neighbors.remove(a_id)

    def update_node(self, node_id: int, name: str, akt: float, etk: float, bagl: int):
        """Düğüm bilgilerini günceller."""
        if node_id not in self.nodes:
            raise ValueError("Düğüm bulunamadı.")
        
        node = self.nodes[node_id]
        node.name = name
        node.aktiflik = akt
        node.etkilesim = etk
        node.baglanti_sayisi = bagl
    
    def run_bfs(self, start_id: int):
        algo = BFS(self)
        return algo.run(start_id)

    def run_dfs(self, start_id: int):
        algo = DFS(self)
        return algo.run(start_id)

    def run_dijkstra(self, start_id: int, end_id: int):
        algo = Dijkstra(self)
        return algo.run(start_id, end_id)

    def run_astar(self, start_id: int, end_id: int):
        algo = AStar(self)
        return algo.run(start_id, end_id)

    def color_graph(self):
        algo = WelshPowell(self)
        return algo.color()

    def max_weight_edge(self):
        if not self.edges: return None
        return max(self.edges.values(), key=lambda e: e.weight)

    def min_weight_edge(self):
        if not self.edges: return None
        return min(self.edges.values(), key=lambda e: e.weight)
    
    def connected_components(self):
        visited = set()
        components = []
        for node_id in self.nodes:
           if node_id not in visited:
                comp = self.run_bfs(node_id)
                components.append(comp)
                visited.update(comp)  
        return components