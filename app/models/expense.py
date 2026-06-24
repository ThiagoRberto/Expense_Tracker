from sqlalchemy import \
    Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(
            Integer, 
            primary_key=True, 
            index=True
        )
    title = Column(
        String(256),
        nullable=False
    )
    expense_value = Column(
        Float
    )
    installment = Column(
        Integer
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
    )
    user = relationship("User",
        back_populates="expense",
    )