from adapters.adapter import ViagemAdapter
from adapters.erros import ViagemInvalidaError

class RotaAdapter(ViagemAdapter):

    EMPRESA = "Rota Transportes"

    def suporta(self, dados: dict) -> bool:
        return (
            "trip_id" in dados
            and "origem" in dados
            and "destino" in dados
            and "partida_em" in dados
            and "chegada_em" in dados
            and "duracao_minutos" in dados
            and "tarifa_centavos" in dados
            and "moeda" in dados
            and "vagas" in dados
        )

    def normalizar(self, dados: dict) -> dict:
        try:
            duracao = int(self._campo_obrigatorio(dados, "duracao_minutos"))
        except (ValueError, TypeError):
            raise ViagemInvalidaError("duracao_minutos", f"Duração '{dados['duracao_minutos']}' inválida.")

        try:
            tarifa = self._campo_obrigatorio(dados, "tarifa_centavos") / 100
        except TypeError:
            raise ViagemInvalidaError("tarifa_centavos", f"Tarifa '{dados['tarifa_centavos']}' inválida.")

        try:
            vagas = int(self._campo_obrigatorio(dados, "vagas"))
        except (ValueError, TypeError):
            raise ViagemInvalidaError("vagas", f"Quantidade de vagas '{dados['vagas']}' inválida.")

        origem = self._campo_obrigatorio(dados, "origem")
        destino = self._campo_obrigatorio(dados, "destino")

        return {
            "id_viagem": self._campo_obrigatorio(dados, "trip_id"),
            "empresa": self.EMPRESA,
            "origem": {
                "cidade": self._campo_obrigatorio(origem, "municipio"),
                "uf": self._campo_obrigatorio(origem, "estado"),
            },
            "destino": {
                "cidade": self._campo_obrigatorio(destino, "municipio"),
                "uf": self._campo_obrigatorio(destino, "estado"),
            },
            "partida": self._campo_obrigatorio(dados, "partida_em"),
            "chegada": self._campo_obrigatorio(dados, "chegada_em"),
            "duracao_minutos": duracao,
            "preco": {"valor": tarifa, "moeda": self._campo_obrigatorio(dados, "moeda")},
            "categoria": self._campo_obrigatorio(dados, "classe"),
            "assentos_disponiveis": vagas,
        }
