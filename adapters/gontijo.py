from datetime import datetime
from zoneinfo import ZoneInfo

from adapters.adapter import ViagemAdapter
from adapters.erros import ViagemInvalidaError

FUSO_PADRAO = "America/Bahia"

CATEGORIAS = {
    "SEMI_SLEEPER": "semileito",
    "SLEEPER": "leito",
    "CONVENTIONAL": "convencional",
}

def _conversor_data_hora(data_hora: str, campo: str) -> str:
    try:
        data = datetime.fromisoformat(data_hora)
    except ValueError:
        raise ViagemInvalidaError(campo, f"Data '{data_hora}' em formato ISO 8601 inválido.")
    data = data.astimezone(ZoneInfo(FUSO_PADRAO))
    return data.isoformat()


class GontijoAdapter(ViagemAdapter):

    EMPRESA = "Gontijo"

    def suporta(self, dados: dict) -> bool:
        return (
            "serviceCode" in dados
            and "from" in dados
            and "to" in dados
            and "departure" in dados
            and "arrival" in dados
            and "estimatedDurationSeconds" in dados
            and "fare" in dados
            and "availableSeats" in dados
            and "serviceClass" in dados
        )

    def normalizar(self, dados: dict) -> dict:
        origem = self._campo_obrigatorio(dados, "from")
        destino = self._campo_obrigatorio(dados, "to")
        fare = self._campo_obrigatorio(dados, "fare")

        try:
            duracao = int(round(self._campo_obrigatorio(dados, "estimatedDurationSeconds") / 60))
        except TypeError:
            raise ViagemInvalidaError(
                "estimatedDurationSeconds", f"Duração '{dados['estimatedDurationSeconds']}' inválida."
            )

        try:
            valor = float(self._campo_obrigatorio(fare, "amount"))
        except ValueError:
            raise ViagemInvalidaError("fare.amount", f"Preço '{fare['amount']}' inválido.")

        try:
            assentos = int(self._campo_obrigatorio(dados, "availableSeats"))
        except (ValueError, TypeError):
            raise ViagemInvalidaError("availableSeats", f"Assentos '{dados['availableSeats']}' inválidos.")

        return {
            "id_viagem": self._campo_obrigatorio(dados, "serviceCode"),
            "empresa": self.EMPRESA,
            "origem": {
                "cidade": self._campo_obrigatorio(origem, "city"),
                "uf": self._campo_obrigatorio(origem, "state"),
            },
            "destino": {
                "cidade": self._campo_obrigatorio(destino, "city"),
                "uf": self._campo_obrigatorio(destino, "state"),
            },
            "partida": _conversor_data_hora(dados["departure"], "departure"),
            "chegada": _conversor_data_hora(dados["arrival"], "arrival"),
            "duracao_minutos": duracao,
            "preco": {"valor": valor, "moeda": self._campo_obrigatorio(fare, "currency")},
            "categoria": self._mapear_categoria(CATEGORIAS, dados.get("serviceClass", "")),
            "assentos_disponiveis": assentos,
        }
