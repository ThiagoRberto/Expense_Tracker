from pydantic import BaseModel


class MonthlyInvoiceItem(BaseModel):
    month: int
    year: int
    total: float


class MonthlyInvoicesResponse(BaseModel):
    months_ahead: int
    invoices: list[MonthlyInvoiceItem]
