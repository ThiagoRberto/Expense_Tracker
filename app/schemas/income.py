from pydantic import BaseModel, ConfigDict

class IncomeBase(BaseModel):
    name: str
    income_value: float

class IncomeCreate(IncomeBase):
    pass

class Income(IncomeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
