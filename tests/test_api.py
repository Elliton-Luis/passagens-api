from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

ENDPOINT = "/api/v1/viagens/normalizar"

def _post(payload):
    return client.post(ENDPOINT, json=payload)

def test_normaliza_progresso():
    payload = [{
        "codigoViagem": "PRG-2026-001",
        "cidadeOrigem": "Paulo Afonso", "ufOrigem": "BA",
        "cidadeDestino": "Recife", "ufDestino": "PE",
        "dataHoraSaida": "15/10/2026 06:30", "dataHoraChegada": "15/10/2026 12:50",
        "fusoHorario": "America/Bahia", "tempoEstimado": "06:20",
        "valorPassagem": "129,90", "tipoServico": "EXECUTIVO", "assentosDisponiveis": "18",
    }]
    r = _post(payload)
    assert r.status_code == 200
    viagem = r.json()["viagens"][0]
    assert viagem["empresa"] == "Auto Viação Progresso"
    assert viagem["duracao_minutos"] == 380
    assert isinstance(viagem["duracao_minutos"], int)
    assert viagem["preco"]["valor"] == 129.90
    assert viagem["categoria"] == "executivo"


def test_normaliza_rota():
    payload = [{
        "trip_id": "ROT-2026-872",
        "origem": {"municipio": "Paulo Afonso", "estado": "BA"},
        "destino": {"municipio": "Aracaju", "estado": "SE"},
        "partida_em": "2026-10-15T07:00:00-03:00", "chegada_em": "2026-10-15T12:10:00-03:00",
        "duracao_minutos": 310, "tarifa_centavos": 8990, "moeda": "BRL",
        "classe": "convencional", "vagas": 22,
    }]
    r = _post(payload)
    assert r.status_code == 200
    viagem = r.json()["viagens"][0]
    assert viagem["empresa"] == "Rota Transportes"
    assert viagem["preco"]["valor"] == 89.90


def test_normaliza_gontijo_e_converte_duracao_para_inteiro():
    payload = [{
        "serviceCode": "GON-2026-554",
        "from": {"city": "Paulo Afonso", "state": "BA"},
        "to": {"city": "Belo Horizonte", "state": "MG"},
        "departure": "2026-10-15T19:30:00Z", "arrival": "2026-10-16T12:10:00Z",
        "estimatedDurationSeconds": 60000,
        "fare": {"amount": "289.50", "currency": "BRL"},
        "serviceClass": "SEMI_SLEEPER", "availableSeats": 9,
    }]
    r = _post(payload)
    assert r.status_code == 200
    viagem = r.json()["viagens"][0]
    assert viagem["duracao_minutos"] == 1000
    assert isinstance(viagem["duracao_minutos"], int)
    assert viagem["categoria"] == "semileito"


def test_normaliza_sertao_bus_e_converte_duracao_para_inteiro():
    payload = [{
        "numero": "SER-2026-100",
        "rota": {"partida": "Paulo Afonso/BA", "chegada": "Maceió/AL"},
        "horarios": {"saida": "2026-10-16T08:00:00-03:00", "chegada": "2026-10-16T13:30:00-03:00"},
        "duracao_horas": 5.5, "preco_total": 105.90, "moeda": "BRL",
        "servico": "EXEC", "lugares_livres": 14,
    }]
    r = _post(payload)
    assert r.status_code == 200
    viagem = r.json()["viagens"][0]
    assert viagem["duracao_minutos"] == 330
    assert isinstance(viagem["duracao_minutos"], int)


def test_ordem_da_resposta_igual_a_ordem_da_requisicao():
    progresso = {
        "codigoViagem": "PRG-1", "cidadeOrigem": "A", "ufOrigem": "BA",
        "cidadeDestino": "B", "ufDestino": "PE",
        "dataHoraSaida": "15/10/2026 06:30", "dataHoraChegada": "15/10/2026 12:50",
        "tempoEstimado": "06:20", "valorPassagem": "10,00",
        "tipoServico": "EXECUTIVO", "assentosDisponiveis": "10",
    }
    rota = {
        "trip_id": "ROT-1", "origem": {"municipio": "A", "estado": "BA"},
        "destino": {"municipio": "B", "estado": "SE"},
        "partida_em": "2026-10-15T07:00:00-03:00", "chegada_em": "2026-10-15T12:10:00-03:00",
        "duracao_minutos": 310, "tarifa_centavos": 1000, "moeda": "BRL",
        "classe": "convencional", "vagas": 10,
    }
    r = _post([rota, progresso])
    assert r.status_code == 200
    empresas = [v["empresa"] for v in r.json()["viagens"]]
    assert empresas == ["Rota Transportes", "Auto Viação Progresso"]

def _rota_valida(**overrides):
    base = {
        "trip_id": "ROT-1", "origem": {"municipio": "A", "estado": "BA"},
        "destino": {"municipio": "B", "estado": "SE"},
        "partida_em": "2026-10-15T07:00:00-03:00", "chegada_em": "2026-10-15T12:10:00-03:00",
        "duracao_minutos": 310, "tarifa_centavos": 8990, "moeda": "BRL",
        "classe": "convencional", "vagas": 22,
    }
    base.update(overrides)
    return base


def test_formato_nao_reconhecido_retorna_422():
    r = _post([{"campo_qualquer": "valor"}])
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert detail["indice"] == 0
    assert detail["empresa_identificada"] is None


def test_chegada_antes_da_partida_retorna_422():
    r = _post([_rota_valida(partida_em="2026-10-15T12:00:00-03:00",
                             chegada_em="2026-10-15T07:00:00-03:00")])
    assert r.status_code == 422
    assert r.json()["detail"]["empresa_identificada"] == "Rota Transportes"


def test_uf_com_tamanho_invalido_retorna_422():
    r = _post([_rota_valida(origem={"municipio": "A", "estado": "BAH"})])
    assert r.status_code == 422
    assert r.json()["detail"]["campo"] == "uf"


def test_preco_zero_ou_negativo_retorna_422():
    r = _post([_rota_valida(tarifa_centavos=0)])
    assert r.status_code == 422
    assert r.json()["detail"]["campo"] == "preco"


def test_categoria_nao_mapeavel_retorna_422():
    r = _post([_rota_valida(classe="vip")])
    assert r.status_code == 422
    assert r.json()["detail"]["campo"] == "categoria"


def test_assentos_negativos_retorna_422():
    r = _post([_rota_valida(vagas=-1)])
    assert r.status_code == 422
    assert r.json()["detail"]["campo"] == "assentos_disponiveis"


def test_duracao_incompativel_com_horarios_retorna_422():
    r = _post([_rota_valida(duracao_minutos=9999)])
    assert r.status_code == 422
    assert r.json()["detail"]["campo"] == "duracao_minutos"


def test_campo_obrigatorio_ausente_retorna_422():
    payload = _rota_valida()
    del payload["tarifa_centavos"]
    r = _post([payload])
    assert r.status_code == 422
    assert r.json()["detail"]["empresa_identificada"] is None


def test_lote_e_rejeitado_por_inteiro_quando_um_item_e_invalido():
    valida = _rota_valida(trip_id="ROT-OK")
    invalida = _rota_valida(trip_id="ROT-RUIM", classe="vip")
    r = _post([valida, invalida])
    assert r.status_code == 422
    assert r.json()["detail"]["indice"] == 1
