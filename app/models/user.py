from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)
    budget_ceiling = Column(Integer, nullable=True)

    incomes = relationship("Income", back_populates="user", uselist=True, cascade="all, delete-orphan")
    bills = relationship("Bill", back_populates="user", uselist=True, cascade="all, delete-orphan")
    investments = relationship("Investment", back_populates="user", uselist=True, cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", uselist=True, cascade="all, delete-orphan")
