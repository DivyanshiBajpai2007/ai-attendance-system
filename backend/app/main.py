from fastapi import FastAPI

from app.routers import detect_test, enroll, recognize

app = FastAPI(title="AI Attendance System")

app.include_router(detect_test.router)
app.include_router(enroll.router)
app.include_router(recognize.router)


@app.get("/health")
def health():
    return {"status": "ok"}
