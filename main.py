import fastapi

app = fastapi.FastAPI()

@app.get("/")
def get_example():
    return {"Viagens": "Exemplo de API de Viagens"}


@app.post("/api/v1/viagens/normalizar")
def normalizar_progresso(viagem: dict):
    return {
        "id_viagem": viagem.get("codigoViagem"),
        "empresa": "Auto Viação Progresso",
        "origem": {
            "cidade": viagem.get("cidadeOrigem"),
            "uf": viagem.get("ufOrigem"),
        },
        "destino": {
            "cidade": viagem.get("cidadeDestino"),
            "uf": viagem.get("ufDestino"),
        },
        "partida": viagem.get("dataHoraSaida"),
        "chegada": viagem.get("dataHoraChegada"),
        "duracao_minutos": 380, #Puramente para testes
        "preco": {
            "valor": 129.90,
            "moeda": "BRL",
        },
        "categoria": "executivo",
        "assentos_disponiveis": 18,
    }