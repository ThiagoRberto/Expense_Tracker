# services/financial_service.py

Camada de regras de negócio do Expense Tracker. Todas as funções são **puras (IO-Free — sem entrada/saída)**: não acessam banco de dados, não fazem chamadas externas e não dependem de estado global. Isso as torna diretamente testáveis com testes unitários sem nenhum mock (objeto simulado).

---

## Glossário

| Termo (código) | Significado |
|----------------|-------------|
| `income` | **Receita** — dinheiro que entra (salário, renda extra) |
| `expense` | **Despesa** — gasto ou compra realizada |
| `bill` | **Conta fixa** — cobrança recorrente (aluguel, água, luz) |
| `installment` | **Parcela** — uma das divisões mensais de uma compra parcelada |
| `balance` | **Saldo** — diferença entre receitas e gastos do mês |
| `budget_ceiling` / `ceiling` | **Teto orçamentário** — limite máximo de gasto definido pelo usuário |
| `net_worth` | **Patrimônio líquido** — soma do saldo com todos os investimentos e dividendos |
| `dividends` | **Dividendos** — rendimentos gerados pelos investimentos |
| `ratio` | **Proporção** — resultado da divisão do gasto pelo teto (ex: 0.85 = 85% do teto usado) |
| `dataclass` | **Classe de dados** — estrutura Python para agrupar campos relacionados |
| `IO-Free` | **Sem entrada/saída** — a função só trabalha com os dados recebidos nos parâmetros; não lê banco, arquivo ou rede |
| `MC/DC` | **Cobertura de condição/decisão modificada** — técnica de teste que verifica cada condição lógica de forma independente |
| `boundary analysis` | **Análise de fronteiras** — testa os valores exatos nos limites de uma condição (ex: exatamente 80% e 100%) |
| `ValueError` | **Erro de valor** — exceção Python lançada quando um argumento tem valor inválido |

---

## Tipos de dados

O arquivo define dataclasses (classes de dados) próprias para desacoplar a lógica dos modelos ORM:

| Dataclass | Campos |
|-----------|--------|
| `IncomeData` | `income_value: float` (valor da receita) |
| `ExpenseData` | `expense_value: float` (valor da despesa), `installment: int = 1` (parcelas), `category: str = "geral"` |
| `BillData` | `bill_value: float` (valor da conta fixa) |
| `InvestmentData` | `value_invested: float`, `dividends: float = 0.0` (dividendos) |
| `CategoryBudgetData` | `category: str`, `ceiling: float` (teto orçamentário) |
| `InstallmentPurchase` | `expense_value: float` (valor da despesa), `installments: int` (parcelas), `start_month: int`, `start_year: int` |
| `InstallmentEntry` | `installment_number: int`, `month: int`, `year: int`, `amount: float` |
| `MonthlyInvoice` | `month: int`, `year: int`, `total: float` (fatura consolidada de um mês) |

> **Por que `ExpenseData` e `InstallmentPurchase` são tipos separados:** cada função recebe exatamente o que precisa (segregação de interface). `calculate_balance` e `calculate_category_totals` não dependem de data, então usam a `ExpenseData` enxuta. As projeções de fatura precisam da data da primeira parcela, então usam a `InstallmentPurchase`, onde `start_month`/`start_year` são **obrigatórios** — a data de uma compra parcelada é dado real, nunca um default. Evita-se assim um campo de data sem semântica numa `ExpenseData` única. A camada pura **nunca** lê o relógio; quem injeta a data real (do ORM) é o router.

`BudgetStatus = Literal["OK", "WARNING", "EXCEEDED"]` — tipo de retorno de `check_budget_alert` e `check_all_category_alerts`.

---

## Funções

### `calculate_balance(incomes, expenses, bills) -> float`

Calcula o saldo (`balance`) mensal disponível do usuário a partir das receitas (`incomes`), despesas (`expenses`) e contas fixas (`bills`).

**Fórmula:**
```
saldo = Σ receitas − Σ (valor_despesa / parcelas) − Σ contas_fixas
```

Cada despesa (`expense`) parcelada contribui apenas com sua fração mensal (`expense_value` (valor da despesa) `/ installment` (parcela)). Se `installment` (parcela) `= 0`, é tratado como `1` via `max(installment, 1)` para evitar divisão por zero.

Resultado negativo indica déficit mensal (saldo negativo).

**Validações:** levanta `ValueError` se qualquer `income_value` (receita), `expense_value` (despesa) ou `bill_value` (conta fixa) for negativo.

---

### `check_budget_alert(category_total, budget_ceiling) -> BudgetStatus`

Compara o total gasto em uma categoria com o teto orçamentário (`budget_ceiling` — limite máximo) definido pelo usuário.

**Lógica (duas condições independentes — base do MC/DC):**

```
ratio (proporção) = gasto_na_categoria / teto_orçamentário

ratio >= 1.0  →  "EXCEEDED"  (teto ultrapassado)
ratio >  0.8  →  "WARNING"   (acima de 80% do teto)
caso contrário →  "OK"
```

| Intervalo de ratio (proporção) | Status |
|-------------------------------|--------|
| 0.0 ≤ ratio ≤ 0.80 | `OK` |
| 0.80 < ratio < 1.0 | `WARNING` |
| ratio ≥ 1.0 | `EXCEEDED` |

**Validações:** `budget_ceiling` (teto) deve ser > 0; `category_total` não pode ser negativo.

---

### `project_installments(expense_value, installments, start_month, start_year) -> list[InstallmentEntry]`

Projeta as faturas futuras de uma compra parcelada, com suporte a virada de ano.

**Comportamento:**
- Divide `expense_value` (valor da despesa) em `installments` (parcelas / pagamentos mensais) iguais, arredondadas em 2 casas decimais
- A **última parcela (`installment`) absorve o erro de arredondamento**, garantindo que a soma seja exatamente igual ao valor original
- Ao passar de dezembro, `month` volta para 1 e `year` incrementa (virada de ano)

**Exemplo:** `project_installments(10.0, 3, 11, 2025)` retorna:
```
[InstallmentEntry(1, 11, 2025, 3.33),   ← parcela 1: novembro
 InstallmentEntry(2, 12, 2025, 3.33),   ← parcela 2: dezembro
 InstallmentEntry(3,  1, 2026, 3.34)]   ← parcela 3: janeiro (correção de arredondamento)
```

**Validações:** `expense_value` (valor da despesa) `>= 0`, `installments` (parcelas) `>= 1`, `1 <= start_month <= 12`, `start_year >= 1`.

---

### `project_monthly_invoices(purchases, reference_month, reference_year, months_ahead) -> list[MonthlyInvoice]`

Recebe uma lista de `InstallmentPurchase` (compras parceladas) e consolida as parcelas (`installments`) de **todas** elas em faturas mensais — responde "quanto vou dever em cada um dos próximos meses".

**Comportamento:**
- Soma o valor de cada parcela que cai na janela de `months_ahead` meses a partir de `(reference_month, reference_year)` **inclusive**
- Todo mês da janela aparece no resultado, em ordem cronológica, mesmo sem parcelas (`total = 0.0`)
- Parcelas fora da janela (já vencidas ou além do horizonte) são ignoradas
- **Compõe** `project_installments` por compra, reaproveitando a lógica testada (virada de ano, arredondamento) e herdando sua política estrita (`installments >= 1`)
- Internamente usa um índice absoluto de mês (`ano*12 + mês-1`) para linearizar a virada de ano

**Pureza:** a função não lê o relógio. O mês/ano de referência ("hoje") é injetado pela camada de router via `datetime.now()`, mantendo o serviço determinístico e testável.

**Exemplo:** janela de 3 meses a partir de nov/2025, com uma compra de R$ 300 em 3x começando em nov/2025:
```python
project_monthly_invoices([InstallmentPurchase(300, 3, 11, 2025)], 11, 2025, 3)
# → [MonthlyInvoice(11, 2025, 100.0),
#    MonthlyInvoice(12, 2025, 100.0),
#    MonthlyInvoice(1, 2026, 100.0)]
```

**Validações:** `months_ahead >= 1`, `1 <= reference_month <= 12`, `reference_year >= 1`.

---

### `calculate_net_worth(investments, balance) -> float`

Calcula o patrimônio líquido (`net_worth`) total do usuário a partir dos investimentos (`investments`) e do saldo (`balance`).

**Fórmula:**
```
patrimônio líquido = saldo + Σ (capital_investido + dividendos)
```

Saldo (`balance`) negativo (déficit) reduz o patrimônio líquido. Lista vazia de investimentos retorna apenas o saldo.

---

### `summarize_finances(incomes, expenses, bills, investments, budget_ceiling) -> dict`

Função de composição que agrega todos os indicadores financeiros em um único dicionário. Internamente chama `calculate_balance` (saldo), `calculate_net_worth` (patrimônio líquido) e, se `budget_ceiling` (teto orçamentário) for informado, `check_budget_alert`.

**Retorno:**
```python
{
    "balance": float,           # saldo mensal
    "net_worth": float,         # patrimônio líquido
    "total_income": float,      # total de receitas
    "total_spending": float,    # total de gastos (despesas + contas fixas)
    "budget_status": "OK" | "WARNING" | "EXCEEDED"  # apenas se budget_ceiling != None
}
```

---

### `calculate_category_totals(expenses) -> dict[str, float]`

Agrupa o custo mensal de cada despesa (`expense`) por categoria.

**Comportamento:**
- Cada despesa (`expense`) contribui com `expense_value / max(installment, 1)` (valor da despesa ÷ parcelas — sua fração mensal, ou seja, o valor de uma parcela)
- Despesas da mesma categoria são somadas
- Despesas sem categoria explícita usam `"geral"` (padrão de `ExpenseData`)

**Exemplo:**
```python
expenses = [
    ExpenseData(600, 2, "alimentação"),  # 300/mês (parcela de compra em 2x)
    ExpenseData(300, 1, "alimentação"),  # 300/mês (compra à vista)
    ExpenseData(400, 1, "transporte"),   # 400/mês
]
calculate_category_totals(expenses)
# → {"alimentação": 600.0, "transporte": 400.0}
```

---

### `check_all_category_alerts(category_totals, category_budgets) -> dict[str, BudgetStatus]`

Aplica `check_budget_alert` para cada categoria que possui teto (limite) definido em `category_budgets`.

**Comportamento:**
- Categorias com teto mas sem despesas são tratadas como gasto zero (`"OK"`)
- Categorias com despesas mas sem teto são ignoradas (não aparecem no resultado)
- Levanta `ValueError` se qualquer `ceiling` (teto) for `<= 0`

**Exemplo:**
```python
totals = {"alimentação": 300.0, "lazer": 600.0}
budgets = [
    CategoryBudgetData("alimentação", 500),  # teto de R$ 500
    CategoryBudgetData("lazer", 500),        # teto de R$ 500
]
check_all_category_alerts(totals, budgets)
# → {"alimentação": "OK", "lazer": "EXCEEDED"}
#   alimentação: 300/500 = 60% → OK
#   lazer: 600/500 = 120% → EXCEEDED (ultrapassou o teto)
```
