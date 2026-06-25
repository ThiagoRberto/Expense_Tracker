# services/financial_service.py

Camada de regras de negócio do Expense Tracker. Todas as funções são **puras (IO-Free)**: não acessam banco de dados, não fazem chamadas externas e não dependem de estado global. Isso as torna diretamente testáveis com testes unitários sem nenhum mock.

## Tipos de dados

O arquivo define dataclasses próprias para desacoplar a lógica dos modelos ORM:

| Dataclass | Campos |
|-----------|--------|
| `IncomeData` | `income_value: float` |
| `ExpenseData` | `expense_value: float`, `installment: int = 1` |
| `BillData` | `bill_value: float` |
| `InvestmentData` | `value_invested: float`, `dividends: float = 0.0` |
| `InstallmentEntry` | `installment_number`, `month`, `year`, `amount` |

`BudgetStatus = Literal["OK", "WARNING", "EXCEEDED"]` — tipo de retorno de `check_budget_alert`.

---

## Funções

### `calculate_balance(incomes, expenses, bills) -> float`

Calcula o saldo mensal disponível do usuário.

**Fórmula:**
```
saldo = Σ receitas − Σ (valor_despesa / parcelas) − Σ contas_fixas
```

Cada despesa parcelada contribui apenas com sua fração mensal (`expense_value / installment`). Se `installment = 0`, é tratado como `1` via `max(installment, 1)` para evitar divisão por zero.

Resultado negativo indica déficit mensal.

**Validações:** levanta `ValueError` se qualquer `income_value`, `expense_value` ou `bill_value` for negativo.

---

### `check_budget_alert(category_total, budget_ceiling) -> BudgetStatus`

Compara o total gasto em uma categoria com o teto orçamentário definido pelo usuário.

**Lógica (duas condições independentes — base do MC/DC):**

```
ratio = category_total / budget_ceiling

ratio >= 1.0  →  "EXCEEDED"
ratio >  0.8  →  "WARNING"
caso contrário →  "OK"
```

| Intervalo de ratio | Status |
|--------------------|--------|
| 0.0 ≤ ratio ≤ 0.80 | `OK` |
| 0.80 < ratio < 1.0 | `WARNING` |
| ratio ≥ 1.0 | `EXCEEDED` |

**Validações:** `budget_ceiling` deve ser > 0; `category_total` não pode ser negativo.

---

### `project_installments(expense_value, installments, start_month, start_year) -> list[InstallmentEntry]`

Projeta as faturas futuras de uma compra parcelada, com suporte a virada de ano.

**Comportamento:**
- Divide `expense_value` em `installments` parcelas iguais (arredondadas em 2 casas)
- A **última parcela absorve o erro de arredondamento**, garantindo que a soma seja exatamente igual ao valor original
- Ao passar de dezembro, `month` volta para 1 e `year` incrementa

**Exemplo:** `project_installments(10.0, 3, 11, 2025)` retorna:
```
[InstallmentEntry(1, 11, 2025, 3.33),
 InstallmentEntry(2, 12, 2025, 3.33),
 InstallmentEntry(3,  1, 2026, 3.34)]  ← correção de arredondamento
```

**Validações:** `expense_value >= 0`, `installments >= 1`, `1 <= start_month <= 12`, `start_year >= 1`.

---

### `calculate_net_worth(investments, balance) -> float`

Calcula o patrimônio líquido total do usuário.

**Fórmula:**
```
patrimônio = saldo + Σ (value_invested + dividends)
```

Saldo negativo (déficit) reduz o patrimônio. Lista vazia de investimentos retorna apenas o saldo.

---

### `summarize_finances(incomes, expenses, bills, investments, budget_ceiling) -> dict`

Função de composição que agrega todos os indicadores em um único dicionário. Internamente chama `calculate_balance`, `calculate_net_worth` e, se `budget_ceiling` for informado, `check_budget_alert`.

**Retorno:**
```python
{
    "balance": float,
    "net_worth": float,
    "total_income": float,
    "total_spending": float,
    "budget_status": "OK" | "WARNING" | "EXCEEDED"  # apenas se budget_ceiling != None
}
```
