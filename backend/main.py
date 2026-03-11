from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from data_layer.gee_client import fetch_satellite_images
from data_layer.ai_layer.vegetation_index import analyze_environmental_change
from core.risk_scoring import assess_climate_risk, process_alerts

app = FastAPI(title="Eco-Guard AI Backend")

# Define the expected request payload
class RegionRequest(BaseModel):
    latitude: float
    longitude: float
    time_t1: str  # e.g., "2025-01-01"
    time_t2: str  # e.g., "2026-01-01"

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
        
        # 4. Trigger Notifications if Risk is High
        location_data = {"lat": request.latitude, "lon": request.longitude}
        process_alerts(risk_report, location_data)
        
        return {
            "status": "success",
            "coordinates": location_data,
            "change_percentage": ndvi_change,
            "risk_assessment": risk_report 
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))