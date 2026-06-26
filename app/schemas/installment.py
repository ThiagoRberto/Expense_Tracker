from pydantic import BaseModel


class InstallmentEntrySchema(BaseModel):
    installment_number: int
    month: int
    year: int
    amount: float


class ExpenseProjection(BaseModel):
    expense_id: int
    expense_name: str
    category: str
    total_value: float
    installments: int
    entries: list[InstallmentEntrySchema]


class InstallmentsResponse(BaseModel):
    projections: list[ExpenseProjection]
