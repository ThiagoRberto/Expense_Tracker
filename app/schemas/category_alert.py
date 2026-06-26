from typing import List
from pydantic import BaseModel
from services.financial_service import BudgetStatus


class CategoryAlertItem(BaseModel):
    category: str
    total: float
    ceiling: float
    status: BudgetStatus


class CategoryAlertsResponse(BaseModel):
    alerts: List[CategoryAlertItem]
