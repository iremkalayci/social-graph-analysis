from node import Node
from edge import Edge
import math
from csv_loader import CSVLoader

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
if __name__=="__main__":
    print("graf test ediliyor")
    g=Graph()
    n1=Node(1,"user1",0.8,12,3)
    n2=Node(2,"user2",0.4,5,2)
    g.add_node(n1)
    g.add_node(n2)
    g.add_edge(1,2)

    print("dugumler:",g.nodes)
    print("kenarlar",{k:e.weight for k,e in g.edges.items()})
    print("test bitti")
    print("csv testing")
    nodes=CSVLoader.load_nodes("test.csv")
    g=Graph()
    for n in nodes:
        g.add_node(n)
    for n in nodes:
        for komsu in n.neighbors:
            g.add_edge(n.id,komsu)
    print("toplam dugum sayisi",len(g.nodes))
    print("toplam kenar sayisi:",len(g.edges))
    print("bitti")
    print("\nBFS Testi:",g.bfs(1))
    print("DFS Testi:",g.dfs(1))
          