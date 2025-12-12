# Social Graph Analysis

This project is a Python implementation of a weighted graph system designed to simulate and analyze social connections. It builds a network where users are treated as nodes and their relationships are weighted edges.

The main goal was to implement and compare Breadth First Search and Depth First Search algorithms on a dataset that mimics real world social interactions.

## How It Works

Instead of simple "connected,not connected" logic, this project calculates a "weight" for every connection. The weight represents the strength of the relationship between two people based on three metrics:
-Activity levels
-Interaction frequency
-Number of mutual connections

A lower weight value means a stronger relationship (closer distance). The system reads user data from a CSV file, builds the graph structure, and then runs traversal algorithms to explore the network.

## Project Structure

The source code is located in the `src` folder:

* **`graph.py`**: Contains the main `Graph` class. This handles adding nodes, creating edges, and running the BFS and DFS logic.
* **`node.py`**: Defines the `Node` object representing a user with attributes like ID and activity scores.
* **`edge.py`**: Defines the connection between two nodes and holds the calculated weight.
* **`csv_loader.py`**: A helper script to parse the input `.csv` file and convert raw data into Node objects.
* **`test.csv`**: Sample data used to test the graph construction.

## Algorithms Used

* **BFS:** Used to explore the immediate neighbors of a user first, expanding layer by layer. This is useful for finding closer connections.
* **DFS:** Used to explore a path as deep as possible before backtracking.

## Usage

you need Python 3 installed to run the scripts.

1.  Clone this repository.
2.  Navigate to the project folder.
3.  Run the graph script to see the traversal outputs.

---

# Türkçe Açıklama

Bu proje sosyal ağlardaki kullanıcı etkilesimlerini simüle etmek ve analiz etmek amacıyla Python ile geliştirdigim bir ağırlıklı çizge uygulamasıdır.

Kullanıcıları birer düğüm, aralarındaki ilişkileri ise ağırlıklı kenar olarak modelleyen bu sistemde, BFS ve Depth-First Search DFS algoritmalarının davranışlarını incelemek hedeflenmiştir.

## Çalışma Mantığı

Standart "arkadaş mı, değil mi?" 0-1 mantığının ötesine geçerek, bu projede her bağlantının bir kuvveti bulunur. İki kişi arasındaki bu bağın gücü şu üç kritere göre hesaplanır:
-Aktiflik seviyeleri
-Etkileşim sıklığı
-Ortak bağlantı sayısı

İlişki ne kadar güçlüyse, "mesafe" değeri o kadar düşük çıkar. Sistem, `.csv` formatındaki ham veriyi okuyup bu kurallara göre bir ağ yapısı oluşturur ve üzerinde gezinme algoritmalarını çalıştırır.

## Proje Yapısı

Kaynak kodları `src` klasörü altındadır:

* **`graph.py`**: Ana `Graph` sınıfını barındırır. Düğüm ekleme, bağ kurma ve BFS/DFS işlemleri burada döner.
* **`node.py`**: Kullanıcı objesini ID, aktiflik puanı vb.tanımlayan sınıftır.
* **`edge.py`**: İki düğüm arasındaki bağlantıyı ve hesaplanan ağırlığı tutar.
* **`csv_loader.py`**: Dışarıdan gelen `.csv` dosyasını parse edip Node objelerine çeviren yardımcı modüldür.
* **`test.csv`**: Ağı test etmek için kullanılan örnek veri setidir.

## Kullanılan Algoritmalar

* **BFS (Genişlik Öncelikli Arama):** Bir kullanıcının doğrudan arkadaşlarını ve onların çevresini katman katman taramak için kullanılır. Yakın ilişkileri bulmada etkilidir.
* **DFS (Derinlik Öncelikli Arama):** Bir ilişki zincirini takip ederek gidebildiği en uç noktaya kadar ilerler, sonra geri döner.

## Kurulum ve Çalıştırma

Kodları çalıştırmak için Python 3 gereklidir. Projeyi indirdikten sonra ana dizinde terminali açıp şu komutu girmeniz yeterli:

```bash
python src/graph.py