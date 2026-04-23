from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import upload, charts

app = FastAPI(
    title="SmartSheet API",
    description="AI-powered spreadsheet analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost", "https://smartsheet-ui.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api")
app.include_router(charts.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
