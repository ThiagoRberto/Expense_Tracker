from pydantic import BaseModel, ConfigDict, Field

class IncomeBase(BaseModel):
    name: str
    income_value: float = Field(ge=0)

class IncomeCreate(IncomeBase):
    pass

class Income(IncomeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
