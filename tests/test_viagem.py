import pytest

from erros import ViagemInvalidaError
from viagem import Viagem


def _viagem_valida(**overrides):
    base = {
        "id_viagem": "T-1",
        "empresa": "Rota Transportes",
        "origem": {"cidade": "A", "uf": "BA"},
        "destino": {"cidade": "B", "uf": "SE"},
        "partida": "2026-10-15T07:00:00-03:00",
        "chegada": "2026-10-15T12:10:00-03:00",
        "duracao_minutos": 310,
        "preco": {"valor": 89.90, "moeda": "BRL"},
        "categoria": "convencional",
        "assentos_disponiveis": 22,
    }
    base.update(overrides)
    return base


def test_chegada_antes_da_partida_levanta_erro():
    with pytest.raises(ViagemInvalidaError) as excinfo:
        Viagem(**_viagem_valida(partida="2026-10-15T12:00:00-03:00",
                                chegada="2026-10-15T07:00:00-03:00"))
    assert excinfo.value.campo == "chegada"
    assert excinfo.value.mensagem == "A data de chegada deve ser posterior à data de saída."


def test_uf_com_tamanho_invalido_levanta_erro():
    with pytest.raises(ViagemInvalidaError) as excinfo:
        Viagem(**_viagem_valida(origem={"cidade": "A", "uf": "BAH"}))
    assert excinfo.value.campo == "uf"
    assert excinfo.value.mensagem == "A UF deve possuir exatamente 2 caracteres."


def test_preco_zero_ou_negativo_levanta_erro():
    with pytest.raises(ViagemInvalidaError) as excinfo:
        Viagem(**_viagem_valida(preco={"valor": 0, "moeda": "BRL"}))
    assert excinfo.value.campo == "preco"
    assert excinfo.value.mensagem == "O preço deve ser maior que zero."


def test_categoria_nao_mapeavel_levanta_erro():
    with pytest.raises(ViagemInvalidaError) as excinfo:
        Viagem(**_viagem_valida(categoria="vip"))
    assert excinfo.value.campo == "categoria"
    assert excinfo.value.mensagem == "A categoria 'vip' não pôde ser normalizada."


def test_assentos_negativos_levanta_erro():
    with pytest.raises(ViagemInvalidaError) as excinfo:
        Viagem(**_viagem_valida(assentos_disponiveis=-1))
    assert excinfo.value.campo == "assentos_disponiveis"
    assert excinfo.value.mensagem == "A quantidade de assentos não pode ser negativa."


def test_duracao_incompativel_com_horarios_levanta_erro():
    with pytest.raises(ViagemInvalidaError) as excinfo:
        Viagem(**_viagem_valida(duracao_minutos=9999))
    assert excinfo.value.campo == "duracao_minutos"
    assert excinfo.value.mensagem == "A duração informada é incompatível com os horários de partida e chegada."
