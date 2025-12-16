from abc import ABC, abstractmethod

class Algorithm(ABC):
    def __init__(self, graph):
        self.graph = graph

    @abstractmethod
    def run(self, *args, **kwargs):
        pass
