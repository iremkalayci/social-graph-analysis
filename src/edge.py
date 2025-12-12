class Edge:
    def __init__(self, a_id: int, b_id: int, weight: float = None):
        self.a = a_id
        self.b = b_id
        self.weight = weight  # WeightCalculator ile doldurulacak
