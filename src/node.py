class Node:
    def __init__(self, node_id: int, name: str, akt: float, etk: float, bagl_say: int):
        self.id = node_id
        self.name = name
        self.aktiflik = float(akt)
        self.etkilesim = float(etk)
        self.baglanti_sayisi = int(bagl_say)
        self.neighbors = set()  # bu kullanicinin kimlerle baglantisi varsa id lerini burada tut., sette tutma sebebim kontrol O(1) hizinda yapiliyor.

    def to_dict(self): #csv kaydederken kullaniyoruz, node u dictionary haline ceviriyor.
        return {
            "id": self.id,
            "name": self.name,
            "aktiflik": self.aktiflik,
            "etkilesim": self.etkilesim,
            "baglanti_sayisi": self.baglanti_sayisi,
            "neighbors": list(self.neighbors)
        }
