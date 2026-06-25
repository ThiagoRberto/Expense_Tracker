from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from schemas.bill import Bill, BillCreate
from schemas.expense import Expense, ExpenseCreate
from schemas.income import Income, IncomeCreate
from schemas.investment import Investment, InvestmentCreate

class UserBase(BaseModel):
    name: str
    password: str
    budget_ceiling: Optional[int] = None

class UserCreate(UserBase):
    bills: List[BillCreate] = []
    expenses: List[ExpenseCreate] = []
    incomes: List[IncomeCreate] = []
    investments: List[InvestmentCreate] = []

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bills: List[Bill] = []
    expenses: List[Expense] = []
    incomes: List[Income] = []
    investments: List[Investment] = []
