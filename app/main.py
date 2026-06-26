import models

from fastapi import FastAPI

from database.database import engine, Base
from routers import users, expenses, bills, incomes, investments, category_budgets

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(bills.router)
app.include_router(incomes.router)
app.include_router(investments.router)
app.include_router(category_budgets.router)
