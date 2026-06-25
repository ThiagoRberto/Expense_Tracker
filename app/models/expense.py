from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    expense_value = Column(Float, nullable=False)
    installment = Column(Integer, nullable=False, default=1)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="expenses")
