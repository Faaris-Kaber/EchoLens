from sqlalchemy import Column, Integer, String, Text, JSON, TIMESTAMP, func
from backend.db import Base

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    mode = Column(String, nullable=False)
    results = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
