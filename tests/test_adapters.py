from adapters.gontijo import GontijoAdapter
from adapters.progresso import ProgressoAdapter
from adapters.rota import RotaAdapter
from adapters.sertao_bus import SertaoBusAdapter


def _payload_progresso(**overrides):
    base = {
        "codigoViagem": "PRG-2026-001",
        "cidadeOrigem": "Paulo Afonso", "ufOrigem": "BA",
        "cidadeDestino": "Recife", "ufDestino": "PE",
        "dataHoraSaida": "15/10/2026 06:30", "dataHoraChegada": "15/10/2026 12:50",
        "fusoHorario": "America/Bahia", "tempoEstimado": "06:20",
        "valorPassagem": "129,90", "tipoServico": "EXECUTIVO", "assentosDisponiveis": "18",
    }
    base.update(overrides)
    return base


def _payload_rota(**overrides):
    base = {
        "trip_id": "ROT-2026-872",
        "origem": {"municipio": "Paulo Afonso", "estado": "BA"},
        "destino": {"municipio": "Aracaju", "estado": "SE"},
        "partida_em": "2026-10-15T07:00:00-03:00", "chegada_em": "2026-10-15T12:10:00-03:00",
        "duracao_minutos": 310, "tarifa_centavos": 8990, "moeda": "BRL",
        "classe": "convencional", "vagas": 22,
    }
    base.update(overrides)
    return base


def _payload_gontijo(**overrides):
    base = {
        "serviceCode": "GON-2026-554",
        "from": {"city": "Paulo Afonso", "state": "BA"},
        "to": {"city": "Belo Horizonte", "state": "MG"},
        "departure": "2026-10-15T19:30:00Z", "arrival": "2026-10-16T12:10:00Z",
        "estimatedDurationSeconds": 60000,
        "fare": {"amount": "289.50", "currency": "BRL"},
        "serviceClass": "SEMI_SLEEPER", "availableSeats": 9,
    }
    base.update(overrides)
    return base


def _payload_sertao_bus(**overrides):
    base = {
        "numero": "SER-2026-100",
        "rota": {"partida": "Paulo Afonso/BA", "chegada": "Maceió/AL"},
        "horarios": {"saida": "2026-10-16T08:00:00-03:00", "chegada": "2026-10-16T13:30:00-03:00"},
        "duracao_horas": 5.5, "preco_total": 105.90, "moeda": "BRL",
        "servico": "EXEC", "lugares_livres": 14,
    }
    base.update(overrides)
    return base


def test_progresso_normalizar_converte_campos():
    normalizado = ProgressoAdapter().normalizar(_payload_progresso())
    assert normalizado["empresa"] == "Auto Viação Progresso"
    assert normalizado["partida"] == "2026-10-15T06:30:00-03:00"
    assert normalizado["chegada"] == "2026-10-15T12:50:00-03:00"
    assert normalizado["duracao_minutos"] == 380
    assert isinstance(normalizado["duracao_minutos"], int)
    assert normalizado["preco"]["valor"] == 129.90
    assert isinstance(normalizado["preco"]["valor"], float)
    assert normalizado["assentos_disponiveis"] == 18
    assert isinstance(normalizado["assentos_disponiveis"], int)
    assert normalizado["categoria"] == "executivo"


def test_rota_normalizar_converte_campos():
    normalizado = RotaAdapter().normalizar(_payload_rota())
    assert normalizado["empresa"] == "Rota Transportes"
    assert normalizado["partida"] == "2026-10-15T07:00:00-03:00"
    assert normalizado["chegada"] == "2026-10-15T12:10:00-03:00"
    assert normalizado["duracao_minutos"] == 310
    assert isinstance(normalizado["duracao_minutos"], int)
    assert normalizado["preco"]["valor"] == 89.90
    assert isinstance(normalizado["preco"]["valor"], float)
    assert normalizado["assentos_disponiveis"] == 22
    assert isinstance(normalizado["assentos_disponiveis"], int)
    assert normalizado["categoria"] == "convencional"


def test_gontijo_normalizar_converte_campos():
    normalizado = GontijoAdapter().normalizar(_payload_gontijo())
    assert normalizado["empresa"] == "Gontijo"
    assert normalizado["partida"] == "2026-10-15T16:30:00-03:00"
    assert normalizado["chegada"] == "2026-10-16T09:10:00-03:00"
    assert normalizado["duracao_minutos"] == 1000
    assert isinstance(normalizado["duracao_minutos"], int)
    assert normalizado["preco"]["valor"] == 289.50
    assert isinstance(normalizado["preco"]["valor"], float)
    assert normalizado["assentos_disponiveis"] == 9
    assert isinstance(normalizado["assentos_disponiveis"], int)
    assert normalizado["categoria"] == "semileito"


def test_sertao_bus_normalizar_converte_campos():
    normalizado = SertaoBusAdapter().normalizar(_payload_sertao_bus())
    assert normalizado["empresa"] == "Sertão Bus"
    assert normalizado["origem"] == {"cidade": "Paulo Afonso", "uf": "BA"}
    assert normalizado["destino"] == {"cidade": "Maceió", "uf": "AL"}
    assert normalizado["partida"] == "2026-10-16T08:00:00-03:00"
    assert normalizado["chegada"] == "2026-10-16T13:30:00-03:00"
    assert normalizado["duracao_minutos"] == 330
    assert isinstance(normalizado["duracao_minutos"], int)
    assert normalizado["preco"]["valor"] == 105.90
    assert isinstance(normalizado["preco"]["valor"], float)
    assert normalizado["assentos_disponiveis"] == 14
    assert isinstance(normalizado["assentos_disponiveis"], int)
    assert normalizado["categoria"] == "executivo"


def test_progresso_suporta_proprio_payload_e_rejeita_outro():
    adapter = ProgressoAdapter()
    assert adapter.suporta(_payload_progresso()) is True
    assert adapter.suporta(_payload_rota()) is False


def test_rota_suporta_proprio_payload_e_rejeita_outro():
    adapter = RotaAdapter()
    assert adapter.suporta(_payload_rota()) is True
    assert adapter.suporta(_payload_gontijo()) is False


def test_gontijo_suporta_proprio_payload_e_rejeita_outro():
    adapter = GontijoAdapter()
    assert adapter.suporta(_payload_gontijo()) is True
    assert adapter.suporta(_payload_sertao_bus()) is False


def test_sertao_bus_suporta_proprio_payload_e_rejeita_outro():
    adapter = SertaoBusAdapter()
    assert adapter.suporta(_payload_sertao_bus()) is True
    assert adapter.suporta(_payload_progresso()) is False
