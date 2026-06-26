from sqlalchemy import Column, Integer, Float, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database.database import Base


class CategoryBudget(Base):
    __tablename__ = 'category_budgets'
    # um único teto por categoria para cada usuário
    __table_args__ = (
        UniqueConstraint("user_id", "category", name="uq_category_budget_user_category"),
    )
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    ceiling = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="category_budgets")
