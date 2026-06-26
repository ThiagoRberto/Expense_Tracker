from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models
from schemas.bill import Bill, BillCreate
from database.database import get_db
from dependencies import get_user_or_404

router = APIRouter(prefix="/users/{user_id}/bills", tags=["bills"])


@router.post("", response_model=Bill)
def create_bill(user_id: int, bill: BillCreate, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    db_bill = models.Bill(**bill.model_dump(), user_id=user_id)
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill


@router.get("", response_model=List[Bill])
def list_bills(user_id: int, db: Session = Depends(get_db)):
    get_user_or_404(user_id, db)
    return db.query(models.Bill).filter(models.Bill.user_id == user_id).all()
