from fastapi import FastAPI

from app.routers import attendance, auth, detect_test, enroll, recognize

app = FastAPI(title='AI Attendance System')

app.include_router(auth.router)
app.include_router(detect_test.router)
app.include_router(enroll.router)
app.include_router(recognize.router)
app.include_router(attendance.router)


@app.get('/health')
def health():
    return {'status': 'ok'}
