from abc import ABC, abstractmethod
from typing import Any

class Algorithm(ABC):
    def __init__(self, graph):
        self.graph = graph

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        Her algoritma kendi türüne göre çıktı döndürür:
        - Yol bulma (Dijkstra, A*): (total_cost: float, path: list)
        - Gezinme (BFS, DFS): order: list
        - Boyama (WelshPowell): color_map: dict
        """
        raise NotImplementedError
