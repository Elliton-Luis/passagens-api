from adapters.adapter import ViagemAdapter
from datetime import datetime
from zoneinfo import ZoneInfo

def conversor_data_hora(data_hora: str) -> str:
    data = datetime.fromisoformat(data_hora)
    data = data.astimezone(ZoneInfo("America/Bahia"))
    return data.isoformat()

class GontijoAdapter(ViagemAdapter):

    categorias = {
        "SEMI_SLEEPER": "semileito",
        "SLEEPER": "leito",
    }

    def suporta(self, dados: dict) -> bool:
        return "serviceCode" in dados and "from" in dados and "to" in dados and "departure" in dados and "arrival" in dados and "estimatedDurationSeconds" in dados and "fare" in dados and "availableSeats" in dados and "serviceClass" in dados

    def normalizar(self, dados: dict) -> dict:
        return {
            "id_viagem": dados["serviceCode"],

            "empresa": "Gontijo",

            "origem": {
                "cidade": dados["from"]["city"],
                "uf": dados["from"]["state"],
            },

            "destino": {
                "cidade": dados["to"]["city"],
                "uf": dados["to"]["state"],
            },

            "partida": conversor_data_hora(dados["departure"]),
            "chegada": conversor_data_hora(dados["arrival"]),

            "duracao_minutos": dados["estimatedDurationSeconds"] / 60,

            "preco": {
                "valor": float(dados["fare"]["amount"]),
                "moeda": dados["fare"]["currency"],
            },

            "categoria": self.categorias[dados['serviceClass']],

            "assentos_disponiveis": dados["availableSeats"],
        }