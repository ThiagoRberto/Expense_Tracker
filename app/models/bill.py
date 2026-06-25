from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base

class Bill(Base):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), nullable=False)
    bill_value = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="bills")
