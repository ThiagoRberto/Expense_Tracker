from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Tipos de dados puros (sem dependência de ORM ou I/O)
# ---------------------------------------------------------------------------

@dataclass
class IncomeData:
    income_value: float

@dataclass
class ExpenseData:
    expense_value: float
    installment: int
    start_month: int
    start_year: int
    category: str = "geral"

@dataclass
class CategoryBudgetData:
    category: str
    ceiling: float

@dataclass
class BillData:
    bill_value: float

@dataclass
class InvestmentData:
    value_invested: float
    dividends: float = 0.0

@dataclass
class InstallmentEntry:
    installment_number: int
    month: int
    year: int
    amount: float

@dataclass
class MonthlyInvoice:
    month: int
    year: int
    total: float

BudgetStatus = Literal["OK", "WARNING", "EXCEEDED"]

# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _monthly_amount(expense: ExpenseData) -> float:
    """
    Fração mensal de uma despesa — o valor de uma única parcela.

    `installment <= 0` é tratado como 1 (compra à vista), evitando divisão por
    zero. Esta é a política tolerante das agregações de saldo/categoria;
    `project_installments` adota a política estrita (levanta ValueError).
    """
    return expense.expense_value / max(expense.installment, 1)


def _monthly_expense_total(expenses: list[ExpenseData]) -> float:
    """Soma da fração mensal de todas as despesas."""
    return sum(_monthly_amount(e) for e in expenses)


def _to_month_index(month: int, year: int) -> int:
    """
    Achata (mês, ano) num único número crescente — o "índice absoluto de mês".
    Fórmula: year*12 (meses dos anos já passados) + (month-1) (mês dentro do ano,
    com janeiro = 0).
    """
    return year * 12 + (month - 1)


def _from_month_index(index: int) -> tuple[int, int]:
    """
    Inverso de `_to_month_index`: índice absoluto → (mês, ano).
    """
    month = index % 12 + 1
    year = index // 12
    return month, year


# ---------------------------------------------------------------------------
# Regras de negócio
# ---------------------------------------------------------------------------

def calculate_balance(
    incomes: list[IncomeData],
    expenses: list[ExpenseData],
    bills: list[BillData],
) -> float:
    """
    Saldo mensal = receitas - parcela mensal de cada despesa - contas fixas.
    Resultado negativo indica déficit.
    """
    if any(i.income_value < 0 for i in incomes):
        raise ValueError("Income values cannot be negative")
    if any(e.expense_value < 0 for e in expenses):
        raise ValueError("Expense values cannot be negative")
    if any(b.bill_value < 0 for b in bills):
        raise ValueError("Bill values cannot be negative")

    total_income = sum(i.income_value for i in incomes)
    # cada despesa parcelada contribui apenas a sua parcela mensal
    total_expenses = _monthly_expense_total(expenses)
    total_bills = sum(b.bill_value for b in bills)

    return round(total_income - total_expenses - total_bills, 2)


def check_budget_alert(category_total: float, budget_ceiling: float) -> BudgetStatus:
    """
    Compara o gasto de uma categoria com o teto orçamentário.

    Retorna:
      "OK"       — gasto <= 80% do teto
      "WARNING"  — gasto entre 80% e 100% do teto (exclusive)
      "EXCEEDED" — gasto >= 100% do teto
    """
    if budget_ceiling <= 0:
        raise ValueError("Budget ceiling must be greater than zero")
    if category_total < 0:
        raise ValueError("Category total cannot be negative")

    ratio = category_total / budget_ceiling

    if ratio >= 1.0:
        return "EXCEEDED"
    if ratio > 0.8:
        return "WARNING"
    return "OK"


def project_installments(
    expense_value: float,
    installments: int,
    start_month: int,
    start_year: int,
) -> list[InstallmentEntry]:
    """
    Projeta as faturas futuras de uma compra parcelada.

    Distribui o valor total em `installments` parcelas iguais. A última
    parcela absorve a diferença de arredondamento para que a soma seja exata.
    """
    if expense_value < 0:
        raise ValueError("Expense value cannot be negative")
    if installments <= 0:
        raise ValueError("Installments must be at least 1")
    if not (1 <= start_month <= 12):
        raise ValueError("start_month must be between 1 and 12")
    if start_year < 1:
        raise ValueError("start_year must be a positive integer")

    monthly = round(expense_value / installments, 2)
    # última parcela corrige erro de arredondamento
    last_amount = round(expense_value - monthly * (installments - 1), 2)

    result: list[InstallmentEntry] = []
    month = start_month
    year = start_year

    for i in range(installments):
        amount = last_amount if i == installments - 1 else monthly
        result.append(InstallmentEntry(
            installment_number=i + 1,
            month=month,
            year=year,
            amount=amount,
        ))
        month += 1
        if month > 12:
            month = 1
            year += 1

    return result


def project_monthly_invoices(
    expenses: list[ExpenseData],
    reference_month: int,
    reference_year: int,
    months_ahead: int,
) -> list[MonthlyInvoice]:
    """
    Consolida as parcelas de todas as despesas em faturas mensais.

    Soma o valor de cada parcela que cai dentro da janela de `months_ahead`
    meses a partir de (reference_month, reference_year) inclusive. Todo mês da
    janela aparece no resultado em ordem cronológica, mesmo sem parcelas
    (total 0.0). Parcelas fora da janela (passadas ou além do horizonte) são
    ignoradas.

    Compõe `project_installments` para cada despesa, herdando sua validação
    estrita (installment >= 1) e o suporte a virada de ano.
    """
    if not (1 <= reference_month <= 12):
        raise ValueError("reference_month must be between 1 and 12")
    if reference_year < 1:
        raise ValueError("reference_year must be a positive integer")
    if months_ahead < 1:
        raise ValueError("months_ahead must be at least 1")

    # A janela é a faixa de meses [referência, referência + months_ahead).
    # Usamos o "índice absoluto de mês" (ver _to_month_index) para que pertencer
    # à janela e somar no mês certo virem comparações de inteiros.
    start_index = _to_month_index(reference_month, reference_year)
    window = range(start_index, start_index + months_ahead)

    # cada mês da janela começa com total zero
    totals: dict[int, float] = {index: 0.0 for index in window}

    # para cada despesa, projeta suas parcelas e soma cada uma no mês em que cai
    for expense in expenses:
        installments = project_installments(
            expense.expense_value,
            expense.installment,
            expense.start_month,
            expense.start_year,
        )
        for installment in installments:
            index = _to_month_index(installment.month, installment.year)
            if index in totals:  # ignora parcelas fora da janela
                totals[index] += installment.amount

    # monta uma fatura por mês da janela, em ordem cronológica
    invoices: list[MonthlyInvoice] = []
    for index in window:
        month, year = _from_month_index(index)
        invoices.append(
            MonthlyInvoice(month=month, year=year, total=round(totals[index], 2))
        )
    return invoices


def calculate_net_worth(
    investments: list[InvestmentData],
    balance: float,
) -> float:
    """
    Patrimônio líquido = saldo do mês + tudo que está investido (capital + dividendos).

    `balance` aqui é o SALDO mensal — o que sobra das receitas depois de descontar
    despesas e contas fixas (é o que `calculate_balance` devolve). A ideia: pegue o
    dinheiro "livre" do mês e some tudo que o usuário tem aplicado; isso é o quanto
    ele vale no total.

    Se o saldo for negativo (gastou mais do que ganhou), ele entra como número
    negativo na soma e reduz o patrimônio — que é o comportamento correto.
    """
    total_invested = sum(i.value_invested + i.dividends for i in investments)
    return round(balance + total_invested, 2)


def summarize_finances(
    incomes: list[IncomeData],
    expenses: list[ExpenseData],
    bills: list[BillData],
    investments: list[InvestmentData],
    budget_ceiling: float | None = None,
) -> dict:
    """
    Consolida os indicadores financeiros de um usuário em um único dicionário.
    Útil como resposta de endpoint de resumo.
    """
    balance = calculate_balance(incomes, expenses, bills)
    net_worth = calculate_net_worth(investments, balance)
    total_spending = _monthly_expense_total(expenses) + sum(b.bill_value for b in bills)

    result = {
        "balance": balance,
        "net_worth": net_worth,
        "total_income": round(sum(i.income_value for i in incomes), 2),
        "total_spending": round(total_spending, 2),
    }

    if budget_ceiling is not None:
        result["budget_status"] = check_budget_alert(total_spending, budget_ceiling)

    return result


def calculate_category_totals(expenses: list[ExpenseData]) -> dict[str, float]:
    """
    Agrupa o custo mensal de cada despesa por categoria.
    Despesas parceladas contribuem apenas com sua fração mensal.
    """
    totals: dict[str, float] = {}
    for e in expenses:
        monthly = round(_monthly_amount(e), 2)
        totals[e.category] = round(totals.get(e.category, 0.0) + monthly, 2)
    return totals


def check_all_category_alerts(
    category_totals: dict[str, float],
    category_budgets: list[CategoryBudgetData],
) -> dict[str, BudgetStatus]:
    """
    Retorna o status de alerta para cada categoria que possui teto definido.
    Categorias sem despesas são tratadas como gasto zero.
    """
    result: dict[str, BudgetStatus] = {}
    for cb in category_budgets:
        if cb.ceiling <= 0:
            raise ValueError(f"Ceiling for category '{cb.category}' must be greater than zero")
        total = category_totals.get(cb.category, 0.0)
        result[cb.category] = check_budget_alert(total, cb.ceiling)
    return result
