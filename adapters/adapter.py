from abc import ABC, abstractmethod
from adapters.erros import ViagemInvalidaError

class ViagemAdapter(ABC):
    EMPRESA: str = ""

    @abstractmethod
    def suporta(self, dados: dict) -> bool:
        ...

    @abstractmethod
    def normalizar(self, dados: dict) -> dict:
        ...

    def _campo_obrigatorio(self, dados: dict, chave: str):
        try:
            return dados[chave]
        except KeyError:
            raise ViagemInvalidaError(chave, f"O campo obrigatório '{chave}' não foi informado.")

    def _mapear_categoria(self, mapa: dict, valor_original: str) -> str:
        try:
            return mapa[valor_original]
        except KeyError:
            raise ViagemInvalidaError(
                "categoria", f"A categoria '{valor_original}' não pôde ser normalizada."
            )
