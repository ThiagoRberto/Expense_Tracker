import models

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from database.database import engine, Base
from routers import users, expenses, bills, incomes, investments, category_budgets, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(bills.router)
app.include_router(incomes.router)
app.include_router(investments.router)
app.include_router(category_budgets.router)
app.include_router(analytics.router)
