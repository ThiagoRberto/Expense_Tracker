from pydantic import BaseModel

class Bill(BaseModel):
    id: int
    name: str
    bill_value: float

    class Config:
        from_atrributes = True

class BillCreate(Bill):
    name: str
    bill_value: float