from sqlalchemy import \
    Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(
        Integer, 
        primary_key=True, 
        index=True
    )
    name = Column(
        String(256),
        nullable=False
    )
    password = Column(
        String(256),
        nullable=False
    )
    incomes = relationship("Income",
        back_populates="user",
        uselist=True,
        cascade="all, delete-orphan"
    )
    bills = relationship("Income",
        back_populates="user",
        uselist=True,
        cascade="all, delete-orphan"
    )
    investments = relationship("Income",
        back_populates="user",
        uselist=True,
        cascade="all, delete-orphan"
    )
    expenses = relationship("Income",
        back_populates="user",
        uselist=True,
        cascade="all, delete-orphan"
    )
    