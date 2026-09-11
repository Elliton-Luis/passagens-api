from adapters.adapter import ViagemAdapter


class RotaAdapter(ViagemAdapter):

    def suporta(self, dados: dict) -> bool:
        return "trip_id" in dados and "ROT" in dados["trip_id"]

    def normalizar(self, dados: dict) -> dict:
        return {
            "id_viagem": dados["trip_id"],

            "empresa": "Rota Transportes",

            "origem": {
                "cidade": dados["origem"]["municipio"],
                "uf": dados["origem"]["estado"],
            },

            "destino": {
                "cidade": dados["destino"]["municipio"],
                "uf": dados["destino"]["estado"],
            },

            "partida": dados["partida_em"],
            "chegada": dados["chegada_em"],

            "duracao_minutos": dados["duracao_minutos"],

            "preco": {
                "valor": dados["tarifa_centavos"] / 100,
                "moeda": dados["moeda"],
            },

            "categoria": "convencional",

            "assentos_disponiveis": dados["vagas"],
        }