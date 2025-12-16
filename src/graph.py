from src.node import Node
from src.edge import Edge
import math
from src.csv_loader import CSVLoader
from src.algorithms.bfs import BFS
from src.algorithms.dfs import DFS
from src.algorithms.dijkstra import Dijkstra
from src.algorithms.astar import AStar
from src.algorithms.coloring import WelshPowell





class WeightCalculator:
    @staticmethod
    def calc(n1:Node,n2:Node)->float:
        d_aktif=n1.aktiflik-n2.aktiflik
        d_etk=n1.etkilesim-n2.etkilesim
        d_bag=n1.baglanti_sayisi-n2.baglanti_sayisi
        agirlik=1+math.sqrt(d_aktif**2+d_etk**2+d_bag**2)
        return 1.0/agirlik
class Graph:
    def __init__(self):
        self.nodes={}
        self.edges={}

    def add_node(self,node:Node):
        if node.id in self.nodes:
            raise ValueError("ayni node da id ztn var")
        self.nodes[node.id]=node #aynı id yoksa ekleme yap

    def add_edge(self,a_id:int,b_id:int):
        if a_id==b_id:
            raise ValueError("self-loop engellendi")
        key=tuple(sorted((a_id,b_id)))
        if key in self.edges:
            return
        if a_id not in self.nodes or b_id not in self.nodes:
            raise KeyError("node bulunamadi")
        w=WeightCalculator.calc(self.nodes[a_id],self.nodes[b_id])
        e=Edge(a_id,b_id,w)
        self.edges[key]=e
        self.nodes[a_id].neighbors.add(b_id)
        self.nodes[b_id].neighbors.add(a_id)

    def bfs(self,start_id:int): #genislik oncelikli arama
        if start_id not in self.nodes:
            raise ValueError("baslangic dugum yok")
        visited=set()
        queue=[start_id] 
        while queue: #is bitene kadar devam
            current=queue.pop(0)    #kuyrugun ilk elemanini al
            if current not in visited:
                visited.add(current) #islenmemisse , isledik diyerek kaydet.
                for komsu in self.nodes[current].neighbors: #komsuları siraya ekle, daha once ziyaret edilmemisse
                    if komsu not in visited:
                        queue.append(komsu)
        return visited
    
    def dfs(self,start_id:int): #depth first search
        if start_id not in self.nodes:
            raise ValueError("baslangic dugumu")       
        visited=set()
        def explore(n):
            visited.add(n)
            for komsu in self.nodes[n].neighbors:
                if komsu not in visited:
                    explore(komsu) #recursive
        explore(start_id)
        return visited  
    def max_weight_edge(self):
        if not self.edges:
            return None
        return max(self.edges.values(),key=lambda e:e.weight)
    def min_weight_edge(self):
        if not self.edges:
            return None
        return min(self.edges.values(),key=lambda e:e.weight)

        
       
    def avarage_degree(self):
        if not self.nodes:
            return 0.0
        toplam=0
        for node in self.nodes.values(): #dictionary nin degerlerini alir;dongu de graf icindeki kullanicilari tek tek gezer.
            toplam+=len(node.neighbors)   
        return toplam/len(self.nodes) 
         #derece/kisi sayisi
        #self.nodes → agdaki herkesin tutuldugu ana yer
        # neighbors →o kisinin baglı olduğu kişiler
        # for node in self.nodes.values() - her kullanıcıyı gez
        # len(node.neighbors) - komsu sayısını al
        # toplam += ... - topla
        # toplam / len(self.nodes) - ort bul
    def connected_components(self):
        visited = set()
        components = []

        for node_id in self.nodes:
           if node_id not in visited:
                comp = self.bfs(node_id)
                components.append(comp)
                visited |= comp  # birleşim
        return components 
    def run_bfs(self, start_id: int):
        algo = BFS(self)
        return algo.run(start_id)

    def run_dfs(self, start_id: int):
        algo = DFS(self)
        return algo.run(start_id)
    def run_dijkstra(self,start_id:int,end_id:int):
        algo=Dijkstra(self)
        return algo.run(start_id, end_id)
    def run_astar(self, start_id: int, end_id: int):
        algo = AStar(self)
        return algo.run(start_id, end_id)
    def color_graph(self):
        algo = WelshPowell(self)
        return algo.color()


        
    
if __name__ == "__main__":
    print("graf test ediliyor")

    g = Graph()
    n1 = Node(1, "user1", 0.8, 12, 3)
    n2 = Node(2, "user2", 0.4, 5, 2)

    g.add_node(n1)
    g.add_node(n2)
    g.add_edge(1, 2)

    print("dugumler:", g.nodes)
    print("kenarlar:", {k: e.weight for k, e in g.edges.items()})
    print("test bitti")

    print("csv testing")
    nodes = CSVLoader.load_nodes("test.csv")
    g = Graph()

    for n in nodes:
        g.add_node(n)

    for n in nodes:
        for komsu in n.neighbors:
            g.add_edge(n.id, komsu)

    print("toplam dugum sayisi:", len(g.nodes))
    print("toplam kenar sayisi:", len(g.edges))
    print("bitti")

    print("BFS Testi:", g.run_bfs(1))
    print("DFS Testi:", g.run_dfs(1))

    mx = g.max_weight_edge()
    mn = g.min_weight_edge()
    print("en guclu baglanti:", mx.a, "-", mx.b, "->", mx.weight)
    print("en zayif baglanti:", mn.a, "-", mn.b, "->", mn.weight)

    print("\nConnected Components:")
    for idx, comp in enumerate(g.connected_components(), start=1):
        print(f"Component {idx}: {sorted(comp)}")

    dist, path = g.run_dijkstra(1, 3)
    print("\nDijkstra Testi:")
    print("Mesafe:", dist)
    print("Yol:", path)

    dist, path = g.run_astar(1, 3)
    print("\nA* Testi:")
    print("Mesafe:", dist)
    print("Yol:", path)

    print("\nGraph Coloring (Welsh–Powell):")
    colors = g.color_graph()
    for node_id, color in colors.items():
        print(f"Node {node_id} -> Color {color}")
