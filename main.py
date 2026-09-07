import fastapi

app = fastapi.FastAPI()

@app.get("/")
async def read_root():
    return {"Viagens": "Exemplo de API de Viagens"}