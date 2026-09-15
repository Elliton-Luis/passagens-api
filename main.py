import fastapi
from fastapi import HTTPException

from adapters.progresso import ProgressoAdapter
from adapters.rota import RotaAdapter
from adapters.gontijo import GontijoAdapter
from adapters.sertao_bus import SertaoBusAdapter
from erros import ViagemInvalidaError
from viagem import Viagem

app = fastapi.FastAPI()

adapters = [ProgressoAdapter(), RotaAdapter(), GontijoAdapter(), SertaoBusAdapter()]

@app.get("/")
def get_example():
    return {"Viagens": "Exemplo de API de Viagens"}

def _erro(indice: int, empresa: str | None, campo: str | None, mensagem: str) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "indice": indice,
            "empresa_identificada": empresa,
            "campo": campo,
            "mensagem": mensagem,
        },
    )


@app.post("/api/v1/viagens/normalizar")
def normalizar_viagens(viagens: list[dict]):
    resultado = []

    for indice, dados in enumerate(viagens):
        adapter_reconhecido = next((a for a in adapters if a.suporta(dados)), None)

        if adapter_reconhecido is None:
            raise _erro(
                indice,
                None,
                None,
                "O formato do payload não corresponde a nenhuma companhia suportada.",
            )

        try:
            normalizado = adapter_reconhecido.normalizar(dados)
            viagem_validada = Viagem(**normalizado)
        except ViagemInvalidaError as e:
            raise _erro(indice, adapter_reconhecido.EMPRESA, e.campo, e.mensagem)
        except (KeyError, ValueError, TypeError) as e:
            raise _erro(
                indice,
                adapter_reconhecido.EMPRESA,
                None,
                f"Não foi possível converter os dados da viagem: {e}",
            )

        resultado.append(viagem_validada.model_dump(mode="json"))

    return {"total": len(resultado), "viagens": resultado}