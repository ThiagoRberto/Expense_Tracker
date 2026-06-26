import models

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from database.database import engine, Base
from routers import users, expenses, bills, incomes, investments, category_budgets, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    # Regras de negócio na camada de serviço sinalizam entradas inválidas via
    # ValueError. A validação dos schemas (Field) já barra dados ruins na escrita;
    # este handler é a rede de segurança para dados legados, traduzindo para 422
    # em vez de deixar vazar um 500.
    return JSONResponse(status_code=422, content={"detail": str(exc)})


app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(bills.router)
app.include_router(incomes.router)
app.include_router(investments.router)
app.include_router(category_budgets.router)
app.include_router(analytics.router)
