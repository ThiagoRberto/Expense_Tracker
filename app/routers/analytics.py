from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

import models
from schemas.summary import FinancialSummary
from schemas.category_alert import CategoryAlertsResponse, CategoryAlertItem
from schemas.installment import InstallmentsResponse, ExpenseProjection, InstallmentEntrySchema
from schemas.monthly_invoice import MonthlyInvoicesResponse, MonthlyInvoiceItem
from services.financial_service import (
    summarize_finances, calculate_category_totals, check_all_category_alerts,
    project_installments, project_monthly_invoices,
    IncomeData, ExpenseData, BillData, InvestmentData, CategoryBudgetData,
    InstallmentPurchase,
)
from database.database import get_db
from dependencies import get_user_or_404

# Indicadores financeiros derivados dos dados do usuário (resumo, alertas por
# categoria, projeção de parcelas e faturas mensais). Separado do CRUD de
# usuário em users.py.
router = APIRouter(prefix="/users/{user_id}", tags=["analytics"])


def _to_expense_data(expense) -> ExpenseData:
    """Converte um Expense (ORM) na ExpenseData pura — usada por saldo/categoria,
    que não dependem da data da compra."""
    return ExpenseData(expense.expense_value, expense.installment, expense.category)


def _to_installment_purchase(expense) -> InstallmentPurchase:
    """Converte um Expense (ORM) na InstallmentPurchase pura — usada pelas
    projeções de fatura, que precisam da data da primeira parcela."""
    return InstallmentPurchase(
        expense.expense_value,
        expense.installment,
        expense.start_month,
        expense.start_year,
    )


@router.get("/summary", response_model=FinancialSummary)
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    user = get_user_or_404(user_id, db, with_relations=True)
    return summarize_finances(
        incomes=[IncomeData(i.income_value) for i in user.incomes],
        expenses=[_to_expense_data(e) for e in user.expenses],
        bills=[BillData(b.bill_value) for b in user.bills],
        investments=[InvestmentData(i.value_invested, i.dividends) for i in user.investments],
        budget_ceiling=user.budget_ceiling,
    )


@router.get("/category-alerts", response_model=CategoryAlertsResponse)
def get_category_alerts(user_id: int, db: Session = Depends(get_db)):
    user = get_user_or_404(user_id, db, with_relations=True)
    category_budgets = (
        db.query(models.CategoryBudget)
        .filter(models.CategoryBudget.user_id == user_id)
        .all()
    )

    expenses = [_to_expense_data(e) for e in user.expenses]
    cb_data = [CategoryBudgetData(cb.category, cb.ceiling) for cb in category_budgets]

    totals = calculate_category_totals(expenses)
    alerts = check_all_category_alerts(totals, cb_data)

    return CategoryAlertsResponse(alerts=[
        CategoryAlertItem(
            category=cb.category,
            total=totals.get(cb.category, 0.0),
            ceiling=cb.ceiling,
            status=alerts[cb.category],
        )
        for cb in category_budgets
    ])


@router.get("/installments", response_model=InstallmentsResponse)
def get_installments(user_id: int, db: Session = Depends(get_db)):
    user = get_user_or_404(user_id, db, with_relations=True)
    projections = []
    for expense in user.expenses:
        entries = project_installments(
            expense.expense_value,
            expense.installment,
            expense.start_month,
            expense.start_year,
        )
        projections.append(ExpenseProjection(
            expense_id=expense.id,
            expense_name=expense.name,
            category=expense.category,
            total_value=expense.expense_value,
            installments=expense.installment,
            entries=[
                InstallmentEntrySchema(
                    installment_number=e.installment_number,
                    month=e.month,
                    year=e.year,
                    amount=e.amount,
                )
                for e in entries
            ],
        ))
    return InstallmentsResponse(projections=projections)


@router.get("/monthly-invoices", response_model=MonthlyInvoicesResponse)
def get_monthly_invoices(
    user_id: int,
    months_ahead: int = Query(default=6, ge=1, le=120),
    db: Session = Depends(get_db),
):
    user = get_user_or_404(user_id, db, with_relations=True)
    # o "hoje" (relógio) é injetado aqui, no router; a função de serviço
    # permanece pura e determinística.
    now = datetime.now()
    invoices = project_monthly_invoices(
        [_to_installment_purchase(e) for e in user.expenses],
        now.month,
        now.year,
        months_ahead,
    )
    return MonthlyInvoicesResponse(
        months_ahead=months_ahead,
        invoices=[
            MonthlyInvoiceItem(month=inv.month, year=inv.year, total=inv.total)
            for inv in invoices
        ],
    )
