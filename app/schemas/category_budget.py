from pydantic import BaseModel, ConfigDict, Field


class CategoryBudgetBase(BaseModel):
    category: str
    ceiling: float = Field(gt=0)


class CategoryBudgetCreate(CategoryBudgetBase):
    pass


class CategoryBudget(CategoryBudgetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
