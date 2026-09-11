from abc import ABC, abstractmethod

class ViagemAdapter(ABC):
    @abstractmethod
    def suporta(self, dados: dict) -> bool:
        pass

    @abstractmethod
    def normalizar(self, dados: dict) -> dict:
        pass