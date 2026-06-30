from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from schemas.income import Income, IncomeCreate
from database.database import get_db
from dependencies import get_user_or_404

router = APIRouter(prefix="/users/{user_id}/incomes", tags=["incomes"])


@router.post("", response_model=Income)
def create_income(user_id: int, income: IncomeCreate, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    db_income = models.Income(**income.model_dump(), user_id=user_id)
    db.add(db_income)
    db.commit()
    db.refresh(db_income)
    return db_income


@router.get("", response_model=List[Income])
def list_incomes(user_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    return db.query(models.Income).filter(models.Income.user_id == user_id).all()


@router.delete("/{income_id}", status_code=204)
def delete_income(user_id: int, income_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    income = db.query(models.Income).filter(
        models.Income.id == income_id, models.Income.user_id == user_id
    ).first()
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    db.delete(income)
    db.commit()
