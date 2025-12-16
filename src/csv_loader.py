import csv
import os
from src.node import Node

class CSVLoader:
    @staticmethod
    def load_nodes(path: str):
        nodes = []
        positions = {}
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Dosya bulunamadı: {path}")

        with open(path, "r", encoding="utf-8-sig") as f: # utf-8-sig Excel karakter sorununu çözer
            # Dosyanın ilk satırını oku ve ayırıcıyı (delimiter) tahmin et
            sample = f.read(1024)
            f.seek(0) # Başa dön
            
            try:
                dialect = csv.Sniffer().sniff(sample)
                delimiter = dialect.delimiter
            except:
                delimiter = ',' # Tahmin edemezse varsayılan virgül
            
            # Tahmin edilen ayırıcı ile oku
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Sütun isimlerindeki boşlukları temizle (Örn: " Name " -> "Name")
            reader.fieldnames = [field.strip() for field in reader.fieldnames]

            for row in reader:
                # Düğüm ID zorunlu
                if "DugumId" not in row:
                    continue
                    
                node_id = int(row["DugumId"])
                
                # İsim kontrolü (Hem 'Name' hem 'İsim' sütununa bakar)
                name = row.get("Name") or row.get("Isim") or f"Node_{node_id}"
                
                # Özellikler (Hata verirse 0.0 ata)
                try:
                    akt = float(row.get("Ozellik_I", 0))
                    etk = float(row.get("Ozellik_II", 0))
                    bagl = int(row.get("Ozellik_III", 0))
                except ValueError:
                    akt, etk, bagl = 0.0, 0.0, 0
                
                # Komşular
                komsular_str = row.get("Komsular", "")
                komsular = []
                if komsular_str and komsular_str.lower() != "none":
                    # Tırnak ve boşluk temizliği
                    clean_str = komsular_str.replace('"', '').replace("'", "")
                    komsular = [k.strip() for k in clean_str.split(',') if k.strip().isdigit()]

                n = Node(node_id, name, akt, etk, bagl)
                
                for k in komsular:
                    n.neighbors.add(int(k))
                        
                nodes.append(n)

                # Pozisyon
                if "Pos_X" in row and "Pos_Y" in row:
                    try:
                        positions[node_id] = (int(row["Pos_X"]), int(row["Pos_Y"]))
                    except:
                        positions[node_id] = None

        return nodes, positions