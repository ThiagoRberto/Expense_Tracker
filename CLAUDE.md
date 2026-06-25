# Expense Tracker — CLAUDE.md

## Visão Geral do Projeto

Website de gerenciamento financeiro pessoal com as seguintes funcionalidades planejadas:
- Divisão de despesas por categorias
- Balanço de receitas versus gastos
- Controle de compras parceladas com projeção de faturas
- Definição de metas de teto orçamentário com alertas de consumo

**Objetivo acadêmico:** Demonstrar regras de negócio complexas com cobertura de testes adequada (unit, integration, e2e, MC/DC, structural testing). O projeto não deve ser um CRUD simples.

## Stack

- **Backend:** Python + FastAPI
- **ORM:** SQLAlchemy 2.x
- **Banco de dados:** SQLite (`financial.db`, gerado automaticamente ao subir o servidor)
- **Validação:** Pydantic v2
- **Servidor:** Uvicorn
- **Testes:** pytest + pytest-cov + httpx

## Estrutura Atual

```
app/
├── main.py                        # Entrypoint FastAPI, endpoints definidos aqui
├── requirements.txt               # Dependências de produção e de teste
├── pytest.ini                     # Configuração do pytest (testpaths = tests)
├── database/
│   └── database.py                # Engine SQLite + SessionLocal + Base
├── models/                        # Modelos ORM (tabelas do banco)
│   ├── __init__.py                # Expõe User, Bill, Expense, Income, Investment
│   ├── user.py
│   ├── bill.py
│   ├── expense.py
│   ├── income.py
│   └── investment.py
├── schemas/                       # Schemas Pydantic (validação de entrada/saída)
│   ├── user.py
│   ├── bill.py
│   ├── expense.py
│   ├── income.py
│   └── investment.py
├── services/
│   └── financial_service.py      # Regras de negócio puras (IO-Free)
└── tests/
    ├── unit/                      # Testes unitários das regras de negócio
    │   ├── test_calculate_balance.py
    │   ├── test_budget_alert.py
    │   ├── test_project_installments.py
    │   ├── test_net_worth.py
    │   └── test_summarize_finances.py
    └── integration/               # Testes dos endpoints HTTP
        ├── conftest.py            # Fixtures: banco in-memory + TestClient
        └── test_users_endpoints.py
```

## O que foi desenvolvido

### Modelos (SQLAlchemy)
- `User`: id, name, password, budget_ceiling + relacionamentos one-to-many com as 4 entidades
- `Bill`: id, name, bill_value, user_id
- `Expense`: id, name, expense_value, installment, user_id
- `Income`: id, name, income_value, user_id
- `Investment`: id, name, value_invested, dividends, user_id

### Schemas (Pydantic v2)
- Padrão `<Entity>Base` / `<Entity>Create` / `<Entity>` para cada entidade
- `UserCreate` aceita listas de cada entidade (zero ou mais por usuário)
- Todos usam `ConfigDict(from_attributes=True)`

### Endpoints
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/users/` | Cria usuário com listas de entidades associadas |
| GET | `/users/` | Lista todos os usuários com relacionamentos |
| GET | `/users/{user_id}` | Busca usuário por ID (404 se não encontrado) |

### Camada de Serviço (`services/financial_service.py`)
Funções puras (sem I/O) que contêm as regras de negócio:

| Função | Regra |
|--------|-------|
| `calculate_balance` | Receitas − parcela mensal de cada despesa − contas fixas |
| `check_budget_alert` | Retorna `OK` / `WARNING` (>80%) / `EXCEEDED` (≥100%) do teto |
| `project_installments` | Projeta faturas futuras com virada de ano e correção de arredondamento |
| `calculate_net_worth` | Saldo + capital investido + dividendos acumulados |
| `summarize_finances` | Consolida todos os indicadores; inclui `budget_status` se ceiling informado |

### Testes (82 testes, 100% passando)

**Unit tests (IO-Free):**
- `test_calculate_balance` — 13 casos: múltiplas receitas/despesas/contas, déficit, saldo zero, installment=0, valores negativos
- `test_budget_alert` — 16 casos: **MC/DC completo** para as duas condições (`ratio >= 1.0` e `ratio > 0.8`), boundary analysis nas fronteiras exatas (80% e 100%)
- `test_project_installments` — 17 casos: virada de ano, 13 parcelas cruzando dois anos, correção de arredondamento na última parcela, todos os inputs inválidos
- `test_net_worth` — 9 casos: saldo negativo, múltiplos investimentos, valores grandes
- `test_summarize_finances` — 6 casos: todos os status de budget, ceiling ausente

**Integration tests (IO-dependent):**
- `test_users_endpoints` — 21 casos: criação com múltiplas entidades, listas vazias, persistência de dados, listagem, busca por ID, 404

## Como rodar

```bash
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Servidor
uvicorn main:app --reload
# Acesse http://localhost:8000/docs

# Testes
pytest
pytest -v                                          # detalhado
pytest --cov=services --cov-report=term-missing    # com cobertura
```
