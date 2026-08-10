from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
import numpy as np
import cv2

from app.database import Embedding, Employee, get_db
from app.face_engine import detect_and_embed

router = APIRouter()

SIMILARITY_THRESHOLD = 0.5


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


@router.post("/recognize")
async def recognize(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = detect_and_embed(image_bgr)

    if len(results) == 0:
        raise HTTPException(status_code=400, detail="No face detected in the photo.")
    if len(results) > 1:
        raise HTTPException(status_code=400, detail="Multiple faces detected. Please submit a photo with only one person.")

    query_embedding = results[0]["embedding"]

    all_embeddings = db.query(Embedding).all()

    best_match = None
    best_score = -1.0

    for emb in all_embeddings:
        score = cosine_similarity(query_embedding, emb.embedding_vector)
        if score > best_score:
            best_score = score
            best_match = emb

    if best_match is not None and best_score >= SIMILARITY_THRESHOLD:
        employee = db.query(Employee).filter(Employee.id == best_match.employee_id).first()
        return {
            "recognized": True,
            "employee_id": employee.id,
            "employee_code": employee.employee_code,
            "name": employee.name,
            "similarity": best_score,
        }
    else:
        return {
            "recognized": False,
            "best_similarity": best_score if best_score > -1 else None,
            "message": "No matching employee found.",
        }
