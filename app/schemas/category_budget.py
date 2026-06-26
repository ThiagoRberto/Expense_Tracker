from pydantic import BaseModel, ConfigDict


class CategoryBudgetBase(BaseModel):
    category: str
    ceiling: float


class CategoryBudgetCreate(CategoryBudgetBase):
    pass


class CategoryBudget(CategoryBudgetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
