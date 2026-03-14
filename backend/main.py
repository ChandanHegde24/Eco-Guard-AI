import logging

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.alerting import dispatch_alert_if_needed
from core.config import settings
from core.logging_config import configure_logging
from data_layer.database import get_session, init_db
from data_layer.gee_client import fetch_satellite_images, ee_initialized
from data_layer.ai_layer.vegetation_index import analyze_environmental_change
from core.risk_scoring import assess_climate_risk
from data_layer.repository import get_recent_analysis_runs, save_analysis_run

configure_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="Eco-Guard AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "project": "Eco-Guard AI",
        "status": "running",
        "earth_engine": "connected" if ee_initialized else "not authenticated",
        "docs": "/docs",
    }

# Define the expected request payload
class RegionRequest(BaseModel):
    latitude: float
    longitude: float
    time_t1: str  # e.g., "2025-01-01"
    time_t2: str  # e.g., "2026-01-01"


@app.on_event("startup")
async def startup_event() -> None:
    init_db()
    logger.info("Backend started and database initialized")

@app.post("/api/v1/analyze-region")
async def analyze_region(request: RegionRequest):
    try:
        # 1. Fetch multi-temporal images (Data Layer)
        images = fetch_satellite_images(
            request.latitude, 
            request.longitude, 
            request.time_t1, 
            request.time_t2
        )
        
        # 2. Process through AI/Indexing (AI Layer)
        ndvi_change = analyze_environmental_change(images['t1'], images['t2'], index_type="NDVI")
        
        # 3. Calculate Risk Score (Output Layer)
        risk_report = assess_climate_risk(ndvi_change)

        location_data = {"lat": request.latitude, "lon": request.longitude}

        # 4. Persist run for auditing and pilot KPI tracking
        with get_session() as session:
            run = save_analysis_run(
                session,
                latitude=request.latitude,
                longitude=request.longitude,
                time_t1=request.time_t1,
                time_t2=request.time_t2,
                change_percentage=ndvi_change,
                risk_level=risk_report["risk_level"],
                recommended_action=risk_report["action"],
                alert_triggered=risk_report["trigger_alert"],
            )

        # 5. Dispatch notifications through configured channels
        alert_dispatched = dispatch_alert_if_needed(risk_report, location_data)
        
        return {
            "status": "success",
            "analysis_id": run.id,
            "coordinates": location_data,
            "change_percentage": ndvi_change,
            "risk_assessment": risk_report,
            "alert_dispatched": alert_dispatched,
        }

    except Exception as e:
        logger.exception("Error while analyzing region")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/analysis/recent")
async def recent_analyses(limit: int = 20):
    safe_limit = min(max(limit, 1), 100)
    with get_session() as session:
        runs = get_recent_analysis_runs(session, safe_limit)

    return [
        {
            "id": run.id,
            "latitude": run.latitude,
            "longitude": run.longitude,
            "time_t1": run.time_t1,
            "time_t2": run.time_t2,
            "change_percentage": run.change_percentage,
            "risk_level": run.risk_level,
            "recommended_action": run.recommended_action,
            "alert_triggered": run.alert_triggered,
            "created_at": run.created_at.isoformat(),
        }
        for run in runs
    ]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)