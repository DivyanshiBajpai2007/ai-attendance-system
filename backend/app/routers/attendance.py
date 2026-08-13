from datetime import date as date_type

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import Attendance, Employee, get_db

router = APIRouter()


@router.get("/attendance/today")
def get_today_attendance(db: Session = Depends(get_db)):
    today = date_type.today()
    records = (
        db.query(Attendance, Employee)
        .join(Employee, Attendance.employee_id == Employee.id)
        .filter(Attendance.date == today)
        .all()
    )
    return [
        {
            "employee_code": emp.employee_code,
            "name": emp.name,
            "time": str(att.time),
            "confidence_score": att.confidence_score,
        }
        for att, emp in records
    ]
