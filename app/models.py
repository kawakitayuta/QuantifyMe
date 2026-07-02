from sqlalchemy import Column, Integer, Float, Date
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class HealthLog(Base):
    __tablename__ = "health_log"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True, nullable=False)
    steps = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
