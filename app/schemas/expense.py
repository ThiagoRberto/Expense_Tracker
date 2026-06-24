from pydantic import BaseModel

class Expense(BaseModel):
    id: int
    name: str
    expense_value: float
    installment: int

    class Config:
        from_atrributes = True

class ExpenseCreate(Expense):
    name: str
    expense_value: float
    installment: int