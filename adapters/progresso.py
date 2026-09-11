from adapters.adapter import ViagemAdapter 

class ProgressoAdapter(ViagemAdapter):
    def suporta(self, dados: dict) -> bool:
     return "codigoViagem" in dados
     
    def normalizar(self,dados: dict) -> dict:
        return {
        "id_viagem": dados["codigoViagem"],
        "empresa": "Auto Viação Progresso",
        "origem": {
            "cidade": dados["cidadeOrigem"],
            "uf": dados["ufOrigem"],
        },
        "destino": {
            "cidade": dados["cidadeDestino"],
            "uf": dados["ufDestino"],
        },
        "partida": dados["dataHoraSaida"],
        "chegada": dados["dataHoraChegada"],
        "duracao_minutos": 380, #Puramente para testes
        "preco": {
            "valor": 129.90,
            "moeda": "BRL",
        },
        "categoria": "executivo",
        "assentos_disponiveis": 18}