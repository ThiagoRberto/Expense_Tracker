from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base


class CategoryBudget(Base):
    __tablename__ = 'category_budgets'
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(100), nullable=False)
    ceiling = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="category_budgets")
