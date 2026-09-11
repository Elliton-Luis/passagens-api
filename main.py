import fastapi

from adapters.progresso import ProgressoAdapter
from adapters.rota import RotaAdapter
from adapters.gontijo import GontijoAdapter
from adapters.sertao_bus import SertaoBusAdapter

app = fastapi.FastAPI()

adapters = [ProgressoAdapter(), RotaAdapter(), GontijoAdapter(), SertaoBusAdapter()]

@app.get("/")
def get_example():
    return {"Viagens": "Exemplo de API de Viagens"}


@app.post("/api/v1/viagens/normalizar")
def normalizar_viagens(viagens: list[dict]):
    resultado = []
    for viagem in viagens:
        for adapter in adapters:
            if adapter.suporta(viagem):
                resultado.append(adapter.normalizar(viagem))
                break
    return resultado