from adapters.adapter import ViagemAdapter


class SertaoBusAdapter(ViagemAdapter):

    categorias = {
        "EXEC": "executivo"
    }

    def suporta(self, dados: dict) -> bool:
        return "numero" in dados and "rota" in dados and "horarios" in dados and "duracao_horas" in dados and "preco_total" in dados and "moeda" in dados and "lugares_livres" in dados

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

            "categoria": self.categorias[dados['servico']],

            "assentos_disponiveis": dados["lugares_livres"],
        }