# Expense Tracker — CLAUDE.md

## Visão Geral do Projeto

Website de gerenciamento financeiro pessoal com as seguintes funcionalidades:
- Balanço de receitas versus gastos
- Controle de compras parceladas com projeção de faturas futuras
- Divisão de despesas por categorias com alertas de teto orçamentário por categoria
- Cálculo de patrimônio líquido

**Objetivo acadêmico:** Demonstrar regras de negócio complexas com cobertura de testes adequada. O projeto não é um CRUD simples — toda lógica de negócio vive em funções puras IO-Free na camada de serviço.

---

## Glossário

### Termos do domínio financeiro

| Termo (código) | Significado |
|----------------|-------------|
| `income` / `incomes` | **Receita(s)** — dinheiro que entra: salário, renda extra, etc. |
| `expense` / `expenses` | **Despesa(s)** — gasto ou compra realizada pelo usuário |
| `bill` / `bills` | **Conta(s) fixa(s)** — cobranças recorrentes como aluguel, água, luz |
| `installment` / `installments` | **Parcela(s)** — divisão de uma compra em pagamentos mensais (ex: 12x) |
| `balance` | **Saldo** — diferença entre receitas e gastos do mês |
| `budget` / `budget_ceiling` / `ceiling` | **Teto orçamentário** — limite máximo de gasto definido pelo usuário |
| `category budget` / `category_budget` | **Teto por categoria** — limite de gasto definido para uma categoria específica (ex: "alimentação: R$ 800") |
| `net_worth` | **Patrimônio líquido** — soma do saldo com todos os investimentos e dividendos |
| `investment` / `investments` | **Investimento(s)** — capital aplicado (poupança, ações, etc.) |
| `dividends` | **Dividendos** — rendimentos gerados pelos investimentos |
| `summary` | **Resumo financeiro** — consolidação de todos os indicadores do usuário |

### Termos técnicos de software

| Termo | Significado |
|-------|-------------|
| `ORM` | **Mapeamento objeto-relacional** (Object-Relational Mapping) — camada que converte objetos Python em linhas de banco de dados automaticamente. Aqui usamos SQLAlchemy. |
| `schema` | **Esquema de validação** — estrutura Pydantic que define e valida os dados recebidos e enviados pela API |
| `endpoint` | **Rota da API** — URL que o cliente acessa para interagir com o sistema (ex: `GET /users/1/summary`) |
| `router` | **Módulo de rotas** — arquivo que agrupa endpoints relacionados (ex: `routers/expenses.py` agrupa tudo de despesas) |
| `dataclass` | **Classe de dados** — estrutura Python simples para agrupar campos relacionados sem lógica extra |
| `IO-Free` | **Sem entrada/saída** — funções que não acessam banco de dados, rede ou arquivos; recebem e retornam apenas dados puros, o que as torna fáceis de testar |
| `CRUD` | **Criar, Ler, Atualizar, Deletar** (Create, Read, Update, Delete) — operações básicas de banco de dados |
| `mock` | **Objeto simulado** — substituto falso criado nos testes para isolar dependências externas (banco, API, etc.) |
| `fixture` | **Dado de suporte** — estado ou objeto preparado antes de um teste rodar (ex: um usuário já criado no banco) |
| `MC/DC` | **Cobertura de condição/decisão modificada** (Modified Condition/Decision Coverage) — técnica de teste que exige verificar cada condição lógica de forma independente |
| `boundary analysis` | **Análise de fronteiras** — técnica que testa os valores exatos nos limites de uma condição (ex: 80% e 100% do teto) |
| `PK` | **Chave primária** (Primary Key) — identificador único de um registro no banco (campo `id`) |
| `FK` | **Chave estrangeira** (Foreign Key) — campo que referencia o `id` de outra tabela (ex: `user_id` em `Expense`) |
| `nullable` | **Aceita nulo** — campo que pode ficar vazio/sem valor |
| `cascade` | **Cascata** — operações que se propagam automaticamente para registros filhos (ex: deletar usuário apaga suas despesas) |
| `in-memory` | **Em memória** — banco de dados que vive apenas na RAM durante os testes, sem criar arquivo em disco |
| `StaticPool` | **Pool estático** — configuração do SQLAlchemy que força todas as conexões a compartilhar o mesmo banco SQLite em memória (necessário para os testes de integração funcionarem) |

---

## Stack

| Componente | Tecnologia |
|------------|------------|
| Backend | Python + FastAPI |
| ORM (mapeamento objeto-relacional) | SQLAlchemy 2.x |
| Banco de dados | SQLite (`financial.db`, gerado automaticamente) |
| Validação de schemas | Pydantic v2 |
| Servidor | Uvicorn |
| Testes | pytest + pytest-cov + httpx |

### Limitação conhecida — valores monetários em `Float`

Todos os campos monetários (`expense_value`, `bill_value`, `income_value`, `ceiling`, `budget_ceiling`, etc.) usam `float`. Ponto flutuante binário não representa frações decimais com exatidão (ex.: `0.1 + 0.2 != 0.3`), por isso a camada de serviço arredonda os resultados em 2 casas (`round(..., 2)`). Para um sistema financeiro de produção, o tipo correto seria `Decimal` (ou centavos em `Integer`), que elimina o erro de arredondamento. Optou-se por `float` neste projeto acadêmico pela simplicidade; a estratégia de arredondamento mantém os resultados consistentes para os casos testados.

---

## Estrutura de Arquivos

```
app/
├── main.py                        # Entrypoint: cria app, tabelas, inclui routers
├── requirements.txt               # Dependências de produção e de teste
├── pytest.ini                     # testpaths = tests
├── dependencies.py                # get_user_or_404 — helper compartilhado entre routers
├── database/
│   └── database.py                # Engine SQLite, SessionLocal, Base, get_db()
├── models/                        # Modelos ORM — mapeiam as tabelas do banco
│   ├── __init__.py
│   ├── user.py
│   ├── bill.py                    # Contas fixas
│   ├── expense.py                 # Despesas (com categoria e parcelas)
│   ├── income.py                  # Receitas
│   ├── investment.py              # Investimentos
│   └── category_budget.py        # Tetos orçamentários por categoria
├── schemas/                       # Schemas Pydantic — validação de entrada/saída
│   ├── user.py
│   ├── bill.py
│   ├── expense.py
│   ├── income.py
│   ├── investment.py
│   ├── summary.py                 # Resposta do resumo financeiro
│   ├── category_budget.py        # Teto por categoria
│   ├── category_alert.py         # Resposta dos alertas por categoria
│   └── installment.py            # Resposta da projeção de parcelas
├── routers/                       # Um arquivo por grupo de rotas (endpoints)
│   ├── users.py
│   ├── expenses.py
│   ├── bills.py
│   ├── incomes.py
│   ├── investments.py
│   └── category_budgets.py
├── services/
│   ├── financial_service.py       # Regras de negócio puras (IO-Free)
│   └── CLAUDE.md                  # Documentação detalhada da camada de serviço
└── tests/
    ├── unit/                      # Testes das funções puras (sem banco)
    │   ├── test_calculate_balance.py       (13 testes)
    │   ├── test_budget_alert.py            (16 testes — MC/DC completo)
    │   ├── test_project_installments.py    (19 testes)
    │   ├── test_net_worth.py               (9 testes)
    │   ├── test_summarize_finances.py      (6 testes)
    │   └── test_category_alerts.py         (19 testes)
    └── integration/               # Testes dos endpoints HTTP (banco in-memory)
        ├── conftest.py            # Fixtures: banco in-memory com StaticPool + TestClient
        ├── test_users_endpoints.py         (19 testes)
        ├── test_entity_endpoints.py        (25 testes)
        ├── test_summary_endpoint.py        (8 testes)
        ├── test_category_endpoints.py      (14 testes)
        └── test_installments_endpoint.py   (9 testes)
```

**Total: 157 testes, 100% passando.**

---

## Modelos (SQLAlchemy)

### `User`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer PK (chave primária) | |
| `name` | String | |
| `password` | String | |
| `budget_ceiling` | Float (nullable — aceita nulo) | Teto orçamentário global |

Relacionamentos um-para-muitos com: `bills` (contas fixas), `expenses` (despesas), `incomes` (receitas), `investments` (investimentos), `category_budgets` (tetos por categoria). Todos com `cascade="all, delete-orphan"` (deleção em cascata).

### `Bill` — Conta fixa
`id`, `name`, `bill_value` (Float), `user_id` FK (chave estrangeira)

### `Expense` — Despesa
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `id` | Integer PK | | |
| `name` | String | | Nome da despesa |
| `category` | String | `"geral"` | Categoria (ex: "alimentação") |
| `expense_value` | Float | | Valor total da compra |
| `installment` | Integer | `1` | Número de parcelas |
| `start_month` | Integer | mês atual | Mês da primeira parcela |
| `start_year` | Integer | ano atual | Ano da primeira parcela |
| `user_id` | FK | | |

`start_month` e `start_year` definem quando começa a primeira parcela — necessários para a projeção de faturas.

### `Income` — Receita
`id`, `name`, `income_value` (Float), `user_id` FK

### `Investment` — Investimento
`id`, `name`, `value_invested` (Float), `dividends` (dividendos, Float), `user_id` FK

### `CategoryBudget` — Teto orçamentário por categoria
`id`, `category` (String), `ceiling` (teto, Float), `user_id` FK

Possui `UniqueConstraint("user_id", "category")` — cada usuário só pode ter um teto por categoria. Tentar criar um teto duplicado retorna **409 Conflict**.

---

## Schemas (Pydantic v2)

Padrão `<Entidade>Base` → `<Entidade>Create` → `<Entidade>` para cada entidade. Todos usam `ConfigDict(from_attributes=True)` para serializar a partir de objetos ORM.

Schemas de resposta especiais:
- `FinancialSummary` — resposta do endpoint `/summary` (resumo financeiro)
- `CategoryAlertsResponse` + `CategoryAlertItem` — resposta dos alertas por categoria
- `InstallmentsResponse` + `ExpenseProjection` + `InstallmentEntrySchema` — resposta da projeção de parcelas

---

## Endpoints (Rotas da API)

### Usuários
| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/users` | Cria usuário (aceita listas de contas/despesas/receitas/investimentos inline) |
| `GET` | `/users` | Lista todos os usuários |
| `GET` | `/users/{user_id}` | Busca usuário por ID (retorna 404 se não encontrado) |

### Resumo financeiro
| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/users/{user_id}/summary` | Retorna saldo (`balance`), patrimônio líquido (`net_worth`), total de receitas, total de gastos e status do teto orçamentário (`budget_status`) — se o usuário tiver teto definido |

### Alertas por categoria (teto orçamentário)
| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/users/{user_id}/category-budgets` | Define teto orçamentário para uma categoria |
| `GET` | `/users/{user_id}/category-budgets` | Lista todos os tetos cadastrados |
| `GET` | `/users/{user_id}/category-alerts` | Retorna `OK` / `WARNING` / `EXCEEDED` por categoria |

### Projeção de parcelas
| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/users/{user_id}/installments` | Projeta todas as faturas futuras de todas as despesas parceladas do usuário |

### Entidades individuais
| Método | Rota |
|--------|------|
| `POST` / `GET` | `/users/{user_id}/expenses` (despesas) |
| `POST` / `GET` | `/users/{user_id}/bills` (contas fixas) |
| `POST` / `GET` | `/users/{user_id}/incomes` (receitas) |
| `POST` / `GET` | `/users/{user_id}/investments` (investimentos) |

Todos retornam 404 se o usuário não existir.

---

## Camada de Serviço (`services/financial_service.py`)

Todas as funções são **puras (IO-Free)**: sem acesso a banco, sem estado global, sem chamadas externas. Isso as torna diretamente testáveis sem necessidade de mocks (objetos simulados).

### Dataclasses (classes de dados) de entrada

| Dataclass | Campos |
|-----------|--------|
| `IncomeData` | `income_value: float` (valor da receita) |
| `ExpenseData` | `expense_value: float`, `installment: int = 1` (parcelas), `category: str = "geral"` |
| `BillData` | `bill_value: float` (valor da conta fixa) |
| `InvestmentData` | `value_invested: float`, `dividends: float = 0.0` (dividendos) |
| `CategoryBudgetData` | `category: str`, `ceiling: float` (teto) |
| `InstallmentEntry` | `installment_number: int`, `month: int`, `year: int`, `amount: float` |

`BudgetStatus = Literal["OK", "WARNING", "EXCEEDED"]`

### Funções

#### `calculate_balance(incomes, expenses, bills) -> float`
```
saldo = Σ receitas − Σ (expense_value / max(installment, 1)) − Σ contas_fixas
```
Cada despesa parcelada contribui apenas com sua fração mensal. Levanta `ValueError` para valores negativos.

#### `check_budget_alert(category_total, budget_ceiling) -> BudgetStatus`
```
ratio = gasto_na_categoria / teto_orçamentário
ratio >= 1.0  →  "EXCEEDED"  (teto ultrapassado)
ratio >  0.8  →  "WARNING"   (acima de 80% do teto)
caso contrário →  "OK"
```
Base das coberturas MC/DC (cobertura de condição/decisão modificada) nos testes. Levanta `ValueError` se `budget_ceiling <= 0` ou `category_total < 0`.

#### `project_installments(expense_value, installments, start_month, start_year) -> list[InstallmentEntry]`
Distribui o valor total em `installments` parcelas mensais iguais (arredondadas em 2 casas). A última parcela absorve o erro de arredondamento, garantindo que `Σ parcelas == expense_value`. Suporta virada de ano (dezembro → janeiro do ano seguinte).

#### `calculate_net_worth(investments, balance) -> float`
```
patrimônio líquido = saldo + Σ (capital_investido + dividendos)
```
Saldo negativo (déficit) reduz o patrimônio.

#### `summarize_finances(incomes, expenses, bills, investments, budget_ceiling) -> dict`
Compõe `calculate_balance`, `calculate_net_worth` e `check_budget_alert` em um único dicionário. `budget_status` só aparece se `budget_ceiling` (teto orçamentário) for informado.

#### `calculate_category_totals(expenses) -> dict[str, float]`
Agrupa o custo mensal por categoria. Cada despesa contribui com `expense_value / max(installment, 1)`.

#### `check_all_category_alerts(category_totals, category_budgets) -> dict[str, BudgetStatus]`
Aplica `check_budget_alert` para cada categoria que possui teto definido. Categorias sem despesas são tratadas como gasto zero. Levanta `ValueError` se qualquer `ceiling` (teto) for `<= 0`.

---

## Estratégia de Testes

### Testes unitários (IO-Free — sem banco de dados)

| Arquivo | Testes | Técnica de cobertura |
|---------|--------|----------------------|
| `test_calculate_balance` | 13 | Combinações de entradas, boundary (análise de fronteiras) no saldo zero e déficit |
| `test_budget_alert` | 16 | **MC/DC completo** para `ratio >= 1.0` e `ratio > 0.8`, boundary analysis nos limites exatos de 80% e 100% |
| `test_project_installments` | 19 | Virada de ano, 13 parcelas cruzando dois anos, correção de arredondamento, todos os inputs inválidos |
| `test_net_worth` | 9 | Saldo negativo, múltiplos investimentos, valores grandes |
| `test_summarize_finances` | 6 | Todos os status de teto, teto ausente |
| `test_category_alerts` | 19 | Categorias sem despesas, múltiplos status simultâneos, boundary 80% e 100%, teto inválido |

### Testes de integração (banco SQLite in-memory)

Configurados em `tests/integration/conftest.py` com `StaticPool` (pool estático — garante que todas as conexões compartilham o mesmo banco em memória). Usa fixtures para criar usuário antes de cada teste.

| Arquivo | Testes | O que cobre |
|---------|--------|-------------|
| `test_users_endpoints` | 19 | CRUD de usuários, criação com entidades inline, 404 |
| `test_entity_endpoints` | 25 | POST/GET de contas, despesas, receitas, investimentos — persistência, 404 |
| `test_summary_endpoint` | 8 | Resumo financeiro via HTTP, com e sem teto orçamentário |
| `test_category_endpoints` | 14 | CRUD de tetos por categoria, alertas OK/WARNING/EXCEEDED, parcelas contribuindo fração mensal |
| `test_installments_endpoint` | 9 | Projeção de parcelas, virada de ano, correção de arredondamento, múltiplas despesas, 404 |

---

## Como rodar

```bash
cd app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Servidor de desenvolvimento
uvicorn main:app --reload
# Documentação interativa: http://localhost:8000/docs

# Testes
pytest
pytest -v                                        # saída detalhada
pytest --cov=services --cov-report=term-missing  # cobertura da camada de serviço
```

> **Atenção a mudanças de schema:** `Base.metadata.create_all` apenas **cria** tabelas que ainda não existem — não altera tabelas já criadas. Ao mudar um modelo (ex.: adicionar uma coluna ou a `UniqueConstraint` de `CategoryBudget`), apague o `financial.db` existente para que ele seja recriado com o schema novo. O banco em memória dos testes nasce sempre do schema atual, então os testes não são afetados. (Num projeto de produção, isso seria resolvido com migrations, ex.: Alembic.)
