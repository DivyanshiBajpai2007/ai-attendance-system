from fastapi import FastAPI

app = FastAPI(title="AI Attendance System")


@app.get("/health")
def health():
    return {"status": "ok"}
