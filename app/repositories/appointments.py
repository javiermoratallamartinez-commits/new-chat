from sqlalchemy.orm import Session
from app.models import Appointment


def get_all_appointments(db: Session):
    return db.query(Appointment).order_by(Appointment.created_at.desc()).all()
