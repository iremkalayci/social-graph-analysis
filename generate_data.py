import csv
import random

def generate_csv(filename, node_count):
    print(f"{filename} oluşturuluyor ({node_count} düğüm)...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Başlıklar (Senin projenin formatında)
        writer.writerow(["DugumId", "Name", "Ozellik_I", "Ozellik_II", "Ozellik_III", "Komsular", "Pos_X", "Pos_Y"])
        
        nodes = []
        for i in range(1, node_count + 1):
            # Rastgele özellikler
            name = f"User_{i}"
            akt = round(random.random(), 2)       # 0.0 - 1.0 arası
            etk = round(random.uniform(1, 100), 2) # 1 - 100 arası
            bagl = random.randint(1, 20)
            
            # Rastgele komşular (Kendisi hariç, rastgele 2-5 kişi)
            possible_neighbors = [x for x in range(1, node_count + 1) if x != i]
            num_neighbors = random.randint(2, 5)
            neighbors = random.sample(possible_neighbors, min(len(possible_neighbors), num_neighbors))
            neighbors_str = ",".join(map(str, neighbors))
            
            # Rastgele Pozisyon (Canvas için)
            pos_x = random.randint(50, 900)
            pos_y = random.randint(50, 600)
            
            writer.writerow([i, name, akt, etk, bagl, f"{neighbors_str}", pos_x, pos_y])

    print(f"✔ {filename} hazır!")

if __name__ == "__main__":
    generate_csv("kucuk_test.csv", 20)   # Küçük Ölçek
    generate_csv("orta_test.csv", 100)   # Orta Ölçek