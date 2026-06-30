from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from schemas.investment import Investment, InvestmentCreate
from database.database import get_db
from dependencies import get_user_or_404

router = APIRouter(prefix="/users/{user_id}/investments", tags=["investments"])


@router.post("", response_model=Investment)
def create_investment(user_id: int, investment: InvestmentCreate, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    db_investment = models.Investment(**investment.model_dump(), user_id=user_id)
    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)
    return db_investment


@router.get("", response_model=List[Investment])
def list_investments(user_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    return db.query(models.Investment).filter(models.Investment.user_id == user_id).all()


@router.delete("/{investment_id}", status_code=204)
def delete_investment(user_id: int, investment_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    investment = db.query(models.Investment).filter(
        models.Investment.id == investment_id, models.Investment.user_id == user_id
    ).first()
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    db.delete(investment)
    db.commit()
