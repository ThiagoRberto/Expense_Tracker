from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

import models
from schemas.user import User, UserCreate
from schemas.summary import FinancialSummary
from schemas.category_alert import CategoryAlertsResponse, CategoryAlertItem
from schemas.installment import InstallmentsResponse, ExpenseProjection, InstallmentEntrySchema
from services.financial_service import (
    summarize_finances, calculate_category_totals, check_all_category_alerts,
    project_installments,
    IncomeData, ExpenseData, BillData, InvestmentData, CategoryBudgetData,
)
from database.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


def _load_user(user_id: int, db: Session):
    user = db.query(models.User).options(
        joinedload(models.User.bills),
        joinedload(models.User.expenses),
        joinedload(models.User.incomes),
        joinedload(models.User.investments),
    ).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        name=user.name,
        password=user.password,
        budget_ceiling=user.budget_ceiling,
        bills=[models.Bill(**b.model_dump()) for b in user.bills],
        expenses=[models.Expense(**e.model_dump()) for e in user.expenses],
        incomes=[models.Income(**i.model_dump()) for i in user.incomes],
        investments=[models.Investment(**inv.model_dump()) for inv in user.investments],
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("", response_model=List[User])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).options(
        joinedload(models.User.bills),
        joinedload(models.User.expenses),
        joinedload(models.User.incomes),
        joinedload(models.User.investments),
    ).all()


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return _load_user(user_id, db)


@router.get("/{user_id}/summary", response_model=FinancialSummary)
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    user = _load_user(user_id, db)
    return summarize_finances(
        incomes=[IncomeData(i.income_value) for i in user.incomes],
        expenses=[ExpenseData(e.expense_value, e.installment, e.category) for e in user.expenses],
        bills=[BillData(b.bill_value) for b in user.bills],
        investments=[InvestmentData(i.value_invested, i.dividends) for i in user.investments],
        budget_ceiling=user.budget_ceiling,
    )


@router.get("/{user_id}/category-alerts", response_model=CategoryAlertsResponse)
def get_category_alerts(user_id: int, db: Session = Depends(get_db)):
    user = _load_user(user_id, db)
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


@router.get("/{user_id}/installments", response_model=InstallmentsResponse)
def get_installments(user_id: int, db: Session = Depends(get_db)):
    user = _load_user(user_id, db)
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
