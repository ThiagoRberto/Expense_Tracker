from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Income(Base):
    __tablename__ = 'incomes'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    income_value = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="incomes")
