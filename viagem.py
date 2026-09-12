from datetime import datetime
from enum import Enum

from pydantic import BaseModel, field_validator, model_validator

from adapters.erros import ViagemInvalidaError

TOLERANCIA_DURACAO_MINUTOS = 1


class Categoria(str, Enum):
    CONVENCIONAL = "convencional"
    EXECUTIVO = "executivo"
    SEMILEITO = "semileito"
    LEITO = "leito"


class Local(BaseModel):
    cidade: str
    uf: str

    @field_validator("uf")
    @classmethod
    def uf_deve_ter_dois_caracteres(cls, v: str) -> str:
        if len(v) != 2:
            raise ViagemInvalidaError("uf", "A UF deve possuir exatamente 2 caracteres.")
        return v.upper()


class Preco(BaseModel):
    valor: float
    moeda: str

    @field_validator("valor")
    @classmethod
    def valor_deve_ser_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ViagemInvalidaError("preco", "O preço deve ser maior que zero.")
        return v


class Viagem(BaseModel):
    id_viagem: str
    empresa: str
    origem: Local
    destino: Local
    partida: datetime
    chegada: datetime
    duracao_minutos: int
    preco: Preco
    categoria: Categoria
    assentos_disponiveis: int

    @field_validator("categoria", mode="before")
    @classmethod
    def categoria_deve_ser_conhecida(cls, v):
        valores_validos = {c.value for c in Categoria}
        if isinstance(v, str) and v not in valores_validos:
            raise ViagemInvalidaError(
                "categoria", f"A categoria '{v}' não pôde ser normalizada."
            )
        return v

    @field_validator("duracao_minutos")
    @classmethod
    def duracao_deve_ser_positiva(cls, v: int) -> int:
        if v <= 0:
            raise ViagemInvalidaError("duracao_minutos", "A duração deve ser maior que zero.")
        return v

    @field_validator("assentos_disponiveis")
    @classmethod
    def assentos_nao_pode_ser_negativo(cls, v: int) -> int:
        if v < 0:
            raise ViagemInvalidaError(
                "assentos_disponiveis", "A quantidade de assentos não pode ser negativa."
            )
        return v

    @model_validator(mode="after")
    def validar_consistencia_de_horarios(self) -> "Viagem":
        if self.chegada <= self.partida:
            raise ViagemInvalidaError(
                "chegada", "A data de chegada deve ser posterior à data de saída."
            )

        duracao_calculada = (self.chegada - self.partida).total_seconds() / 60
        if abs(duracao_calculada - self.duracao_minutos) > TOLERANCIA_DURACAO_MINUTOS:
            raise ViagemInvalidaError(
                "duracao_minutos",
                "A duração informada é incompatível com os horários de partida e chegada.",
            )
        return self