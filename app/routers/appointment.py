from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.appointments import get_all_appointments
from app.schemas.appointment import AppointmentResponse

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.get("/", response_model=list[AppointmentResponse])
def list_appointments(db: Session = Depends(get_db)):
    return get_all_appointments(db)
