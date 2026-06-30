from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

import models
from schemas.category_budget import CategoryBudget, CategoryBudgetCreate
from database.database import get_db
from dependencies import get_user_or_404

router = APIRouter(prefix="/users/{user_id}/category-budgets", tags=["category_budgets"])


@router.post("", response_model=CategoryBudget)
def create_category_budget(user_id: int, budget: CategoryBudgetCreate, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    db_budget = models.CategoryBudget(**budget.model_dump(), user_id=user_id)
    db.add(db_budget)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail=f"Budget for category '{budget.category}' already exists",
        )
    db.refresh(db_budget)
    return db_budget


@router.get("", response_model=List[CategoryBudget])
def list_category_budgets(user_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    return db.query(models.CategoryBudget).filter(models.CategoryBudget.user_id == user_id).all()


@router.delete("/{budget_id}", status_code=204)
def delete_category_budget(user_id: int, budget_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    budget = db.query(models.CategoryBudget).filter(
        models.CategoryBudget.id == budget_id, models.CategoryBudget.user_id == user_id
    ).first()
    if not budget:
        raise HTTPException(status_code=404, detail="Category budget not found")
    db.delete(budget)
    db.commit()
