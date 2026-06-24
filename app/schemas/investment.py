from pydantic import BaseModel

class Investment(BaseModel):
    id: int
    name: str
    value_invested: float
    dividends: float

    class Config:
        from_atrributes = True

class InvestmentCreate(Investment):
    name: str
    value_invested: float
    dividends: float