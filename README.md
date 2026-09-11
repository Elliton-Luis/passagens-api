# Passagens API

API desenvolvida em **Python** com **FastAPI** para integração e normalização de dados de viagens provenientes de diferentes companhias de transporte.

## Tecnologias

* Python
* FastAPI
* Uvicorn

## Execução

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>

cd passagens-api
```

### 2. Crie o ambiente virtual

```bash
python3 -m venv .venv
```

### 3. Ative o ambiente virtual

```bash
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute a API

```bash
uvicorn main:app --reload
```

A API estará disponível em:

`http://localhost:8000`

A documentação interativa pode ser acessada em:

`http://localhost:8000/docs`

## Endpoint

### GET `/`

Endpoint inicial utilizado para verificar o funcionamento da aplicação.

**Resposta:**

```json
{
  "Viagens": "Exemplo de API de Viagens"
}
```

### POST `/api/v1/viagens/normalizar`

Recebe os dados de uma viagem e os converte para um contrato único e padronizado.

A identificação da companhia é realizada automaticamente pelo adapter correspondente.

**Exemplo de requisição:**

```json
{
  "codigoViagem": "PRG-2026-001",
  "cidadeOrigem": "Paulo Afonso",
  "ufOrigem": "BA",
  "cidadeDestino": "Recife",
  "ufDestino": "PE",
  "dataHoraSaida": "15/10/2026 06:30",
  "dataHoraChegada": "15/10/2026 12:50"
}
```

**Resposta:**

```json
{
  "id_viagem": "PRG-2026-001",
  "empresa": "Auto Viação Progresso",
  "origem": {
    "cidade": "Paulo Afonso",
    "uf": "BA"
  },
  "destino": {
    "cidade": "Recife",
    "uf": "PE"
  },
  "partida": "15/10/2026 06:30",
  "chegada": "15/10/2026 12:50",
  "duracao_minutos": 380,
  "preco": {
    "valor": 129.90,
    "moeda": "BRL"
  },
  "categoria": "executivo",
  "assentos_disponiveis": 18
}
```

## Estrutura

Os adapters são responsáveis por reconhecer e normalizar os diferentes formatos de dados das companhias.

```text
passagens-api/
├── adapters/
│   ├── adapter.py
│   └── gontijo.py
│   └── progresso.py
│   └── rota.py
│   └── sertao_bus.py
├── main.py
├── viagem.py
├── requirements.txt
└── README.md
```

O `ViagemAdapter` define o contrato que os adapters devem seguir, enquanto cada implementação concreta é responsável pelas particularidades de sua respectiva companhia.

## Status

🚧 Em desenvolvimento.
