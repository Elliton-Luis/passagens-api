from datetime import datetime
from zoneinfo import ZoneInfo

from adapters.adapter import ViagemAdapter
from adapters.erros import ViagemInvalidaError

FUSO_PADRAO = "America/Bahia"

CATEGORIAS = {
    "EXECUTIVO": "executivo",
    "CONVENCIONAL": "convencional",
    "SEMILEITO": "semileito",
    "LEITO": "leito",
}

def _conversor_minutos(tempo_estimado: str) -> int:
    try:
        horas, minutos = map(int, tempo_estimado.split(":"))
    except (ValueError, AttributeError):
        raise ViagemInvalidaError(
            "tempoEstimado", f"Duração estimada '{tempo_estimado}' em formato inválido (esperado HH:MM)."
        )
    return horas * 60 + minutos


def _conversor_data_hora(data_hora: str, fuso: str, campo: str) -> str:
    try:
        data = datetime.strptime(data_hora, "%d/%m/%Y %H:%M")
    except ValueError:
        raise ViagemInvalidaError(campo, f"Data '{data_hora}' em formato inválido (esperado dd/mm/aaaa HH:MM).")
    try:
        data = data.replace(tzinfo=ZoneInfo(fuso))
    except Exception:
        raise ViagemInvalidaError(campo, f"Fuso horário '{fuso}' desconhecido.")
    return data.isoformat()


class ProgressoAdapter(ViagemAdapter):

    EMPRESA = "Auto Viação Progresso"

    def suporta(self, dados: dict) -> bool:
        return (
            "codigoViagem" in dados
            and "cidadeOrigem" in dados
            and "cidadeDestino" in dados
            and "dataHoraSaida" in dados
            and "dataHoraChegada" in dados
            and "tempoEstimado" in dados
            and "valorPassagem" in dados
            and "assentosDisponiveis" in dados
        )

    def normalizar(self, dados: dict) -> dict:
        fuso = dados.get("fusoHorario", FUSO_PADRAO)

        try:
            valor = float(self._campo_obrigatorio(dados, "valorPassagem").replace(",", "."))
        except ValueError:
            raise ViagemInvalidaError("valorPassagem", f"Preço '{dados['valorPassagem']}' inválido.")

        try:
            assentos = int(self._campo_obrigatorio(dados, "assentosDisponiveis"))
        except ValueError:
            raise ViagemInvalidaError(
                "assentosDisponiveis", f"Quantidade de assentos '{dados['assentosDisponiveis']}' inválida."
            )

        return {
            "id_viagem": self._campo_obrigatorio(dados, "codigoViagem"),
            "empresa": self.EMPRESA,
            "origem": {
                "cidade": self._campo_obrigatorio(dados, "cidadeOrigem"),
                "uf": self._campo_obrigatorio(dados, "ufOrigem"),
            },
            "destino": {
                "cidade": self._campo_obrigatorio(dados, "cidadeDestino"),
                "uf": self._campo_obrigatorio(dados, "ufDestino"),
            },
            "partida": _conversor_data_hora(dados["dataHoraSaida"], fuso, "dataHoraSaida"),
            "chegada": _conversor_data_hora(dados["dataHoraChegada"], fuso, "dataHoraChegada"),
            "duracao_minutos": _conversor_minutos(dados["tempoEstimado"]),
            "preco": {"valor": valor, "moeda": "BRL"},
            "categoria": self._mapear_categoria(CATEGORIAS, dados.get("tipoServico", "").upper()),
            "assentos_disponiveis": assentos,
        }
