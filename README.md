# Passagens API

API desenvolvida em **Python** com **FastAPI** para integração e normalização de dados de viagens provenientes de diferentes companhias de transporte (Auto Viação Progresso, Rota Transportes, Gontijo e Sertão Bus), retornando um contrato único e validado independentemente da empresa de origem.

## Tecnologias

- Python 3.11+
- FastAPI
- Pydantic (validação e contrato de saída)
- Uvicorn
- Pytest + httpx (testes automatizados)

## Instalação

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
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

> **Nota (Windows):** o pacote `tzdata` está incluído no `requirements.txt` porque o Windows não vem com o banco de fusos horários IANA por padrão — sem ele, conversões de data para `America/Bahia` falham com `ZoneInfoNotFoundError`. Em Linux/Mac normalmente não é necessário, mas não custa nada tê-lo instalado.

## Execução

```bash
uvicorn main:app --reload
```

A API estará disponível em `http://localhost:8000`, com documentação interativa (Swagger) em `http://localhost:8000/docs`.

## Testes automatizados

```bash
python3 -m pytest tests/ -v
```

Os testes cobrem o caminho feliz de cada empresa suportada e todos os cenários de erro do item 7 da especificação (formato não reconhecido, chegada anterior à partida, UF inválida, preço/duração inválidos, categoria não mapeável, assentos negativos, campo obrigatório ausente e rejeição do lote inteiro quando um item é inválido).

## Endpoints

### `GET /`

Endpoint de verificação de funcionamento.

```json
{ "Viagens": "Exemplo de API de Viagens" }
```

### `POST /api/v1/viagens/normalizar`

Recebe um array JSON com viagens de diferentes companhias e devolve todas no mesmo contrato, na mesma ordem em que foram recebidas. A empresa de cada objeto é identificada automaticamente pela estrutura do payload — não é necessário (nem permitido) informar qual empresa é.

**Exemplo de requisição**:

```json
[
  {
    "codigoViagem": "PRG-2026-001",
    "cidadeOrigem": "Paulo Afonso",
    "ufOrigem": "BA",
    "cidadeDestino": "Recife",
    "ufDestino": "PE",
    "dataHoraSaida": "15/10/2026 06:30",
    "dataHoraChegada": "15/10/2026 12:50",
    "tempoEstimado": "06:20",
    "valorPassagem": "129,90",
    "tipoServico": "EXECUTIVO",
    "assentosDisponiveis": "18"
  }
]
```

**Resposta:**

```json
{
  "total": 1,
  "viagens": [
    {
      "id_viagem": "PRG-2026-001",
      "empresa": "Auto Viação Progresso",
      "origem": { "cidade": "Paulo Afonso", "uf": "BA" },
      "destino": { "cidade": "Recife", "uf": "PE" },
      "partida": "2026-10-15T06:30:00-03:00",
      "chegada": "2026-10-15T12:50:00-03:00",
      "duracao_minutos": 380,
      "preco": { "valor": 129.9, "moeda": "BRL" },
      "categoria": "executivo",
      "assentos_disponiveis": 18
    }
  ]
}
```

Note que `partida`/`chegada` já saem convertidas para **ISO 8601 com fuso horário** — mesmo quando a empresa manda a data em outro formato (como a Progresso, que usa `dd/mm/aaaa HH:MM` sem fuso).

### Tratamento de erros

Se **qualquer** objeto do array for inválido, a requisição inteira é rejeitada com **HTTP 422** e nenhum resultado parcial é retornado — nem os itens válidos que vieram antes do inválido:

```json
{
  "detail": {
    "indice": 1,
    "empresa_identificada": "Rota Transportes",
    "campo": "chegada",
    "mensagem": "A data de chegada deve ser posterior à data de saída."
  }
}
```

Quando o formato do payload não é reconhecido por nenhum adapter:

```json
{
  "detail": {
    "indice": 1,
    "empresa_identificada": null,
    "campo": null,
    "mensagem": "O formato do payload não corresponde a nenhuma companhia suportada."
  }
}
```

## Estrutura

```text
passagens-api/
├── adapters/
│   ├── adapter.py       # interface ViagemAdapter + helpers comuns
│   ├── erros.py         # ViagemInvalidaError
│   ├── progresso.py
│   ├── rota.py
│   ├── gontijo.py
│   └── sertao_bus.py
├── tests/
│   └── test_api.py
├── main.py               # endpoint + fluxo de identificação/validação
├── viagem.py              # contrato de saída (Pydantic) + regras de negócio
├── requirements.txt
└── README.md
```

## Decisões de projeto

### Padrão Adapter para identificação da companhia

Cada empresa tem uma classe que implementa a interface `ViagemAdapter`:

```python
class ViagemAdapter(ABC):
    def suporta(self, dados: dict) -> bool: ...
    def normalizar(self, dados: dict) -> dict: ...
```

O `main.py` mantém uma lista de adapters e, para cada viagem recebida, pergunta a cada um "você reconhece esse formato?" (`suporta`) até encontrar o responsável:

```python
adapter_reconhecido = next((a for a in adapters if a.suporta(dados)), None)
```

Isso evita a cadeia de `if/elif/else` por empresa proibida no item 8 da especificação: a decisão de "quem sou eu" fica encapsulada dentro de cada adapter, e o `main.py` só delega — sem saber nada sobre os campos específicos de nenhuma empresa.

Esse desenho também atende aos princípios SOLID pedidos no item 2:

- **SRP** — cada adapter cuida só da sua empresa; a validação de regras comuns fica isolada em `Viagem`.
- **OCP** — dá pra adicionar uma empresa nova sem alterar o código das existentes (só estender, nunca modificar).
- **LSP** — qualquer adapter pode substituir outro do ponto de vista do `main.py`, pois todos seguem o mesmo contrato `ViagemAdapter`.
- **ISP** — a interface tem só os dois métodos que todo adapter realmente precisa, nada supérfluo.
- **DIP** — o fluxo principal (`main.py`) depende da abstração `ViagemAdapter`, não dos detalhes de conversão de cada empresa.

### Pydantic como contrato de saída único

`viagem.py` define o modelo `Viagem` (e os submodelos `Local`/`Preco`) com **todas as regras de negócio centralizadas**: UF com 2 caracteres, categoria dentro de um conjunto fechado (`convencional`/`executivo`/`semileito`/`leito`), preço e duração positivos, assentos não-negativos, chegada posterior à partida e duração compatível com o intervalo partida→chegada.

Cada adapter só precisa converter tipos e formatos específicos da sua empresa; a validação de negócio comum a todas roda uma única vez, no modelo, em vez de ser reimplementada (ou esquecida) em cada adapter.

### Erros estruturados via exceção de domínio

`ViagemInvalidaError(campo, mensagem)` carrega exatamente as informações que o `main.py` precisa para montar o corpo de erro pedido no item 7. Ela é levantada tanto pelos adapters (erros de conversão específicos de cada empresa) quanto pelo modelo `Viagem` (erros de regra de negócio comuns), e capturada num único lugar no endpoint — sem duplicar lógica de formatação de erro em cada adapter.

Exceções não previstas (`KeyError`/`ValueError`/`TypeError`) também são capturadas como rede de segurança, evitando que um bug num adapter novo derrube a API com HTTP 500 e stacktrace exposto.

### Tolerância na checagem de duração

A comparação entre a duração informada pela empresa e a duração calculada a partir de `partida`/`chegada` usa uma tolerância de 1 minuto (`TOLERANCIA_DURACAO_MINUTOS`), para absorver arredondamentos legítimos (ex: conversão de segundos ou horas fracionadas para minutos inteiros) sem deixar de detectar inconsistências reais.

## Procedimento para adicionar uma nova companhia

Adicionar uma empresa **não exige alterar** o endpoint, o contrato de entrada, o contrato de saída, as integrações existentes, o fluxo principal de processamento nem os testes das outras empresas. As alterações ficam concentradas em três lugares:

**1. Criar o adapter da empresa** em `adapters/<empresa>.py`, implementando `ViagemAdapter`:

```python
from adapters.adapter import ViagemAdapter
from adapters.erros import ViagemInvalidaError

class NovaEmpresaAdapter(ViagemAdapter):
    EMPRESA = "Nome da Empresa"

    def suporta(self, dados: dict) -> bool:
        # verifica a presença das chaves que identificam essa empresa
        return "campo_exclusivo_da_empresa" in dados and ...

    def normalizar(self, dados: dict) -> dict:
        # usa self._campo_obrigatorio(...) para ler campos com segurança
        # e self._mapear_categoria(...) para traduzir a categoria da empresa
        return {
            "id_viagem": ...,
            "empresa": self.EMPRESA,
            "origem": {"cidade": ..., "uf": ...},
            "destino": {"cidade": ..., "uf": ...},
            "partida": ...,   # string ISO 8601
            "chegada": ...,   # string ISO 8601
            "duracao_minutos": ...,  # int
            "preco": {"valor": ..., "moeda": ...},
            "categoria": ...,
            "assentos_disponiveis": ...,
        }
```

**2. Registrar o adapter em `main.py`** (a única alteração num arquivo existente, e explicitamente permitida pelo item 9 da especificação, que fala em "registro no sistema"):

```python
from adapters.nova_empresa import NovaEmpresaAdapter
# ...
adapters = [ProgressoAdapter(), RotaAdapter(), GontijoAdapter(), SertaoBusAdapter(), NovaEmpresaAdapter()]
```

**3. Criar os testes da nova empresa** em `tests/test_<empresa>.py` (arquivo próprio, sem tocar em `tests/test_api.py`), cobrindo pelo menos o caminho feliz e os erros específicos do formato dessa empresa.

Nenhuma regra de negócio comum (UF, categoria, preço, duração, assentos, consistência de horários) precisa ser reimplementada — todas já são validadas automaticamente pelo modelo `Viagem` assim que `normalizar()` devolve o dict no formato esperado.

## Status

✅ Funcional — identificação automática, normalização, validação de regras de negócio, tratamento de erros estruturado e testes automatizados implementados para as 4 companhias suportadas.
