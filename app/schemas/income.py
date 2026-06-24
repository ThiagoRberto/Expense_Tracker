from pydantic import BaseModel

class Income(BaseModel):
    id: int
    name: str
    income_value: float

    class Config:
        from_atrributes = True

class IncomeCreate(Income):
    name: str
    income_value: float