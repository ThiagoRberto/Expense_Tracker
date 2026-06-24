from sqlalchemy import \
    Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Income(Base):
    __tablename__ = 'incomes'
    id = Column(
            Integer, 
            primary_key=True, 
            index=True
        )
    title = Column(
        String(256),
        nullable=False
    )
    income_value = Column(
        Float
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
    )
    user = relationship("User",
        back_populates="income",
    )