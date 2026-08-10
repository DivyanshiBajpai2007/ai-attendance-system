from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
import numpy as np
import cv2

from app.database import Embedding, Employee, get_db
from app.face_engine import detect_and_embed

router = APIRouter()


@router.post("/enroll")
async def enroll(
    employee_code: str = Form(...),
    name: str = Form(...),
    department: str = Form(None),
    label: str = Form("default"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = detect_and_embed(image_bgr)

    if len(results) == 0:
        raise HTTPException(status_code=400, detail="No face detected in the photo. Please try again with a clearer photo.")
    if len(results) > 1:
        raise HTTPException(status_code=400, detail="Multiple faces detected. Please submit a photo with only one person.")

    embedding_vector = results[0]["embedding"].tolist()

    employee = db.query(Employee).filter(Employee.employee_code == employee_code).first()
    if employee is None:
        employee = Employee(employee_code=employee_code, name=name, department=department)
        db.add(employee)
        db.commit()
        db.refresh(employee)

    new_embedding = Embedding(employee_id=employee.id, embedding_vector=embedding_vector, label=label)
    db.add(new_embedding)
    db.commit()

    return {
        "message": "Enrolled successfully",
        "employee_id": employee.id,
        "employee_code": employee.employee_code,
        "name": employee.name,
        "embedding_id": new_embedding.id,
    }
