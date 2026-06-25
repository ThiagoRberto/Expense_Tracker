from pydantic import BaseModel, ConfigDict

class InvestmentBase(BaseModel):
    name: str
    value_invested: float
    dividends: float = 0.0

class InvestmentCreate(InvestmentBase):
    pass

class Investment(InvestmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
