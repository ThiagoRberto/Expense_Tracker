from pydantic import BaseModel, ConfigDict


class ExpenseBase(BaseModel):
    name: str
    category: str = "geral"
    expense_value: float
    installment: int = 1


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
