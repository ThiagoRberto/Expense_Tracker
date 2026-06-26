import models

from schemas.user import User, UserCreate
from schemas.summary import FinancialSummary
from services.financial_service import (
    summarize_finances, IncomeData, ExpenseData, BillData, InvestmentData
)

from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database.database import SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/users/', response_model=User)
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

@app.get('/users/', response_model=List[User])
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).options(
        joinedload(models.User.bills),
        joinedload(models.User.expenses),
        joinedload(models.User.incomes),
        joinedload(models.User.investments),
    ).all()
    return users

@app.get('/users/{user_id}', response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).options(
        joinedload(models.User.bills),
        joinedload(models.User.expenses),
        joinedload(models.User.incomes),
        joinedload(models.User.investments),
    ).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get('/users/{user_id}/summary', response_model=FinancialSummary)
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).options(
        joinedload(models.User.bills),
        joinedload(models.User.expenses),
        joinedload(models.User.incomes),
        joinedload(models.User.investments),
    ).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return summarize_finances(
        incomes=[IncomeData(i.income_value) for i in user.incomes],
        expenses=[ExpenseData(e.expense_value, e.installment) for e in user.expenses],
        bills=[BillData(b.bill_value) for b in user.bills],
        investments=[InvestmentData(i.value_invested, i.dividends) for i in user.investments],
        budget_ceiling=user.budget_ceiling,
    )
