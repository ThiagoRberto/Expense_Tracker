from typing import List, Optional
from pydantic import BaseModel

from schemas.bill import Bill, BillCreate
from schemas.expense import Expense, ExpenseCreate
from schemas.income import Income, IncomeCreate
from schemas.investment import Investment, InvestmentCreate

class User(BaseModel):
    id: int
    name: str
    password: str
    bills: Optional[Bill] = None
    expenses: Optional[Expense] = None
    incomes: Optional[Income] = None
    investments: Optional[Investment] = None

    class Config:
        from_atrributes = True

class UserCreate(User):
    name: str
    password: str
    bills: BillCreate
    expenses: ExpenseCreate
    incomes: IncomeCreate
    investments: InvestmentCreate
