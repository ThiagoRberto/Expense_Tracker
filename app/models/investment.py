from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Investment(Base):
    __tablename__ = 'investments'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    value_invested = Column(Float, nullable=False)
    dividends = Column(Float, nullable=False, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="investments")
