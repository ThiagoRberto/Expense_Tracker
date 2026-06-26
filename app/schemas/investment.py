from pydantic import BaseModel, ConfigDict, Field

class InvestmentBase(BaseModel):
    name: str
    value_invested: float = Field(ge=0)
    dividends: float = Field(default=0.0, ge=0)

class InvestmentCreate(InvestmentBase):
    pass

class Investment(InvestmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
