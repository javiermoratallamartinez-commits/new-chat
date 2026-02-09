# app/models.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, Time, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    reason = Column(String, nullable=False)

    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    half_day = Column(String, nullable=False)

    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)
