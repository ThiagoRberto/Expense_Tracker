from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

import models
from schemas.user import User, UserCreate, UserUpdate, LoginRequest
from database.database import get_db
from dependencies import get_user_or_404

router = APIRouter(prefix="/users", tags=["users"])


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
    return get_user_or_404(user_id, db, with_relations=True)


@router.post("/login", response_model=User)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .options(
            joinedload(models.User.bills),
            joinedload(models.User.expenses),
            joinedload(models.User.incomes),
            joinedload(models.User.investments),
        )
        .filter(models.User.name == payload.name)
        .first()
    )
    if not user or user.password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid name or password")
    return user


@router.patch("/{user_id}", response_model=User)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = get_user_or_404(user_id, db, with_relations=True)
    if payload.budget_ceiling is not None:
        user.budget_ceiling = payload.budget_ceiling
    else:
        user.budget_ceiling = None
    db.commit()
    db.refresh(user)
    return user
