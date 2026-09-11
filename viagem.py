from dataclasses import dataclass

@dataclass
class Viagem:
    id_viagem: str
    empresa: str
    origem: dict
    destino: dict
    partida: str
    chegada: str
    duracao_minutos: int
    preco: dict
    categoria: str
    assentos_disponiveis: int