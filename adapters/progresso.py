from adapters.adapter import ViagemAdapter 
from datetime import datetime
from zoneinfo import ZoneInfo

def conversor_minutos(tempo_estimado: str) -> int:
    horas, minutos = map(int, tempo_estimado.split(':'))
    return horas * 60 + minutos

def conversor_data_hora(data_hora: str) -> str:
    data = datetime.strptime(data_hora, "%d/%m/%Y %H:%M")
    data = data.replace(tzinfo=ZoneInfo("America/Bahia"))
    return data.isoformat()

class ProgressoAdapter(ViagemAdapter):
    
    def suporta(self, dados: dict) -> bool:
     return "codigoViagem" in dados and "cidadeOrigem" in dados and "cidadeDestino" in dados and "dataHoraSaida" in dados and "dataHoraChegada" in dados and "tempoEstimado" in dados and "valorPassagem" in dados and "assentosDisponiveis" in dados
     
    def normalizar(self,dados: dict) -> dict:
        return {
        "id_viagem": dados["codigoViagem"],
        "empresa": "Auto Viação Progresso",
        "origem": {
            "cidade": dados["cidadeOrigem"],
            "uf": dados["ufOrigem"],
        },
        "destino": {
            "cidade": dados["cidadeDestino"],
            "uf": dados["ufDestino"],
        },
        "partida": conversor_data_hora(dados["dataHoraSaida"]),
        "chegada": conversor_data_hora(dados["dataHoraChegada"]),
        "duracao_minutos": conversor_minutos(dados['tempoEstimado']),
        "preco": {
            "valor": float(dados["valorPassagem"].replace(",",".")),
            "moeda": "BRL",
        },
        "categoria": "executivo",
        "assentos_disponiveis": dados["assentosDisponiveis"],}

