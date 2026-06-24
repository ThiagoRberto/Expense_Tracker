import models
import database

from schemas.user import User, UserCreate 

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

@app.post('/users/', 
          response_model = User)
def create_user(user: UserCreate,
                   db: Session = Depends(get_db)
                ):
    db_user = models.User(
        name = user.name,
        password = user.password,
        bills = models.Bill(**user.bill.dict()),
        expenses = models.Expense(**user.expense.dict()),
        incomes = models.Income(**user.income.dict()),
        investments = models.Investment(**user.investment.dict()),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get('/users/', 
          response_model = List[User])
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).options(
        joinedload(models.User.bill),
        joinedload(models.User.expense),
        joinedload(models.User.income),
        joinedload(models.User.investment),
    ).all()
    return users
