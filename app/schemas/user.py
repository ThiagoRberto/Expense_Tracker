from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from schemas.bill import Bill, BillCreate
from schemas.expense import Expense, ExpenseCreate
from schemas.income import Income, IncomeCreate
from schemas.investment import Investment, InvestmentCreate

class UserBase(BaseModel):
    name: str
    budget_ceiling: Optional[float] = Field(default=None, gt=0)

class UserCreate(UserBase):
    password: str
    bills: List[BillCreate] = []
    expenses: List[ExpenseCreate] = []
    incomes: List[IncomeCreate] = []
    investments: List[InvestmentCreate] = []

# `password` fica apenas no schema de entrada (UserCreate); nunca é serializado na saída.
class UserUpdate(BaseModel):
    budget_ceiling: Optional[float] = Field(default=None, gt=0)

class LoginRequest(BaseModel):
    name: str
    password: str

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bills: List[Bill] = []
    expenses: List[Expense] = []
    incomes: List[Income] = []
    investments: List[Investment] = []
