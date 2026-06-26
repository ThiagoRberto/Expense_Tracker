from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    name: str
    category: str = "geral"
    expense_value: float
    installment: int = 1
    start_month: int = Field(default_factory=lambda: datetime.now().month)
    start_year: int = Field(default_factory=lambda: datetime.now().year)


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
