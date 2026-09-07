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

A API estará disponível localmente em:

`http://localhost:8000`

## Endpoint

A API será responsável por receber dados de viagens de diferentes companhias e convertê-los para um contrato único e padronizado.

### GET /

Endpoint inicial utilizado para verificar o funcionamento da aplicação.

**Resposta:**

```json
{
  "Viagens": "Exemplo de API de Viagens"
}
```

## Status

🚧 Em desenvolvimento.
