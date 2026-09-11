from adapters.adapter import ViagemAdapter


class GontijoAdapter(ViagemAdapter):

    def suporta(self, dados: dict) -> bool:
        return "serviceCode" in dados and "GON" in dados["serviceCode"]

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

            "partida": dados["departure"],
            "chegada": dados["arrival"],

            "duracao_minutos": dados["estimatedDurationSeconds"] / 60,

            "preco": {
                "valor": float(dados["fare"]["amount"]),
                "moeda": dados["fare"]["currency"],
            },

            "categoria": "semileito",

            "assentos_disponiveis": dados["availableSeats"],
        }