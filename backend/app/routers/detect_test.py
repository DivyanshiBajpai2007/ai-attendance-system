from fastapi import APIRouter, UploadFile, File
import numpy as np
import cv2

from app.face_engine import detect_and_embed

router = APIRouter()


@router.post("/detect-test")
async def detect_test(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = detect_and_embed(image_bgr)

    faces = []
    for r in results:
        faces.append({
            "bbox": r["bbox"],
            "det_score": r["det_score"],
            "embedding_preview": r["embedding"][:5].tolist(),
            "embedding_length": len(r["embedding"]),
        })

    return {"faces_detected": len(results), "faces": faces}
