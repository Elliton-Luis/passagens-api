from adapters.adapter import ViagemAdapter


class SertaoBusAdapter(ViagemAdapter):

    def suporta(self, dados: dict) -> bool:
        return "numero" in dados and "SER" in dados["numero"]

    def normalizar(self, dados: dict) -> dict:
        return {
            "id_viagem": dados["numero"],

            "empresa": "Sertão Bus",

            "origem": {
                "cidade": dados["rota"]["partida"].split("/")[0],
                "uf": dados["rota"]["partida"].split("/")[1],
            },

            "destino": {
                "cidade": dados["rota"]["chegada"].split("/")[0],
                "uf": dados["rota"]["chegada"].split("/")[1],
            },

            "partida": dados["horarios"]["saida"],
            "chegada": dados["horarios"]["chegada"],

            "duracao_minutos": dados["duracao_horas"] * 60,

            "preco": {
                "valor": dados["preco_total"],
                "moeda": dados["moeda"],
            },

            "categoria": "executivo",

            "assentos_disponiveis": dados["lugares_livres"],
        }