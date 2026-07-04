from pydantic import BaseModel
from datetime import date as date_type
from typing import Optional

class HealthLogIn(BaseModel):
    date: date_type
    steps: Optional[int] = None

class HealthLogOut(HealthLogIn):
    id: int
    class Config:
        from_attributes = True
