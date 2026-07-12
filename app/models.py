from sqlalchemy import Column, Integer, Date, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class HealthLog(Base):
    __tablename__ = "health_log"
    __table_args__ = (
        UniqueConstraint("date", "user_name", name="ix_health_log_date_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True, nullable=False)
    user_name = Column(String, nullable=False, default="yuta")
    steps = Column(Integer, nullable=True)
