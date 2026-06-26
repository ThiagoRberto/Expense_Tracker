from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from schemas.summary import FinancialSummary
from schemas.category_alert import CategoryAlertsResponse, CategoryAlertItem
from schemas.installment import InstallmentsResponse, ExpenseProjection, InstallmentEntrySchema
from services.financial_service import (
    summarize_finances, calculate_category_totals, check_all_category_alerts,
    project_installments,
    IncomeData, ExpenseData, BillData, InvestmentData, CategoryBudgetData,
)
from database.database import get_db
from dependencies import get_user_or_404

# Indicadores financeiros derivados dos dados do usuário (resumo, alertas por
# categoria e projeção de parcelas). Separado do CRUD de usuário em users.py.
router = APIRouter(prefix="/users/{user_id}", tags=["analytics"])


@router.get("/summary", response_model=FinancialSummary)
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    user = get_user_or_404(user_id, db, with_relations=True)
    return summarize_finances(
        incomes=[IncomeData(i.income_value) for i in user.incomes],
        expenses=[ExpenseData(e.expense_value, e.installment, e.category) for e in user.expenses],
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

    expenses = [ExpenseData(e.expense_value, e.installment, e.category) for e in user.expenses]
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
