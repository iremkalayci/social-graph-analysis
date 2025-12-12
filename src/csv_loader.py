import csv
from node import Node

class CSVLoader:
    @staticmethod
    def load_nodes(path: str):
        nodes = []
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                node_id = int(row["DugumId"])
                akt = float(row["Ozellik_I"])
                etk = float(row["Ozellik_II"])
                bagl = int(row["Ozellik_III"])
                komsular = row["Komsular"].split(",") if row["Komsular"] else []

                n = Node(node_id, f"Node_{node_id}", akt, etk, bagl)
                n.neighbors = {int(k) for k in komsular}
                nodes.append(n)
        return nodes
