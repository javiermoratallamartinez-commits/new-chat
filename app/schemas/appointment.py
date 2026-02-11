from pydantic import BaseModel
from datetime import date, time, datetime
from uuid import UUID


class AppointmentResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    reason: str
    date: date
    time: time
    half_day: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True  # 👈 MUY IMPORTANTE con SQLAlchemy 2
