from pydantic import BaseModel, ConfigDict

class BillBase(BaseModel):
    name: str
    bill_value: float

class BillCreate(BillBase):
    pass

class Bill(BillBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
