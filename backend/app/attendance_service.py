from datetime import date as date_type, datetime

from sqlalchemy.orm import Session

from app.database import Attendance


def mark_attendance(db: Session, employee_id: int, confidence_score: float, device_location: str = None):
    today = date_type.today()
    existing = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee_id, Attendance.date == today)
        .first()
    )

    if existing:
        return {'is_new': False, 'time': str(existing.time)}

    now = datetime.now()
    record = Attendance(
        employee_id=employee_id,
        date=today,
        time=now.time(),
        confidence_score=confidence_score,
        device_location=device_location,
        status='present',
    )
    db.add(record)
    db.commit()
    return {'is_new': True, 'time': str(record.time)}
