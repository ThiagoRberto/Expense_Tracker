from pydantic import BaseModel, ConfigDict, Field

class BillBase(BaseModel):
    name: str
    bill_value: float = Field(ge=0)

class BillCreate(BillBase):
    pass

class Bill(BillBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
