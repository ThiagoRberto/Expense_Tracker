from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from schemas.expense import Expense, ExpenseCreate
from database.database import get_db
from dependencies import get_user_or_404

router = APIRouter(prefix="/users/{user_id}/expenses", tags=["expenses"])


@router.post("", response_model=Expense)
def create_expense(user_id: int, expense: ExpenseCreate, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    db_expense = models.Expense(**expense.model_dump(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


@router.get("", response_model=List[Expense])
def list_expenses(user_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    return db.query(models.Expense).filter(models.Expense.user_id == user_id).all()
