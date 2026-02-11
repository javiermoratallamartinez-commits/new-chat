from sqlalchemy import Enum
from app.model.appointment import AppointmentStatus

status = Column(
    Enum(AppointmentStatus, name="appointment_status"),
    nullable=False,
    default=AppointmentStatus.CONFIRMED
)
