from sqlalchemy import \
    Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Investment(Base):
    __tablename__ = 'investments'
    id = Column(
            Integer, 
            primary_key=True, 
            index=True
        )
    title = Column(
        String(256),
        nullable=False
    )
    value_invested = Column(
        Float
    )
    dividends = Column(
        Float
    )
    # investment_type = Column(
    #     InvestMentType
    # )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
    )
    user = relationship("User",
        back_populates="investment",
    )