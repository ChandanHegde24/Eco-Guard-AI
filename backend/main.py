import logging
import asyncio
import time
from contextlib import asynccontextmanager
from datetime import date

import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.alerting import dispatch_alert_if_needed
from core.config import settings
from core.logging_config import configure_logging
from data_layer.database import get_session, get_db, init_db
from data_layer.gee_client import fetch_satellite_images, ee_initialized, get_image_thumbnail
from data_layer.ai_layer.vegetation_index import analyze_environmental_change
from core.risk_scoring import assess_composite_climate_risk
from data_layer.repository import get_recent_analysis_runs, save_analysis_run

configure_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


# Simple in-memory TTL cache for expensive remote analysis calls.
# Keyed by request coordinates and date range.
analysis_cache: dict[tuple[float, float, str, str], tuple[float, dict]] = {}


def _cache_key(lat: float, lon: float, time_t1: str, time_t2: str) -> tuple[float, float, str, str]:
    return (round(lat, 5), round(lon, 5), time_t1, time_t2)


def _get_cached_analysis(key: tuple[float, float, str, str]) -> dict | None:
    cached = analysis_cache.get(key)
    if not cached:
        return None

    cached_at, payload = cached
    if (time.time() - cached_at) > settings.ANALYSIS_CACHE_TTL_SECONDS:
        analysis_cache.pop(key, None)
        return None

    return payload


def _set_cached_analysis(key: tuple[float, float, str, str], payload: dict) -> None:
    analysis_cache[key] = (time.time(), payload)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    logger.info("Backend started and database initialized")
    yield


app = FastAPI(title="Eco-Guard AI Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request.complete",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    return response

@app.get("/")
async def root():
    return {
        "project": "Eco-Guard AI",
        "status": "running",
        "earth_engine": "connected" if ee_initialized else "not authenticated",
        "docs": "/docs",
    }


@app.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
    }


@app.get("/ready")
async def readiness(db: Session = Depends(get_db)):
    db_ready = True
    db_error = None

    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_ready = False
        db_error = str(exc)

    payload = {
        "status": "ready" if db_ready else "not_ready",
        "checks": {
            "database": "ok" if db_ready else "failed",
            "earth_engine": "ok" if ee_initialized else "not_authenticated",
        },
    }

    if db_error:
        payload["checks"]["database_error"] = db_error

    if db_ready:
        return payload
    return JSONResponse(status_code=503, content=payload)

# Security and validation through Pydantic constraints
class RegionRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude between -180 and 180")
    time_t1: date = Field(..., description="Baseline analysis date") 
    time_t2: date = Field(..., description="Current analysis date")

    @model_validator(mode="after")
    def validate_date_order(self):
        if self.time_t2 < self.time_t1:
            raise ValueError("time_t2 must be greater than or equal to time_t1")
        return self

@app.post("/api/v1/analyze-region")
async def analyze_region(request: RegionRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    try:
        time_t1_str = request.time_t1.isoformat()
        time_t2_str = request.time_t2.isoformat()
        cache_key = _cache_key(request.latitude, request.longitude, time_t1_str, time_t2_str)

        cached_payload = _get_cached_analysis(cache_key)
        if cached_payload:
            return {
                "status": "success",
                "cached": True,
                **cached_payload,
            }

        # Execute blocking EE calls in a thread pool to avoid stalling the FastAPI event loop
        def run_gee_analysis():
            images = fetch_satellite_images(request.latitude, request.longitude, time_t1_str, time_t2_str)
            ndvi = analyze_environmental_change(images['t1'], images['t2'], index_type="NDVI")
            ndwi = analyze_environmental_change(images['t1'], images['t2'], index_type="NDWI")
            
            thumb_t1 = get_image_thumbnail(images['t1'], images['roi'])
            thumb_t2 = get_image_thumbnail(images['t2'], images['roi'])
            return ndvi, ndwi, thumb_t1, thumb_t2

        ndvi_change, ndwi_change, thumb_t1, thumb_t2 = await asyncio.to_thread(run_gee_analysis)
        
        # Calculate composite risk score using vegetation + water signals
        risk_report = assess_composite_climate_risk(ndvi_change, ndwi_change)
        location_data = {"lat": request.latitude, "lon": request.longitude}

        # Persist run via dependency injected session
        run = save_analysis_run(
            db,
            latitude=request.latitude,
            longitude=request.longitude,
            time_t1=time_t1_str,
            time_t2=time_t2_str,
            change_percentage=ndvi_change,
            risk_level=risk_report["risk_level"],
            recommended_action=risk_report["action"],
            alert_triggered=risk_report["trigger_alert"],
        )

        # Dispatch notifications asynchronously in background
        background_tasks.add_task(dispatch_alert_if_needed, risk_report, location_data)
        
        response_payload = {
            "status": "success",
            "analysis_id": run.id,
            "coordinates": location_data,
            "change_percentage": risk_report["composite_change_percentage"],
            "index_changes": {
                "ndvi_change_percentage": ndvi_change,
                "ndwi_change_percentage": ndwi_change,
            },
            "risk_assessment": risk_report,
            "thumbnails": {
                "t1": thumb_t1,
                "t2": thumb_t2
            },
            "alert_dispatched_in_background": risk_report["trigger_alert"],
            "cached": False,
        }

        # Cache everything except the status/cached wrapper metadata.
        _set_cached_analysis(
            cache_key,
            {
                "analysis_id": run.id,
                "coordinates": location_data,
                "change_percentage": risk_report["composite_change_percentage"],
                "index_changes": {
                    "ndvi_change_percentage": ndvi_change,
                    "ndwi_change_percentage": ndwi_change,
                },
                "risk_assessment": risk_report,
                "thumbnails": {
                    "t1": thumb_t1,
                    "t2": thumb_t2,
                },
                "alert_dispatched_in_background": risk_report["trigger_alert"],
            },
        )

        return response_payload

    except Exception as e:
        logger.exception("Error while analyzing region")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analysis/recent")
async def recent_analyses(limit: int = 20, db: Session = Depends(get_db)):
    safe_limit = min(max(limit, 1), 100)
    runs = get_recent_analysis_runs(db, safe_limit)

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