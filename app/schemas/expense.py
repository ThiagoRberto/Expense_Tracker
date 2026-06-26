from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ExpenseBase(BaseModel):
    name: str
    category: str = "geral"
    expense_value: float = Field(ge=0)
    installment: int = Field(default=1, ge=1)
    start_month: int = Field(default_factory=lambda: datetime.now().month, ge=1, le=12)
    start_year: int = Field(default_factory=lambda: datetime.now().year, ge=1)


class ExpenseCreate(ExpenseBase):
    pass


class Expense(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
