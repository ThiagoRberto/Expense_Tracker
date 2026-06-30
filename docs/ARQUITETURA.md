# Arquitetura — Expense Tracker

Documento visual da arquitetura. Todos os diagramas usam **nomes legíveis nos nós**
(sem letras soltas tipo `C`/`B`), pra você não precisar voltar pra cima toda hora pra
lembrar o que cada caixinha significa.

> Os blocos abaixo são [Mermaid](https://mermaid.js.org). O VSCode renderiza com a
> extensão *Markdown Preview Mermaid Support*; o GitHub renderiza nativamente.

---

## 1. Visão em camadas (o caminho de uma requisição)

```mermaid
flowchart TD
    Navegador["🌐 Navegador — React + Vite (porta 5173)"]
    ProxyVite["Proxy /api do Vite<br/>reescreve /api/... → /...<br/>encaminha para localhost:8000"]
    FastAPI["FastAPI / Uvicorn (porta 8000)"]
    Routers["Routers<br/>(um arquivo por grupo de rotas)"]
    Servicos["Camada de Serviço<br/>financial_service.py<br/>(funções puras, IO-Free)"]
    Modelos["Modelos ORM (SQLAlchemy)"]
    Banco[("SQLite — financial.db")]

    Navegador -->|"fetch('/api/...')"| ProxyVite
    ProxyVite -->|HTTP| FastAPI
    FastAPI --> Routers
    Routers -->|"regras de negócio"| Servicos
    Routers -->|"ler / gravar dados"| Modelos
    Modelos --> Banco

    classDef front fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef infra fill:#fef3c7,stroke:#d97706,color:#7c2d12;
    classDef back fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef data fill:#ede9fe,stroke:#7c3aed,color:#4c1d95;
    class Navegador front;
    class ProxyVite,FastAPI infra;
    class Routers,Servicos,Modelos back;
    class Banco data;
```

**Como ler:** o frontend nunca fala `localhost:8000` direto. Ele chama caminhos
relativos `/api/...` (ver `frontend/src/api/client.ts`, `BASE_URL = '/api'`). O proxy do
Vite (`frontend/vite.config.ts`) tira o prefixo `/api` e repassa pro backend. Por isso em
produção basta servir os dois sob o mesmo domínio — o código do frontend não muda.

---

## 2. Mapa completo: cada página → cada chamada → cada endpoint

Cada página do frontend usa um *módulo de API* (`frontend/src/api/*.ts`), que chama o
`apiClient`, que vira uma requisição HTTP num router do backend.

```mermaid
flowchart LR
    subgraph Paginas["Páginas (React)"]
        SelecionarUsuario["SelectUserPage"]
        Dashboard["DashboardPage"]
        Despesas["ExpensesPage"]
        ContasFixas["BillsPage"]
        Receitas["IncomesPage"]
        Investimentos["InvestmentsPage"]
        TetosCategoria["CategoryBudgetsPage"]
        Parcelas["InstallmentsPage"]
        FaturasMensais["MonthlyInvoicesPage"]
    end

    subgraph Endpoints["Endpoints (FastAPI)"]
        direction TB
        ep_users_get["GET /users"]
        ep_users_post["POST /users"]
        ep_summary["GET /users/{id}/summary"]
        ep_expenses["GET + POST /users/{id}/expenses"]
        ep_bills["GET + POST /users/{id}/bills"]
        ep_incomes["GET + POST /users/{id}/incomes"]
        ep_invest["GET + POST /users/{id}/investments"]
        ep_catbud["GET + POST /users/{id}/category-budgets"]
        ep_catalert["GET /users/{id}/category-alerts"]
        ep_inst["GET /users/{id}/installments"]
        ep_invoices["GET /users/{id}/monthly-invoices?months_ahead=N"]
    end

    SelecionarUsuario -->|"usersApi.list()"| ep_users_get
    SelecionarUsuario -->|"usersApi.create()"| ep_users_post
    Dashboard -->|"analyticsApi.summary()"| ep_summary
    Despesas -->|"expensesApi.list() / .create()"| ep_expenses
    ContasFixas -->|"billsApi.list() / .create()"| ep_bills
    Receitas -->|"incomesApi.list() / .create()"| ep_incomes
    Investimentos -->|"investmentsApi.list() / .create()"| ep_invest
    TetosCategoria -->|"categoryBudgetsApi.create()"| ep_catbud
    TetosCategoria -->|"analyticsApi.categoryAlerts()"| ep_catalert
    Parcelas -->|"analyticsApi.installments()"| ep_inst
    FaturasMensais -->|"analyticsApi.monthlyInvoices(N)"| ep_invoices

    classDef pg fill:#dbeafe,stroke:#2563eb,color:#1e3a8a;
    classDef ep fill:#dcfce7,stroke:#16a34a,color:#14532d;
    class SelecionarUsuario,Dashboard,Despesas,ContasFixas,Receitas,Investimentos,TetosCategoria,Parcelas,FaturasMensais pg;
    class ep_users_get,ep_users_post,ep_summary,ep_expenses,ep_bills,ep_incomes,ep_invest,ep_catbud,ep_catalert,ep_inst,ep_invoices ep;
```

### Mesma informação em tabela (pra consulta rápida)

| Página | Função de API (`frontend/src/api`) | Método + Rota | Router (backend) | Usa serviço? |
|--------|------------------------------------|---------------|------------------|--------------|
| SelectUserPage | `usersApi.list()` | `GET /users` | `users.py` | — |
| SelectUserPage | `usersApi.create()` | `POST /users` | `users.py` | — |
| DashboardPage | `analyticsApi.summary()` | `GET /users/{id}/summary` | `analytics.py` | ✅ `summarize_finances` |
| ExpensesPage | `expensesApi.list/create()` | `GET·POST /users/{id}/expenses` | `expenses.py` | — (CRUD) |
| BillsPage | `billsApi.list/create()` | `GET·POST /users/{id}/bills` | `bills.py` | — (CRUD) |
| IncomesPage | `incomesApi.list/create()` | `GET·POST /users/{id}/incomes` | `incomes.py` | — (CRUD) |
| InvestmentsPage | `investmentsApi.list/create()` | `GET·POST /users/{id}/investments` | `investments.py` | — (CRUD) |
| CategoryBudgetsPage | `categoryBudgetsApi.create()` | `POST /users/{id}/category-budgets` | `category_budgets.py` | — (CRUD + 409) |
| CategoryBudgetsPage | `analyticsApi.categoryAlerts()` | `GET /users/{id}/category-alerts` | `analytics.py` | ✅ `check_all_category_alerts` |
| InstallmentsPage | `analyticsApi.installments()` | `GET /users/{id}/installments` | `analytics.py` | ✅ `project_installments` |
| MonthlyInvoicesPage | `analyticsApi.monthlyInvoices(N)` | `GET /users/{id}/monthly-invoices` | `analytics.py` | ✅ `project_monthly_invoices` |

> A função `usersApi.get(id)` também existe (`frontend/src/api/users.ts`) e é usada para
> recarregar o usuário selecionado no `UserContext`, não a partir de uma página específica.

---

## 3. Sequência detalhada das chamadas "interessantes" (analytics)

Os endpoints de CRUD são diretos (recebe → grava/lê → responde). Os de *analytics* são os
que valem um diagrama de sequência, porque é onde a camada de serviço entra.

### 3.1 Dashboard — resumo financeiro

```mermaid
sequenceDiagram
    autonumber
    participant Pagina as DashboardPage
    participant Cliente as apiClient
    participant Proxy as Proxy Vite
    participant Router as analytics.py
    participant Servico as financial_service
    participant Banco as SQLite

    Pagina->>Cliente: analyticsApi.summary(userId)
    Cliente->>Proxy: GET /api/users/1/summary
    Proxy->>Router: GET /users/1/summary
    Router->>Banco: carrega usuário + receitas/despesas/contas/investimentos
    Router->>Servico: summarize_finances(...)
    Note over Servico: compõe calculate_balance +<br/>calculate_net_worth + check_budget_alert
    Servico-->>Router: { balance, net_worth, totais, budget_status }
    Router-->>Cliente: 200 JSON (FinancialSummary)
    Cliente-->>Pagina: dados renderizados
```

### 3.2 Faturas mensais (projeção consolidada)

```mermaid
sequenceDiagram
    autonumber
    participant Pagina as MonthlyInvoicesPage
    participant Cliente as apiClient
    participant Router as analytics.py
    participant Servico as financial_service
    participant Banco as SQLite

    Pagina->>Cliente: analyticsApi.monthlyInvoices(userId, N)
    Cliente->>Router: GET /api/users/1/monthly-invoices?months_ahead=N
    Router->>Banco: carrega despesas do usuário
    Note over Router: injeta o "hoje" (mês/ano de referência)<br/>— mantém o serviço puro
    Router->>Servico: project_monthly_invoices(despesas, mês, ano, N)
    Note over Servico: reusa project_installments<br/>e soma o que cai em cada mês
    Servico-->>Router: lista de MonthlyInvoice (um item por mês)
    Router-->>Cliente: 200 JSON (MonthlyInvoicesResponse)
    Cliente-->>Pagina: tabela de faturas futuras
```

### 3.3 Caminho de erro (404 — usuário inexistente)

Vale para **qualquer** rota `/users/{id}/...`: o helper `get_user_or_404`
(`app/dependencies.py`) roda antes da lógica.

```mermaid
sequenceDiagram
    autonumber
    participant Cliente as apiClient
    participant Router as router
    participant Guarda as get_user_or_404
    participant Banco as SQLite

    Cliente->>Router: GET /api/users/999/summary
    Router->>Guarda: valida usuário 999
    Guarda->>Banco: SELECT user 999
    Banco-->>Guarda: nada encontrado
    Guarda-->>Cliente: 404 { detail: "User not found" }
    Note over Cliente: client.ts lança ApiError(404)<br/>→ a página mostra o estado de erro
```

---

## 4. Camada de serviço — como as regras se compõem

Esta é a parte mais importante do projeto (todas as regras de negócio vivem aqui, em
funções **puras / IO-Free**). Em vez de descrever em texto, o melhor formato é um grafo de
**composição**: quais funções são "folhas" (regra atômica) e quais **reusam** as outras.

```mermaid
flowchart TD
    subgraph Endpoints["Endpoints que consomem o serviço"]
        rota_summary["GET /summary"]
        rota_alerts["GET /category-alerts"]
        rota_inst["GET /installments"]
        rota_invoices["GET /monthly-invoices"]
    end

    subgraph Compostas["Funções compostas (orquestram regras)"]
        summarize["summarize_finances"]
        all_alerts["check_all_category_alerts"]
        monthly["project_monthly_invoices"]
        cat_totals["calculate_category_totals"]
    end

    subgraph Folhas["Regras atômicas (folhas — totalmente testadas isoladas)"]
        balance["calculate_balance"]
        net_worth["calculate_net_worth"]
        budget["check_budget_alert<br/>OK · WARNING · EXCEEDED"]
        installments["project_installments"]
    end

    rota_summary --> summarize
    rota_alerts --> cat_totals
    rota_alerts --> all_alerts
    rota_inst --> installments
    rota_invoices --> monthly

    summarize --> balance
    summarize --> net_worth
    summarize --> budget
    all_alerts -->|"por categoria"| budget
    monthly -->|"reusa"| installments

    classDef ep fill:#dcfce7,stroke:#16a34a,color:#14532d;
    classDef comp fill:#fef3c7,stroke:#d97706,color:#7c2d12;
    classDef leaf fill:#ede9fe,stroke:#7c3aed,color:#4c1d95;
    class rota_summary,rota_alerts,rota_inst,rota_invoices ep;
    class summarize,all_alerts,monthly,cat_totals comp;
    class balance,net_worth,budget,installments leaf;
```

**Por que esse formato ajuda nos testes (objetivo acadêmico do projeto):**

- As **folhas** (roxo) são funções puras pequenas — testadas com unit tests e técnicas de
  cobertura (ex.: `check_budget_alert` tem MC/DC completo nos limites 80% e 100%).
- As **compostas** (amarelo) não reimplementam regra: elas *reusam* as folhas. Então o
  teste delas foca na orquestração, não em recalcular tudo.
- Os **endpoints** (verde) só fazem IO (ler banco, injetar "hoje") e delegam — por isso a
  regra continua testável sem banco e sem mocks.

### Resumo das funções

| Função | Papel | Compõe / reusa |
|--------|-------|----------------|
| `calculate_balance` | saldo = Σ receitas − Σ parcela mensal − Σ contas fixas | folha |
| `check_budget_alert` | classifica gasto vs. teto em OK/WARNING/EXCEEDED | folha |
| `project_installments` | distribui a compra em parcelas mensais (última absorve arredondamento) | folha |
| `calculate_net_worth` | patrimônio = saldo + Σ (investido + dividendos) | folha |
| `calculate_category_totals` | agrupa custo mensal por categoria | folha |
| `summarize_finances` | monta o resumo do dashboard | balance + net_worth + budget |
| `check_all_category_alerts` | aplica o alerta a cada categoria com teto | budget (por categoria) |
| `project_monthly_invoices` | consolida parcelas de todas as despesas por mês | installments |

---

## Referência rápida de arquivos

| Camada | Onde |
|--------|------|
| Cliente HTTP do front | `frontend/src/api/client.ts` |
| Módulos de API | `frontend/src/api/{users,entities,analytics}.ts` |
| Proxy de dev | `frontend/vite.config.ts` |
| Entrypoint backend | `app/main.py` |
| Rotas | `app/routers/*.py` |
| Regras de negócio | `app/services/financial_service.py` (+ `services/CLAUDE.md`) |
| Modelos ORM | `app/models/*.py` |
| Guarda 404 | `app/dependencies.py` |
