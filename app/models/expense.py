from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    category = Column(String(100), nullable=False, default="geral")
    expense_value = Column(Float, nullable=False)
    installment = Column(Integer, nullable=False, default=1)
    start_month = Column(Integer, nullable=False, default=lambda: datetime.now().month)
    start_year = Column(Integer, nullable=False, default=lambda: datetime.now().year)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="expenses")
