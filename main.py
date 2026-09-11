import fastapi

from adapters.progresso import ProgressoAdapter

app = fastapi.FastAPI()

@app.get("/")
def get_example():
    return {"Viagens": "Exemplo de API de Viagens"}


@app.post("/api/v1/viagens/normalizar")
def normalizar_viagens(viagem: dict):
    return ProgressoAdapter().normalizar(viagem)