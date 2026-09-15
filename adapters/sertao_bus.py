from adapters.adapter import ViagemAdapter
from erros import ViagemInvalidaError

CATEGORIAS = {
    "EXEC": "executivo",
    "CONV": "convencional",
    "SEMI": "semileito",
    "LEITO": "leito",
}

def _dividir_localidade(texto: str, campo: str) -> dict:
    partes = texto.split("/")
    if len(partes) != 2:
        raise ViagemInvalidaError(campo, f"Localidade '{texto}' deveria estar no formato 'Cidade/UF'.")
    cidade, uf = partes
    return {"cidade": cidade, "uf": uf}


class SertaoBusAdapter(ViagemAdapter):

    EMPRESA = "Sertão Bus"

    def suporta(self, dados: dict) -> bool:
        return (
            "numero" in dados
            and "rota" in dados
            and "horarios" in dados
            and "duracao_horas" in dados
            and "preco_total" in dados
            and "moeda" in dados
            and "lugares_livres" in dados
        )

    def normalizar(self, dados: dict) -> dict:
        rota = self._campo_obrigatorio(dados, "rota")
        horarios = self._campo_obrigatorio(dados, "horarios")

        try:
            duracao = int(round(self._campo_obrigatorio(dados, "duracao_horas") * 60))
        except TypeError:
            raise ViagemInvalidaError("duracao_horas", f"Duração '{dados['duracao_horas']}' inválida.")

        try:
            preco = float(self._campo_obrigatorio(dados, "preco_total"))
        except (ValueError, TypeError):
            raise ViagemInvalidaError("preco_total", f"Preço '{dados['preco_total']}' inválido.")

        try:
            lugares = int(self._campo_obrigatorio(dados, "lugares_livres"))
        except (ValueError, TypeError):
            raise ViagemInvalidaError("lugares_livres", f"Lugares '{dados['lugares_livres']}' inválidos.")

        return {
            "id_viagem": self._campo_obrigatorio(dados, "numero"),
            "empresa": self.EMPRESA,
            "origem": _dividir_localidade(self._campo_obrigatorio(rota, "partida"), "rota.partida"),
            "destino": _dividir_localidade(self._campo_obrigatorio(rota, "chegada"), "rota.chegada"),
            "partida": self._campo_obrigatorio(horarios, "saida"),
            "chegada": self._campo_obrigatorio(horarios, "chegada"),
            "duracao_minutos": duracao,
            "preco": {"valor": preco, "moeda": self._campo_obrigatorio(dados, "moeda")},
            "categoria": self._mapear_categoria(CATEGORIAS, dados.get("servico", "")),
            "assentos_disponiveis": lugares,
        }
