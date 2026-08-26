from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db

from app.api.policies import router as policies_router
from app.api.triage import router as triage_router
from app.api.allocation import router as allocation_router
from app.api.cdss import router as cdss_router

app = FastAPI(
    title="Healthcare System API",
    description="API for the Holistic Optimization System for Policy-Integrated Admission & Treatment Intelligence",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(policies_router)
app.include_router(triage_router)
app.include_router(allocation_router)
app.include_router(cdss_router)

@app.get("/health", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "Healthcare System API is running"}

@app.get("/api/v1/db/health", tags=["Health Check"])
def db_health_check(db: Session = Depends(get_db)):
    """Verifies database connectivity by executing a simple SELECT query."""
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Healthcare System API. Visit /docs for documentation."}
