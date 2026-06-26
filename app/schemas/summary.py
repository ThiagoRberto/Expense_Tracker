from typing import Optional
from pydantic import BaseModel
from services.financial_service import BudgetStatus


class FinancialSummary(BaseModel):
    balance: float
    net_worth: float
    total_income: float
    total_spending: float
    budget_status: Optional[BudgetStatus] = None
